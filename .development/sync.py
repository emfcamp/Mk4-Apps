import os, glob, shutil, sys

def sync(storage, patterns):
    root = get_root()

    # Add all paths that are already files
    paths = [os.path.join(root, p) for p in (patterns or []) if os.path.isfile(os.path.join(root, p))]

    if patterns:
        new_patterns = []
        patterns = [os.path.join(root, p, "**") for p in patterns]
    else:
        patterns = ["**/**", "boot.py"]

    for pattern in patterns:
        for path in glob.glob(pattern):
            paths.append(path)

    if len(paths) == 0:
        print("No files to copy found for pattern %s" % patterns)
        sys.exit(1)

    for path in paths:
        rel_path = os.path.relpath(path, root)
        if rel_path.startswith("."):
            continue
        print("Copying %s..." % rel_path)

        target = os.path.join(storage, rel_path)
        target_dir = os.path.dirname(target)
        if os.path.isfile(target_dir):
            # micropython has the tendency to sometimes corrupt directories into files
            os.remove(target_dir)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        shutil.copy2(path, target)

    else:
        print("Files copied successfully")


def set_boot_app(storage, app_to_boot):
    path = os.path.join(storage, 'once.txt')
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, 'w') as f:
        f.write(app_to_boot + "\n")
    print("setting next boot to %s" % app_to_boot)

def get_root():
    root = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    if not os.path.isfile(os.path.join(root, "boot.py")):
        print("Path %s doesn't contain a boot.py, aborting. Something is probably wrong with your setup.")
        sys.exit(1)
    return root
