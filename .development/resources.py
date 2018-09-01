import os, hashlib, binascii
from metadata_reader import read_metadata, ParseException

"""
Resources are the basic components of any given library.

supported the following types:
* lib (files in lib/)
* shared (file in shared/)
* app (all other folders in root)
* root (files in root)

A resource has the following form:
{
    "app1": {"type": "app", dependencies: ["lib/lib1.py"], "files": {"app1/main.py": "abcdef1234", "app1/nested/text.txt": "abcdef1234"}},
    "app2": {"type": "app", dependencies: ["lib/lib2.py"], "files": {"app2/main.py": "abcdef1234", "app2/other_content.txt": "abcdef1234", "app2/some_binary_file.gif": "abcdef1234"}},
    "lib/lib1.py": {"type": "lib", , dependencies: ["lib/lib3.py"], "files": {"lib/lib1.py": "abcdef1234"}},
    "lib/lib2.py": {"type": "lib", "files": {"lib/lib2.py": "abcdef1234"}},
    "lib/lib3.py": {"type": "lib", "files": {"lib/lib3.py": "abcdef1234"}},
    "lib/lib4.py": {"type": "lib", "files": {"lib/lib4.py": "abcdef1234"}},
    "lib/lib5.py": {"type": "lib", "files": {"lib/lib5.py": "abcdef1234"}},
    "shared/foo.txt": {"type": "shared", "files": {"shared/foo.txt": "abcdef1234"}},
    "boot.py": {"type": "root", "files": {"boot.py": "abcdef1234"}}
}

Every resource can also contain other metadata fields which are extracted from the body
of its main python class (in case of lib or app).

This module has the following operations:
resources = get_resources(path) # Gets resources for a given path
add_hashes(path, resources)     # Adds hashes to the file dict - not needed for testing
add_metadata(path, resources)   # Adds metadata
validate(resources)             # Runs basic validation
resolve_dependencies(resources) # Merges all dependencies into each resource's file dict
remove_upip(resources)          # Remove upip resources from dict again

This module encapsulates all the main operations the app library is expect to
perform on a given checkout. It's intentionally kept in one file to make it easier
to share between repositories. The only exception to this rule it metadata_reader
(because it's rather complex and I didn't want to make this file impossible to read)

Please make sure this file can be executes on any operating system running python3.
Don't include any external dependencies. It forms part of the local toolchain.
"""

"""
scan(path)

A resource scanner for the Tilda filesystem. Returns a {path: {type:<type>, files:{...}}}

ignored are the following:
* dotfiles
* __pycache__
"""

def _scan_files(path, rel_path = ""):
    result = []
    for element in os.listdir(path):
        if element.startswith(".") or element == "__pycache__":
            continue
        element_path = os.path.join(path, element)
        element_rel_path = os.path.join(rel_path, element)
        if os.path.isdir(element_path):
            result.extend(_scan_files(element_path, element_rel_path))
        else:
            result.append(element_rel_path)

    return result

def get_resources(path):
    result = {}
    for sub_path in os.listdir(path):
        if sub_path.startswith(".") or sub_path == "__pycache__":
            continue
        full_path = os.path.join(path, sub_path)
        if os.path.islink(full_path):
            continue
        if os.path.isfile(full_path):
            result[sub_path] = {"type": "root", "files": {sub_path: None}}
            continue
        if sub_path in ["lib", "shared"]:
            files = _scan_files(full_path, sub_path)
            for rel_path in files:
                result[rel_path] = {"type": sub_path, "files": {rel_path: None}}
        elif sub_path == "upip":
            for upip_lib in os.listdir(full_path):
                if upip_lib.startswith(".") or upip_lib == "__pycache__":
                    continue
                full_lib_path = os.path.join(full_path, upip_lib)
                rel_lib_path = os.path.join(sub_path, upip_lib)
                files = {}
                if os.path.isfile(full_lib_path):
                    files = {rel_lib_path: None}
                    upip_lib = upip_lib.rsplit('.', 1)[0]
                else:
                    for rel_path in _scan_files(full_lib_path, os.path.join(sub_path, upip_lib)):
                        files[rel_path] = None
                result["upip:%s" % upip_lib] = {"type": sub_path, "files": files}
        else:
            files = _scan_files(full_path, sub_path)
            result[sub_path] = {"type": "app", "files": {}}
            for rel_path in files:
                result[sub_path]["files"][rel_path] = None
    return result

"""
add_hashes(path, resource)

Adds the first 10 characters of SHA256 hashes to all elements in "files".
The hash is calcuated on the file content, not the file name.
"""

def add_hashes(path, resources):
    for resource in resources.values():
        for file_path in resource["files"]:
            resource["files"][file_path] = _hash_file(os.path.join(path, file_path))

def _hash_file(filename):
    """Calculates the SHA256 hash of a file."""
    with open(filename, "rb") as file:
        sha256 = hashlib.sha256()
        buf = file.read(128)
        while len(buf) > 0:
            sha256.update(buf)
            buf = file.read(128)
        return str(binascii.hexlify(sha256.digest()), "utf8")[:10]

"""
add_metadata(path, resource)

Reads primary files for app and lib resources and extracts metadata information from its header
"""

def add_metadata(path, resources):
    for resource in resources.values():
        file = None
        if resource['type'] == "app":
            file = next(f for f in resource['files'] if os.path.basename(f) == "main.py")
        elif resource['type'] == "lib":
            file = next(iter(resource['files'].keys()))

        if file:
            try:
                with open(os.path.join(path, file), "r", encoding='utf8') as stream:
                    resource.update(_normalize_metadata(read_metadata(stream)))
            except ParseException as e:
                resource.setdefault("errors", []).append(file + ": " + str(e))

def _normalize_metadata(metadata):
    metadata['description'] = metadata.pop('doc')
    if 'dependencies' in metadata:
        metadata['dependencies'] = [normalize_dependency(l) for l in metadata.pop('dependencies')]

    return metadata

"""
resolve_dependencies(resources)

merges files from dependent resources into the original files dict
"""

def resolve_dependencies(resources):
    for file, resource in resources.items():
        if 'dependencies' in resource:
            already_added = [file]
            to_add = resource['dependencies'].copy()
            while len(to_add):
                r = to_add.pop()
                r = os.path.normpath(r)
                if r in already_added:
                    continue
                if r not in resources:
                    resource.setdefault("errors", []).append("Dependency %s not found" % r)
                    continue
                already_added.append(r)
                to_add.extend(resources[r].get("dependencies", []))
                resource['files'].update(resources[r]['files'])


"""
validate(path, resources)

does basic verification:
* Is it valid python?
* Are metadata fields missing
* TBD: Does it have imports that are not dependencies?
"""
def validate(path, resources):
    for resource in resources.values():
        if resource['type'] == "upip":
            continue
        _validate_resource(path, resource)

def _validate_resource(path, resource):
    # Compile
    for file in resource['files'].keys():
        if file.endswith(".py"):
            try:
                filename = os.path.join(path, file)
                with open(filename, 'r', encoding='utf8') as s:
                    compile(s.read() + '\n', filename, 'exec')
            except Exception as e:
                resource.setdefault("errors", []).append(str(e))

    # Metadata check
    if resource['type'] in ["app", "lib"]:
        pass #todo: should we make license required?

    if resource['type'] == "app":
        if 'categories' not in resource or (not isinstance(resource['categories'], list)) or len(resource['categories']) == 0:
            resource.setdefault("errors", []).append("___categories___ list is required in main.py but not found")


"""
remove_upip(resources)

upip adds over a 100 resources to the list. Some of them have broken validation as well, so it's
useful to remove them after resolving dependencies.
"""
def remove_upip(resources):
    to_delete = []
    for key, resource in resources.items():
        if resource['type'] == "upip":
            to_delete.append(key)
    for key in to_delete:
        del resources[key]

"""
helpers
"""

def get_error_summary(resources):
    summary = ""
    for key, resource in resources.items():
        if "errors" in resource:
            summary += "--- %s ---\n" % key
            for error in resource['errors']:
                summary += error + "\n"
            summary += "\n"
    return summary.strip()

def pretty_print_resources(resources):
    import json
    return json.dumps(resources, indent=4)

def normalize_dependency(dependency):
    """lib dependencies can be shortened to just their module name"""
    if "." in dependency or os.pathsep in dependency or "upip:" in dependency:
        return dependency
    return os.path.join("lib", "%s.py" % dependency)
