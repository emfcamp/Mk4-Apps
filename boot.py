import os, tilda

os.sync()
root = os.listdir()

def app(a):
    if (a in root) and ("main.py" in os.listdir(a)):
        return a + "/main.py"

def file(file, remove):
    try:
        a = None
        with open(file, 'r') as f:
            a = f.read().strip()
        if remove:
            os.remove(file)
        return app(a)
    except Exception as e:
        print(str(e))

def any_home():
    h = [a for a in root if a.startswith("home")]
    return h[0] if len(h) else False

if "no_boot" in root:
    start = None
    if "main.py" in root:
        start = "main.py"
    start = file("once.txt", True) or file("default_app.txt", False) or any_home() or "bootstrap.py"
    print("Booting into %s" % start)
    tilda.main(start)
