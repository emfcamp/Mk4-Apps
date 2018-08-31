import os, tilda
from machine import Neopix

n=Neopix()
n.display([0,0,0])
n.display([0,0,0])

print("EMF: boot.py")
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
        print("Not found: %s" % file)

def any_home():
    h = [a for a in root if a.startswith("home")]
    return h[0] if len(h) else False

if "no_boot" in root:
    print("no_boot found, aborting boot sequence")
elif "bootstrap.py" in root:
    print("Bootstrapping...")
    tilda.main("bootstrap.py")
else:
    start = None
    if "main.py" in root:
        start = "main.py"
    start = start or file("once.txt", True) or file("default_app.txt", False) or any_home()
    if ".py" not in start:
        start += "/main.py"
    print("Booting into %s" % start)
    tilda.main(start)

