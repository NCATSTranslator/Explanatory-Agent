from multiprocessing.dummy import Pool as ThreadPool
from .clsDelayedException import clsDelayedException
from ..modMiscUtils import findObjectType
import time
import logging


def printer(object, status: str):
    message = f"{findObjectType(object)} with dispatchId {object.dispatchId} {status}"
    if object.dispatchDescription is not None:
        message += f", description: {object.dispatchDescription}"
    return message


def runner(object):
    startTime = time.time()
    status = "Started"

    try:
        logging.debug(printer(object=object, status=status))
        object.execute()
        status = "Completed"

    except Exception as tb:
        status = "Failed"
        logging.error(str(tb))
        raise clsDelayedException(tb)

    finally:
        endTime = time.time()
        object.dispatchRunTimeSeconds = endTime - startTime
        message = printer(object=object, status=status)
        if status == "Completed":
            logging.debug(message)
        elif status == "Failed":
            logging.error(message)
        logging.debug(f"{findObjectType(object)} with dispatchId {object.dispatchId} took {object.dispatchRunTimeSeconds} seconds")
        

def dispatch(objects: list, method: str, parentId: int):

    if method.lower() == "serial":

        for object in objects:
            try:
                runner(object)
            except clsDelayedException as tb:
                tb.re_raise()

    elif method.lower() == "parallel":

        pool = ThreadPool(processes=len(objects))
        try:
            # imap_unordered returns the result as soon as they're available
            list(pool.imap_unordered(runner, objects))
        except clsDelayedException as tb:
            logging.error(f"Terminating thread pool of parent with id {parentId}")
            pool.close()
            pool.terminate()
            tb.re_raise()
        else:
            pool.close()
            pool.join()

    else:
        raise AttributeError("Only 'serial' or 'parallel' supported for dispatch method")
