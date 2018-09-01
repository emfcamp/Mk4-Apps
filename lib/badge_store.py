"""Library to interact with the badge store"""

___license___      = "MIT"
___dependencies___ = ["http", "ospath"]

from ospath import *
from http import *
import hashlib, binascii

class BadgeStore:
    def __init__(self, url = "http://badgeserver.emfcamp.org/2018", repo="emfcamp/Mk4-Apps", ref="master"):
        self.url = url
        self.repo = repo
        self.ref = ref
        self._apps = None

    def get_all_apps(self):
        if not self._apps:
            self._apps = self._call("apps")
        return self._apps

    def get_apps(self, category):
        return self.get_all_apps()[category]

    def get_categories(self):
        return self.get_all_apps().keys()

    def get_app(self, app):
        return self._call("app", {"app": app})

    def get_prs(self):
        return self._call("prs")

    def install(self, apps):
        return self._create_installers(self._call("install", {"apps": ",".join(apps)}))

    def bootstrap(self):
        return self._create_installers(self._call("bootstrap"))

    def _call(self, command, params = {}):
        params["repo"] = self.repo
        params["ref"] = self.ref
        with get("%s/%s" % (self.url, command), params=params).raise_for_status() as response:
            return response.json() # todo: error handling

    def _create_installers(self, files):
        installers = []
        url = "%s/download" % (self.url)
        for path, hash in files.items():
            if hash == get_hash(path):
                continue
            params = {"repo": self.repo, "ref": self.ref, "path": path}
            installers.append(Installer(path, url, params, hash))
        return installers

    def _is_file_up_to_date(self, path, hash):
        return hash == _get_hash(path)

TEMP_FILE = ".tmp.download"

class Installer:
    def __init__(self, path, url, params, hash):
        self.path = path
        self.url = url
        self.params = params
        self.hash = hash

    def download(self):
        count = 0
        while get_hash(TEMP_FILE) != self.hash:
            count += 1
            if count > 5:
                try:
                    os.remove(TEMP_FILE)
                except:
                    pass
                raise OSError("Aborting download of %s after 5 unsuccessful attempts" % self.path)
            try:
                get(self.url, params=self.params).raise_for_status().download_to(TEMP_FILE)
            except OSError as e:
                if "404" in str(e):
                    raise e
                pass
        try:
            os.remove(self.path)
        except OSError:
            pass
        makedirs(dirname(self.path))

        os.rename(TEMP_FILE, self.path)

def get_hash(path):
    if not isfile(path):
        return None

    with open(path, "rb") as file:
        sha256 = hashlib.sha256()
        buf = file.read(128)
        while len(buf) > 0:
            sha256.update(buf)
            buf = file.read(128)
        return str(binascii.hexlify(sha256.digest()), "utf8")[:10]

