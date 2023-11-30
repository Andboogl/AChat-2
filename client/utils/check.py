"""Miscellaneous Checks Module"""


def check_for_empty(string):
    """Returns True if the string is a put. Otherwise, False."""
    return True if not string.strip() else False


def is_int(value):
    """Check for a number"""
    try:
        int(value)
        return True

    except (TypeError, ValueError):
        return False
