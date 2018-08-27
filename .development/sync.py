import os, shutil, sys, fnmatch, glob, pyboard_util

def sync(args, patterns, resources, verbose, skip_wifi):
    root = get_root(verbose)

    # Add all paths that are already files
    paths = set([p for p in (patterns or []) if os.path.isfile(os.path.join(root, p))])

    # Always copy boot.py
    paths.add("boot.py")

    # wifi.json
    if not skip_wifi:
        wifi_path = os.path.join(root, "wifi.json")
        if os.path.isfile(wifi_path):
            paths.add(wifi_path)

    if not patterns:
        patterns = ["*"]

    synced_resources = []
    for pattern in patterns:
        found = False
        for key, resource in resources.items():
            if fnmatch.fnmatch(key, pattern):
                found = True
                synced_resources.append(key)
                if verbose:
                    print("Resource %s is going to be synced" % key)
                for path in resource['files'].keys():
                    paths.add(path)
        if not found and (pattern not in paths):
            print("WARN: No resources to copy found for pattern %s" % patterns)
    pyboard_util.init_copy_via_repl(args)
    if not verbose:
        print("Copying %s files: " % len(paths), end="", flush=True)
    for path in paths:
        if not path:
            continue
        rel_path = os.path.relpath(path, root)
        if rel_path.startswith(".") or os.path.isdir(path) or os.path.islink(path):
            continue

        updated = pyboard_util.copy_via_repl(args, path, rel_path)
        if verbose:
            print("Copied %s, updated: %s" % (rel_path, updated))
        else:
            if updated:
                print("+", end="", flush=True)
            else:
                print("=", end="", flush=True)
    pyboard_util.end_copy_via_repl(args)

    if verbose:
        print("Files copied successfully")
    else:
        print(" DONE")
    return synced_resources

def clean(args):
    print("Cleaning:", end=" ", flush=True)
    pyboard_util.clean_via_repl(args)
    print("DONE")

def set_boot_app(args, app_to_boot):
    content = app_to_boot + "\n"
    pyboard_util.write_via_repl(args, content.encode("utf8"), 'once.txt')
    if app_to_boot:
        print("setting next boot to %s" % app_to_boot)

def set_no_boot(args):
    pyboard_util.write_via_repl(args, b"\n", 'no_boot')

def get_root(verbose=False):
    root = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    if not os.path.isfile(os.path.join(root, "boot.py")):
        print("Path %s doesn't contain a boot.py, aborting. Something is probably wrong with your setup.")
        sys.exit(1)
    return root
