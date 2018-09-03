"""Library to generate random numbers

Warning! Don't use this for anything important, it's probably biased
"""

___license___ = "MIT"

try:
    import urandom as sysrand
except ImportError:
    import random as sysrand

def random():
    """Return the next random floating point number in the range [0.0, 1.0)."""
    return sysrand.random()

def randrange(start, stop=None):
    """Return a randomly selected element from range(start, stop)"""
    if stop is None:
        stop = start
        start = 0
    return sysrand.randrange(start, stop)

def randint(start, stop):
    """Return a random integer N such that a <= N <= b."""
    return sysrand.randint(start, stop)

def shuffle(seq):
    """Shuffle the sequence x in place."""
    l = len(seq)
    for i in range(l):
        j = randrange(l)
        seq[i], seq[j] = seq[j], seq[i]
