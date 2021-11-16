import logging
from .modDispatcher import dispatch
from .clsElement import clsElement


class clsNode(clsElement):

    def __init__(self, dispatchId: int, dispatchDescription: str, dispatchMode: str, dispatchList: list):
        super().__init__(dispatchId=dispatchId, dispatchDescription=dispatchDescription)

        self.dispatchMode = dispatchMode.lower()
        self.dispatchList = dispatchList

        self.validateInputs()

    def validateInputs(self):

        if self.dispatchMode not in ("serial", "parallel"):
            raise AttributeError(f"Node with id {str(self.dispatchId)} must have dispatchMode set to 'serial' or 'parallel'")

    def applyThreadLockToChildren(self):

        if self.dispatchList is not None:
            for object in self.dispatchList:
                object.dispatchThreadLock = self.dispatchThreadLock

    # to be overridden if desired, but not abstract
    def preExecute(self):
        pass

    def dispatch(self):
        if self.dispatchList is not None:
            dispatch(
                objects=self.dispatchList,
                method=self.dispatchMode,
                parentId=self.dispatchId,
            )

    def execute(self):
        self.applyThreadLockToChildren()
        self.preExecute()
        self.dispatch()
