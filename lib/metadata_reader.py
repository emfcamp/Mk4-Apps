""" Consumes a stream and returns a dict

However, the dict won't contain "__doc__", "___version___" etc, but
the shortened versions without underscores: "doc", "version".

Currently not supported:
* Dicts
* Floating points
* ints in list
* Strings in any other format then "x" or 'y'
* Docstrings with any other delimiter other than triple-" or triple='
* Comments

Feel free to expand if necessary
"""

class ParseException(Exception):
    """Indicates a parsing exception"""
    def __init__(self, message = ""):
        super().__init__(message)

def read_metadata(s):
    result = {}

    result["doc"] = _read_docstring(s)

    while True:
        key = _read_key(s)
        if key:
            result[key] = _read_value(s)
        else:
            break

    return result

def _read_docstring(s):
    delimiter = _read_non_whitespace(s, 3)
    if delimiter not in ["'''", '"""']:
        raise ParseException("Docstring delimiter expected")
    result = _read(s, 3);
    while result[-3:] != delimiter:
        result += _read(s)
    return result[:-3]

def _read_value(s):
    char = _read_non_whitespace(s)
    return _read_value_given_first_char(s, char)


def _read_value_given_first_char(s, first_char):
    if first_char in ["'", '"']:
        return _read_string(s, first_char)
    if first_char in "0123456789":
        return _read_int(s, first_char)
    if first_char in "TF":
        return _read_bool(s, first_char)
    if first_char == "[":
        return _read_list(s)
    raise ParseException("Invalid character %s found" % first_char)

def _read_string(s, delimiter):
    result = _read(s)
    try:
        while result[-1:] != delimiter:
            result += _read(s)
    except ParseException:
        raise ParseException("Invalid string or not terminated: %s" % result)
    return result[:-1]

def _read_int(s, char):
    result = char
    while not char.isspace():
        char = s.read(1)
        if not char:
            break
        result += char
        if not char in "0123456789":
            raise ParseException("Invalid int: %s" % result)
    return int(result)

def _read_bool(s, char):
    if char == "T":
        _assert(char + _read(s, 3), "True", "Invalid boolean")
        return True
    else:
        _assert(char + _read(s, 4), "False", "Invalid boolean")
        return False

def _read_list(s):
    result = []
    while True:
        char = _read_non_whitespace(s)
        if char == "]":
            break
        if result:
            if char != ",":
                raise ParseException("Expected comma, got '%s'" % char)
            result.append(_read_value(s))
        else:
            result.append(_read_value_given_first_char(s, char))

    return result

def _read_key(s):
    delimiter = _read_non_whitespace(s, 3)
    if delimiter != "___":
        return None
    try:
        result = _read(s, 3);
        while result[-3:] != delimiter:
            char = _read(s)
            if char in [" ", "="]:
                raise ParseException()
            result += char
    except ParseException:
        raise ParseException("Invalid key: ___%s" % result)
    _assert(_read_non_whitespace(s), "=", "Expected equals")
    return result[:-3]

def _read(s, l=1):
    result = s.read(l)
    if len(result)<l:
        raise ParseException("Expected to read at least %s characters, got '%s'" % (l, result))
    return result

def _assert(input, expected, message):
    if not input == expected:
        raise ParseException(message + " ('%s' expected, '%s' found)" % (expected, input))

def _read_non_whitespace(s, l=1):
    result = s.read(1)
    while result.isspace():
        result = s.read(1)
    if l == 1:
        return result
    else:
        return result + s.read(l - 1)

