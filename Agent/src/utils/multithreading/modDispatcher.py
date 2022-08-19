from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing
from .clsDelayedException import clsDelayedException
from ..modMiscUtils import findObjectType
import time
import logging
from utils.clsLog import clsLogEvent
import traceback


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
        print(traceback.format_exc())
        logging.error(str(tb))
        object.logs.append(clsLogEvent(
            identifier=str(object.dispatchId),
            level="ERROR",
            code="",
            message=f"Unexpected error in object with dispatchId {object.dispatchId}: {tb}"
        ))
        # raise clsDelayedException(tb)

    finally:
        endTime = time.time()
        object.dispatchRunTimeSeconds = endTime - startTime
        message = printer(object=object, status=status)
        if status == "Completed":
            logging.debug(message)
        elif status == "Failed":
            logging.error(message)
        logging.debug(f"{findObjectType(object)} with dispatchId {object.dispatchId} took {object.dispatchRunTimeSeconds} seconds")

        return object
        

def dispatch(objects: list, method: str, parentId: int):
    # print("{} sleepin 5".format(parentId))
    # time.sleep(5)
    # print("{} done sleepin 5".format(parentId))
    # return parentId

    if method.lower() == "serial":

        for object in objects:
            try:
                runner(object)
            except clsDelayedException as tb:
                tb.re_raise()

    elif method.lower() == "parallel":
        # pool = ThreadPool(processes=len(objects))
        pool = ThreadPool(processes=5)
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
            # pool.wait(timeout=10)

    else:
        raise AttributeError("Only 'serial' or 'parallel' supported for dispatch method")


def test_runner(sleeptime):
    print("sleepin {}".format(sleeptime))
    import time
    time.sleep(sleeptime)
    print("done sleepin {}".format(sleeptime))
    return sleeptime


def test_runner_objectmanip(thing):
    print("sleepin {}".format(thing.sleeptime))
    import time
    time.sleep(thing.sleeptime)
    print("done sleepin {}".format(thing.sleeptime))
    thing.done = "yes"
    return thing


class thingClass:
    def __init__(self, sleeptime, done):
        self.sleeptime = sleeptime
        self.done = done


def query_dispatch(objects: list, method: str, parentId: int, abort_time: int, pool_size: int = 7):
    """
    Dispatches a worker for each Query Manager with a global timeout. Once the timeout is reached all working threads are stopped and any results are returned.
    :param objects:
    :param method:
    :param parentId:
    :param abort_time: time in epoch seconds when the threads should be aborted
    :param pool_size:
    :return:
    """

    if method.lower() == "serial":

        for object in objects:
            try:
                runner(object)
            except clsDelayedException as tb:
                tb.re_raise()

    elif method.lower() == "parallel":
        # pool = multiprocessing.Pool(processes=5)
        pool = ThreadPool(processes=pool_size)
        print("running pool")
        # list(pool.imap_unordered(runner, objects))
        imap_results = pool.imap_unordered(runner, objects)
        # imap_results = pool.imap_unordered(test_runner, [3, 2, 1, 12, 15, 16, 17, 18, 19, 20, 21])
        # imap_results = pool.imap_unordered(test_runner, [3, 2, 1])
        # imap_results = pool.imap_unordered(test_runner_objectmanip, [
        #     thingClass(1, "no"),
        #     thingClass(2, "no"),
        #     thingClass(3, "no"),
        #     thingClass(12, "nope"),
        # ])
        results = []
        pool.close()
        # pool.join()
        print("pool waiting")
        # start_time = time.time()
        # timeout_time = start_time + 10
        current_time = time.time()
        while current_time < abort_time:
            try:
                result = imap_results.next(timeout=1)
                results.append(result)
                print("Got result {}".format(result,))
            except StopIteration:
                print("StopIteration")
                break
            except multiprocessing.TimeoutError:
                print("TimeoutError: time left {}".format(abort_time - current_time))
            current_time = time.time()

        print("pool done {}".format(results,))
        pool.terminate()

    else:
        raise AttributeError("Only 'serial' or 'parallel' supported for dispatch method")

    return
