# This is meant to run on the badge
import hashlib, binascii, os

def split(path):
    if path == "":
        return ("", "")
    r = path.rsplit("/", 1)
    if len(r) == 1:
        return ("", path)
    head = r[0]
    if not head:
        head = "/"
    return (head, r[1])

def dirname(path):
    return split(path)[0]

def exists(path):
    try:
        os.stat(path)[0]
        return True
    except OSError:
        return False

def makedirs(path):
    sub_path = split(path)[0]
    if sub_path and (not exists(sub_path)):
        makedirs(sub_path)
    if not exists(path):
        os.mkdir(path)

def isdir(path):
    try:
        return os.stat(path)[0] & 0o170000 == 0o040000
    except OSError:
        return False

def h(p):
    try:
        with open(p, "rb") as f:
            h = hashlib.sha256()
            h.update(f.read())
            print(str(binascii.hexlify(h.digest()), "utf8")[:10])
            return
    except:
        pass
    print("nooooooooo")

def w(p, c):
    try:
        print("file", p)
        makedirs(dirname(p))
        with open(p, "wb") as f:
            f.write(binascii.a2b_base64(c))
        os.sync()
        print("OK")
    except Exception as e:
        import sys
        print("Error while writing file %s" % p)
        sys.print_exception(e)
        pass

def clean(path=""):
    for s in os.listdir(path):
        full = "/".join([path, s]) if path else s
        try:
            if isdir(full):
                try:
                    clean(full)
                except:
                    pass
                os.rmdir(full)
            else:
                os.remove(full)
        except Exception as e:
            print("Error while trying to clean '%s'" % full)

try:
    os.remove("bootstrap.py")
except:
    pass
