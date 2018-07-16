"""A simple key/value store backed by a json file

Keys need to be convertable to str
Values can be anything json can store, including a dict

Usage:

import database
with database.open() as db:
    print(db.get("hello", "default"))
    db.set("foo", "world")
    db.delete("bar")

Or, to make things even easier, there are three static function:

import database
print(database.get("hello", "default"))
database.set("foo", "world")
database.delete("bar")
"""

___license___ = "MIT"

import os, json

class Database:
    def __init__(self, filename = "config.json"):
        self.filename = filename
        self.dirty = False
        try:
            with open(filename, "rt") as file:
                self.data = json.loads(file.read())
        except (OSError, ValueError):
            print("Database %s doesn't exists or is invalid, creating new" % (filename))
            self.data = {}
            self.dirty = True
            self.flush()

    def set(self, key, value):
        """Sets a value for a given key.

        'key' gets converted into a string
        'value' can be anything that json can store, including a dict
        """
        self.data[key] = value
        self.dirty = True

    def get(self, key, default_value = None):
        """Returns the value for a given key.

        If key is not found 'default_value' will be returned
        """
        return self.data[key] if key in self.data else default_value

    def delete(self, key):
        """Deletes a key/value pair"""
        if key in self.data:
            del self.data[key]
            self.dirty = True


    def flush(self):
        """Writes changes to flash"""
        if self.dirty:
            with open(self.filename, "wt") as file:
                file.write(json.dumps(self.data))
                file.flush()
            os.sync()
            self.dirty = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()


def get(key, default_value = None, *args, **kwargs):
    with Database(*args, **kwargs) as db:
        return db.get(key, default_value)

def set(key, value, *args, **kwargs):
    with Database(*args, **kwargs) as db:
        return db.set(key, value)

def delete(key, *args, **kwargs):
    with Database(*args, **kwargs) as db:
        return db.delete(key)
