

def findObjectType(object):
    return str(type(object)).split("'")[1].split(".")[-1]


def isNullOrEmptyList(value):
    if value is None or value == []: return True
    return False
