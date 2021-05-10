import logging


def printAndLog(msg, level=logging.INFO):
    """
    Helper function to print and logging.info
    :param msg: Any message
    :return: None
    """
    print(msg)
    logging.log(level=level, msg=msg)
