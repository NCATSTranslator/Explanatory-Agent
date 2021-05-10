"""
WHAT: Miscellaneous utilities for text or strings
WHY: Need a common place for functions to be shared
ASSUMES: Manipulates only text or strings
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-05
"""


def isNullOrWhiteSpace(text):
    """
    Checks whether a supplied string is None or contains only white space
    :param text: A string to be tested
    :return: Boolean, True if it is null or all white space, False if it is not null and not all white space
    """
    if text is None or str(text).strip() == "":
        return True
    return False


def resolveDefaultValue(value, default):
    """
    Resolves default if the text is null or white space
    :param value: any value with possible null or whitespcae
    :param default: default value to return
    :return: value or default
    """
    if isNullOrWhiteSpace(value):
        return default
    return value