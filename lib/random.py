"""Library to generate random numbers"""

___license___ = "MIT"

import os

# todo: write an actual useful function
def rand():
    return int(os.urandom(1)[0])
