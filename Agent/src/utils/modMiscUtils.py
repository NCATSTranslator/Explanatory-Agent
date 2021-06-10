

def findObjectType(object):
    return str(type(object)).split("'")[1].split(".")[-1]
