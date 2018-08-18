"""Library to generate random numbers

Warning! Don't use this for anything important, it's probably biased
"""

___license___ = "MIT"

# todo: simplify this by using "urandom"
import os

_bigrand_bytes = 10
_bigrand_max = pow(256, _bigrand_bytes)

def _bigrand():
    """generates a random number between 0 (incl) and _bigrand_max (excl)"""
    base = 0
    for b in os.urandom(_bigrand_bytes):
        base = (base << 8) + b
    return base

def random():
    """Return the next random floating point number in the range [0.0, 1.0)."""
    return _bigrand() / _bigrand_max

def randrange(start, stop=None):
    """Return a randomly selected element from range(start, stop)"""
    if stop is None:
        stop = start
        start = 0
    return start + (_bigrand() * (stop - start) // _bigrand_max)

def randint(start, stop):
    """Return a random integer N such that a <= N <= b."""
    return randrange(start, stop + 1)

def shuffle(seq):
    """Shuffle the sequence x in place."""
    l = len(seq)
    for i in range(l):
        j = randrange(l)
        seq[i], seq[j] = seq[j], seq[i]
