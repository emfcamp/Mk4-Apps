"""Model and Helpers for TiLDA apps and the App Library API"""

___license___      = "MIT"
___dependencies___ = ["http"]

import os
import ure
import http_client
import filesystem
import gc

ATTRIBUTE_MATCHER = ure.compile("^\s*###\s*([^:]*?)\s*:\s*(.*)\s*$") # Yeah, regex!
CATEGORY_ALL = "all"
CATEGORY_NOT_SET = "uncategorised"

class App:
    """Models an app and provides some helper functions"""
    def __init__(self, folder_name, api_information = None):
        self.folder_name = self.name = folder_name.lower()
        self.user = EMF_USER
        if USER_NAME_SEPARATOR in folder_name:
            [self.user, self.name] = folder_name.split(USER_NAME_SEPARATOR, 1)
            self.user = self.user.lower()
            self.name = self.name.lower()

        self._attributes = None # Load lazily
        self.api_information = api_information

    @property
    def folder_path(self):
        return "apps/" + self.folder_name

    @property
    def main_path(self):
        return self.folder_path + "/main.py"

    @property
    def loadable(self):
        return filesystem.is_file(self.main_path) and os.stat(self.main_path)[6] > 0

    @property
    def description(self):
        """either returns a local attribute or uses api_information"""
        if self.api_information and "description" in self.api_information:
            return self.api_information["description"]
        return self.get_attribute("description") or ""

    @property
    def files(self):
        """returns a list of file dicts or returns False if the information is not available"""
        if self.api_information and "files" in self.api_information:
            return self.api_information["files"]
        return False

    @property
    def category(self):
        return self.get_attribute("Category", CATEGORY_NOT_SET).lower()

    @property
    def title(self):
        return self.get_attribute("appname") or self.name

    @property
    def user_and_title(self):
        if self.user == EMF_USER:
            return self.name
        else:
            return "%s by %s" % (self.title, self.user)

    def matches_category(self, category):
        """returns True if provided category matches the category of this app"""
        category = category.lower()
        return category == CATEGORY_ALL or category == self.category

    @property
    def attributes(self):
        """Returns all attribues of this app

        The result is cached for the lifetime of this object
        """
        if self._attributes == None:
            self._attributes = {}
            if self.loadable:
                with open(self.main_path) as file:
                    for line in file:
                        match = ATTRIBUTE_MATCHER.match(line)
                        if match:
                            self._attributes[match.group(1).strip().lower()] = match.group(2).strip()
                        else:
                            break
        return self._attributes

    def get_attribute(self, attribute, default=None):
        """Returns the value of an attribute, or a specific default value if attribute is not found"""
        attribute = attribute.lower() # attributes are case insensitive
        if attribute in self.attributes:
            return self.attributes[attribute]
        else:
            return default

    def fetch_api_information(self):
        """Queries the API for information about this app, returns False if app is not publicly listed"""
        with http_client.get("http://api.badge.emfcamp.org/api/app/%s/%s" % (self.user, self.name)) as response:
            if response.status == 404:
                return False
            self.api_information = response.raise_for_status().json()
        return self.api_information

    def __str__(self):
        return self.user_and_title

    def __repr__(self):
        return "<App %s>" % (self.folder_name)


def app_by_name_and_user(name, user):
    """Returns an user object"""
    if user.lower() == EMF_USER:
        return App(name)
    else:
        return App(user + USER_NAME_SEPARATOR + name)

def app_by_api_response(response):
    if response["user"].lower() == EMF_USER:
        return App(response["name"], response)
    else:
        return App(response["user"] + USER_NAME_SEPARATOR + response["name"], response)

def get_local_apps(category=CATEGORY_ALL):
    """Returns a list of apps that can be found in the apps folder"""
    apps = [App(folder_name) for folder_name in os.listdir("apps") if filesystem.is_dir("apps/" + folder_name)]
    return [app for app in apps if app.matches_category(category)]

_public_apps_cache = None
def fetch_public_app_api_information(uncached=False):
    """Returns a dict category => list of apps

    Uses cached version unless the uncached parameter is set
    """
    global _public_apps_cache
    if not _public_apps_cache or uncached:
        response = {}
        for category, apps in http_client.get("http://api.badge.emfcamp.org/api/apps").raise_for_status().json().items():
            response[category] = [app_by_api_response(app) for app in apps]

        _public_apps_cache = response
    return _public_apps_cache

def get_public_app_categories(uncached=False):
    """Returns a list of all categories used on the app library"""
    return list(fetch_public_app_api_information(uncached).keys())

def get_public_apps(category=CATEGORY_ALL, uncached=False):
    """Returns a list of all public apps in one category"""
    category = category.lower()
    api_information = fetch_public_app_api_information(uncached)
    return api_information[category] if category in api_information else []

_category_cache = None
def get_local_app_categories(uncached=False):
    """Returns a list of all app categories the user's apps are currently using

    Uses cached version unless the uncached parameter is set
    """
    global _category_cache
    if not _category_cache or uncached:
        _category_cache = ["all"]
        for app in get_local_apps():
            if app.category not in _category_cache:
                _category_cache.append(app.category)

    return _category_cache

def empty_local_app_cache():
    """If you're tight on memory you can clean up the local cache"""
    global _public_apps_cache, _category_cache
    _public_apps_cache = None
    _category_cache = None
        gc.collect()
