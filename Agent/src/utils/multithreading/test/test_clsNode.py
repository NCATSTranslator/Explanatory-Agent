import unittest
from ..clsElement import clsElement
from ..clsNode import clsNode
import threading
from timeit import default_timer as timer
import time


class clsDummyElement(clsElement):

    def __init__(self, dispatchId: int, dispatchDescription: str):
        super().__init__(dispatchId=dispatchId, dispatchDescription=dispatchDescription)
        self.var = None

    def execute(self):
        if self.dispatchThreadLock is not None:
            with self.dispatchThreadLock:
                time.sleep(5)
        else:
            time.sleep(5)
        self.var = "preserved!"


class clsDummyElementWithCrash(clsElement):

    def __init__(self, dispatchId: int, dispatchDescription: str):
        super().__init__(dispatchId=dispatchId, dispatchDescription=dispatchDescription)
        self.var = None

    def execute(self):
        time.sleep(2)
        x = 1 / 0
        self.var = "preserved!"


class test_clsNode(unittest.TestCase):

    def test_dispatch_mode_validation_with_serial_passes(self):
        node = clsNode(dispatchId=1, dispatchDescription="test", dispatchMode="seRiaL", dispatchList=[])
        self.assertEqual("serial", node.dispatchMode, "Expected dispatchMode to be set to 'serial'")

    def test_dispatch_mode_validation_with_parallel_passes(self):
        node = clsNode(dispatchId=1, dispatchDescription="test", dispatchMode="paRaLlel", dispatchList=[])
        self.assertEqual("parallel", node.dispatchMode, "Expected dispatchMode to be set to 'parallel'")

    def test_dispatch_mode_validation_with_unknown_fails(self):
        with self.assertRaises(AttributeError, msg="Expected a bad dispatchMode to raise"):
            node = clsNode(dispatchId=1, dispatchDescription="test", dispatchMode="unKnOwN", dispatchList=[])

    def test_applying_thread_lock_to_children(self):
        child1 = clsDummyElement(dispatchId=101, dispatchDescription="child 1")
        child2 = clsDummyElement(dispatchId=102, dispatchDescription="child 2")
        rootNode = clsNode(dispatchId=100, dispatchDescription="root node", dispatchMode="serial", dispatchList=[child1, child2])
        rootNode.dispatchThreadLock = threading.Lock()
        rootNode.applyThreadLockToChildren()
        self.assertEqual(rootNode.dispatchThreadLock, child1.dispatchThreadLock, "Expected threadLock to be same reference on child 1")
        self.assertEqual(rootNode.dispatchThreadLock, child2.dispatchThreadLock, "Expected threadLock to be same reference on child 2")

    def test_not_applying_thread_lock_to_children_does_nothing(self):
        child1 = clsDummyElement(dispatchId=101, dispatchDescription="child 1")
        child2 = clsDummyElement(dispatchId=102, dispatchDescription="child 2")
        rootNode = clsNode(dispatchId=100, dispatchDescription="root node", dispatchMode="serial", dispatchList=[child1, child2])
        rootNode.dispatchThreadLock = threading.Lock()
        # don't apply thread lock
        self.assertEqual(None, child1.dispatchThreadLock, "Expected threadLock to be same reference on child 1")
        self.assertEqual(None, child2.dispatchThreadLock, "Expected threadLock to be same reference on child 2")

    def test_dispatching_serial_works(self):
        child1 = clsDummyElement(dispatchId=101, dispatchDescription="child 1")
        child2 = clsDummyElement(dispatchId=102, dispatchDescription="child 2")
        rootNode = clsNode(dispatchId=100, dispatchDescription="root node", dispatchMode="serial", dispatchList=[child1, child2])
        startTime = timer()
        rootNode.execute()
        endTime = timer()
        totalSeconds = endTime - startTime
        self.assertGreaterEqual(totalSeconds, 10, "Expected serial run time to be at least 10 seconds (2x)")
        self.assertEqual(child1.var, "preserved!", "Expected serial run to preserve variable reference for child 1")
        self.assertEqual(child2.var, "preserved!", "Expected serial run to preserve variable reference for child 2")

    def test_dispatching_serial_invoke_on_main_thread(self):
        child1 = clsDummyElement(dispatchId=101, dispatchDescription="child 1")
        child2 = clsDummyElementWithCrash(dispatchId=102, dispatchDescription="child 2")
        rootNode = clsNode(dispatchId=100, dispatchDescription="root node", dispatchMode="serial", dispatchList=[child1, child2])
        startTime = timer()
        with self.assertRaises(ZeroDivisionError, msg="Expected ZeroDivisionError"):
            rootNode.execute()
        endTime = timer()
        totalSeconds = endTime - startTime
        self.assertGreaterEqual(totalSeconds, 7, "Expected serial run time to be at least 7 seconds (1x child 1 + 1x child 2)")
        self.assertEqual(child1.var, "preserved!", "Expected serial run to preserve variable reference for child 1")
        self.assertIsNone(child2.var, "Expected serial run to not set variable reference for child 2")

    def test_dispatching_parallel_works(self):
        child1 = clsDummyElement(dispatchId=101, dispatchDescription="child 1")
        child2 = clsDummyElement(dispatchId=102, dispatchDescription="child 2")
        rootNode = clsNode(dispatchId=100, dispatchDescription="root node", dispatchMode="parallel", dispatchList=[child1, child2])
        startTime = timer()
        rootNode.execute()
        endTime = timer()
        totalSeconds = endTime - startTime
        self.assertGreaterEqual(totalSeconds, 5, "Expected parallel run time to be at least 5 seconds (1x)")
        self.assertLessEqual(totalSeconds, 10, "Expected parallel run time to be less than 10 seconds (2x)")
        self.assertEqual(child1.var, "preserved!", "Expected parallel run to preserve variable reference for child 1")
        self.assertEqual(child2.var, "preserved!", "Expected parallel run to preserve variable reference for child 2")

    def test_dispatching_parallel_invoke_on_main_thread(self):
        child1 = clsDummyElement(dispatchId=101, dispatchDescription="child 1")
        child2 = clsDummyElementWithCrash(dispatchId=102, dispatchDescription="child 2")
        rootNode = clsNode(dispatchId=100, dispatchDescription="root node", dispatchMode="parallel", dispatchList=[child1, child2])
        startTime = timer()
        with self.assertRaises(ZeroDivisionError, msg="Expected ZeroDivisionError"):
            rootNode.execute()
        endTime = timer()
        totalSeconds = endTime - startTime
        self.assertGreaterEqual(totalSeconds, 2, "Expected parallel run time to be at least 2 seconds (1x child 2)")
        self.assertLessEqual(totalSeconds, 5, "Expected parallel run time to be less than 5 seconds (1x child 1")
        self.assertIsNone(child1.var, "Expected parallel run to not set variable reference for child 1")
        self.assertIsNone(child2.var, "Expected parallel run to not set variable reference for child 2")

    def test_dispatching_parallel_thread_lock(self):
        child1 = clsDummyElement(dispatchId=101, dispatchDescription="child 1")
        child2 = clsDummyElement(dispatchId=102, dispatchDescription="child 2")
        rootNode = clsNode(dispatchId=100, dispatchDescription="root node", dispatchMode="parallel", dispatchList=[child1, child2])
        rootNode.dispatchThreadLock = threading.Lock()
        startTime = timer()
        rootNode.execute()
        endTime = timer()
        totalSeconds = endTime - startTime
        self.assertGreaterEqual(totalSeconds, 10, "Expected parallel run time to be at least 10 seconds (1x child 1 + 1x child 2)")
        self.assertEqual(child1.var, "preserved!", "Expected parallel run to preserve variable reference for child 1")
        self.assertEqual(child2.var, "preserved!", "Expected parallel run to preserve variable reference for child 2")


if __name__ == '__main__':
    unittest.main()
