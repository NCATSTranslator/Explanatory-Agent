from abc import ABC, abstractmethod


class clsElement(ABC):

    def __init__(self, dispatchId: int, dispatchDescription: str):
        self.dispatchId = dispatchId
        self.dispatchDescription = dispatchDescription
        self.dispatchRunTimeSeconds = None
        self.dispatchThreadLock = None

    @abstractmethod
    def execute(self):
        pass
