"""
WHAT: Workflow parsing and information. See https://github.com/NCATSTranslator/OperationsAndWorkflows for details and
https://github.com/NCATSTranslator/OperationsAndWorkflows/blob/main/schema/operation.json for operations' schema.
WHY: Removes this logic from the view, and puts in a testable class
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2022-03-13
"""
from typing import List
from abc import ABC, abstractmethod


class Operation(ABC):
    # TODO: Implement runner_parameters (seems to be global across all operations?)
    def __init__(self, definition: dict):
        self.definition: dict = definition

    @abstractmethod
    def parse(self):
        raise NotImplementedError

    def __repr__(self):
        return f"{repr(self.__class__.__name__)}(definition={repr(self.definition)})"

    def __eq__(self, other):
        return self.definition == other.definition


class FillOperation(Operation):
    # TODO: Implement qedge_keys allow/deny lists
    def __init__(self, definition):
        super(FillOperation, self).__init__(definition)
        self.allow_list: List[str] | None = None
        self.deny_list: List[str] | None = None

    def parse(self):
        # only one list can be present, thankfully avoiding the problem of which list to apply first
        if "allowlist" in self.definition["parameters"]:
            self.allow_list = self.definition["parameters"]["allowlist"]

        elif "denylist" in self.definition["parameters"]:
            self.deny_list = self.definition["parameters"]["denylist"]

        # one list MUST be present
        assert self.allow_list or self.deny_list, "An allowlist or denylist must be provided!"

    def __repr__(self):
        return f"{repr(self.__class__.__name__)}(definition={repr(self.definition)}, allow_list={repr(self.allow_list)}, deny_list={repr(self.deny_list)})"

    def __eq__(self, other):
        return self.definition == other.definition and \
               self.allow_list == other.allow_list and \
               self.deny_list == other.deny_list


class BindOperation(Operation):
    def __init__(self, definition):
        super(BindOperation, self).__init__(definition)

    def parse(self):
        # no parameters as of 2022-03-13
        return


class CompleteResultsOperation(Operation):
    def __init__(self, definition):
        super(CompleteResultsOperation, self).__init__(definition)

    def parse(self):
        # no parameters as of 2022-03-13
        return
