"""
WHAT: Primary entry point to application
WHY: Need a primary entry point
ASSUMES: Invoked via "python modMain.py", either directly on an OS or via Docker
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-28
"""

import modConfig
import logging
from clsBertManager import clsBertManager


def main():
    """
    The primary entry point to execute the program
    :return: None
    """
    bertManager = clsBertManager()
    bertManager.execute()


if __name__ == '__main__':

    from datetime import datetime

    startTime = datetime.now()

    logging.basicConfig(
        filemode="a",
        filename=modConfig.logFilePath,
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)8s %(message)s')

    msg = "Program started"
    print(msg)
    logging.info(msg)

    try:
        main()
    except Exception as e:
        msg = "Exception running main method"
        print(msg)
        print(str(e))
        logging.error(msg)
        logging.error(e)
        raise

    msg = "Program complete"
    print(msg)
    logging.info(msg)

    endTime = datetime.now()
    totalTime = endTime - startTime
    msg = "App run time: %s" % str(totalTime)
    print(msg)
    logging.info(msg)

