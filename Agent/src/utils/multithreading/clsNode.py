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

        for object in self.dispatchList:
            object.dispatchThreadLock = self.dispatchThreadLock

    def execute(self):

        self.applyThreadLockToChildren()

        if self.dispatchList is not None:
            dispatch(objects=self.dispatchList, method=self.dispatchMode, parentId=self.dispatchId)
