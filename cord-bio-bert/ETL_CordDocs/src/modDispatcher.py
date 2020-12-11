"""
WHAT: A dispatcher to facilitate executing objects in series or in parallel
WHY: Need to speed up processing time for parallel execution, but also allow for series execution for tests
ASSUMES: Linux/Unix OS for multiprocessing logging to work properly; Windows still runs, but objects in dispatcher won't write their logs
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""

import multiprocessing
from tqdm import tqdm
import logging


def runner(obj):
    """
    Run an object, the generic function to be called over and over again in parallel.
    Assumes the object has an "id" property.
    :param obj: Any instance of an object which implements an "execute" method
    :return: A copy of the original object
    """

    try:
        obj.execute()
    except Exception as e:
        msg = "Document with id %s failed to process" % str(obj.id)
        print(msg)
        print(e)
        logging.error(msg)
        logging.error(e)
        raise

    return obj


def dispatcher(objs, mode, unit='it'):
    """
    Execute a list of objects in parallel or series
    :param objs: Any list of instantiated objects which implement an "execute" method
    :param mode: "serial" to run as a for loop, "parallel" to run on all available CPUs
    :param unit: Describes 1 element of the object list, default 'it' for 'iteration' per tqdm documentation
    :return: A list of copies of the original objects
    """

    if mode.lower() == "serial":

        msg = "Dispatching in series"
        print(msg)
        logging.info(msg)

        for obj in tqdm(objs, desc="Processing objects", unit=unit):
            runner(obj)
        return objs

    elif mode.lower() == "parallel":

        msg = "Dispatching in parallel on %s cores" % str(multiprocessing.cpu_count())
        print(msg)
        logging.info(msg)

        with multiprocessing.Pool() as pool:
            newObjs = list(tqdm(pool.imap_unordered(runner, objs), desc="Processing objects", total=len(objs), unit=unit))
        return newObjs
