""" A TiLDA optimized implementation of os.path

The one in upip requires a modified version of "os" that I don't want to include
"""

___dependencies___ = ["upip:stat"]

from stat import *
import os

sep = "/"

R_OK = const(4)
W_OK = const(2)
X_OK = const(1)
F_OK = const(0)

def join(*args):
    # TODO: this is non-compliant
    if type(args[0]) is bytes:
        return b"/".join(args)
    else:
        return sep.join(args)

def split(path):
    if path == "":
        return ("", "")
    r = path.rsplit(sep, 1)
    if len(r) == 1:
        return ("", path)
    head = r[0] #.rstrip(sep)
    if not head:
        head = sep
    return (head, r[1])

def dirname(path):
    return split(path)[0]

def basename(path):
    return split(path)[1]

def exists(path):
    try:
        os.stat(path)[0]
        return True
    except OSError:
        return False

def isdir(path):
    import stat
    try:
        mode = os.stat(path)[0]
        return stat.S_ISDIR(mode)
    except OSError:
        return False

def isfile(path):
    import stat
    try:
        mode = os.stat(path)[0]
        return stat.S_ISREG(mode)
    except OSError:
        return False
