"""Model and Helpers for local apps

This is useful for the launcher and other apps.
"""

___license___      = "MIT"
___dependencies___ = ["metadata_reader", "ospath"]

from ospath import *
import os, machine
from metadata_reader import read_metadata

class App:
    """Models an app and provides some helper functions"""
    def __init__(self, name):
        self.name = name
        self._attributes = None # Load lazily

    @property
    def folder_path(self):
        return self.name

    @property
    def main_path(self):
        return self.folder_path + "/main.py"

    @property
    def loadable(self):
        return isfile(self.main_path)

    @property
    def description(self):
        return self.get_attribute("doc")

    @property
    def title(self):
        return self.get_attribute("title", self.name)

    @property
    def categories(self):
        return self.get_attribute("categories")

    def matches_category(self, target):
        return target in self.categories

    @property
    def attributes(self):
        if self._attributes == None:
            try:
                with open(self.main_path) as file:
                    self._attributes = read_metadata(file)
            except OSError:
                raise Exception("File %s not found in on badge" % self.main_path)
        return self._attributes

    def get_attribute(self, attribute, default=None):
        if attribute in self.attributes:
            return self.attributes[attribute]
        return default

    def boot(self):
        write_launch_file(self.name)
        machine.reset()

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<App %s>" % (self.name)

    def __eq__(self, other):
        if isinstance(other, App):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)


_apps = None
def get_apps(category=None):
    global _apps
    if _apps == None:
        _apps = []
        for path in os.listdir():
            if path.startswith(".") or (not isdir(path)) or path in ["lib", "shared", "upip"]:
                continue
            app = App(path)
            if app.loadable:
                _apps.append(app)

    if category:
        return [app for app in _apps if app.matches_category(category)]
    return _apps

def uncache_apps():
    global _apps
    _apps = None

_categories = None
def get_categories():
    global _categories
    if _categories == None:
        _categories = set()
        for app in get_apps():
            _categories.update(app.categories)
    return _categories

def write_launch_file(app, file = "once.txt"):
    with open(file, "wt") as file:
        file.write(app)
        file.flush()
    os.sync()

def restart_to_default():
    write_launch_file("")
    machine.reset()

