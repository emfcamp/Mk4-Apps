import os, shutil, sys, fnmatch

def sync(storage, patterns, resources, verbose):
    root = get_root()

    # Add all paths that are already files
    paths = set([p for p in (patterns or []) if os.path.isfile(os.path.join(root, p))])

    # Always copy boot.py
    paths.add("boot.py")

    # wifi.json
    wifi_path = os.path.join(root, "wifi.json")
    if os.path.isfile(wifi_path):
        paths.add(wifi_path)

    if not patterns:
        patterns = ["*"]

    for pattern in patterns:
        found = False
        for key, resource in resources.items():
            if fnmatch.fnmatch(key, pattern):
                found = True
                if verbose:
                    print("Resource %s is going to be synced" % key)
                for path in resource['files'].keys():
                    paths.add(path)
        if not found:
            print("WARN: No resources to copy found for pattern %s" % patterns)

    if not verbose:
        print("Copying %s files: " % len(paths), end="")
    for path in paths:
        if not path:
            continue
        rel_path = os.path.relpath(path, root)
        if rel_path.startswith(".") or os.path.isdir(path) or os.path.islink(path):
            continue
        if verbose:
            print("Copying %s..." % rel_path)
        else:
            print(".", end="")

        target = os.path.join(storage, rel_path)
        target_dir = os.path.dirname(target)
        if os.path.isfile(target_dir):
            # micropython has the tendency to sometimes corrupt directories into files
            os.remove(target_dir)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        shutil.copy2(path, target)

    if verbose:
        print("Files copied successfully")
    else:
        print(" DONE")

def set_boot_app(storage, app_to_boot):
    path = os.path.join(storage, 'once.txt')
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, 'w') as f:
        f.write(app_to_boot + "\n")
    if app_to_boot:
        print("setting next boot to %s" % app_to_boot)

def get_root():
    root = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    if not os.path.isfile(os.path.join(root, "boot.py")):
        print("Path %s doesn't contain a boot.py, aborting. Something is probably wrong with your setup.")
        sys.exit(1)
    return root
