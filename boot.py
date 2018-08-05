import pyb, os, micropython, sys

micropython.alloc_emergency_exception_buf(100)

sys.path.append('/flash/upip')

os.sync()
root = os.listdir()

def app(a):
    if (a in root) and ("main.py" in os.listdir(a)):
        return a + "/main.py"

def file(file, remove):
    print(file)
    try:
        a = None
        with open(file, 'r') as f:
            a = f.read().strip()
        if remove:
            os.remove(file)
        return app(a)
    except Exception as e:
        print(e)

def any_home():
    return app(next(a for a in root if a.startswith("home")))

if "no_boot" in root:
    os.remove("no_boot")
else:
    start = None
    if "main.py" in root:
        start = "main.py"
    start = file("once.txt", True) or file("default_app.txt", False) or any_home() or "bootstrap.py"

    pyb.main(start)
