"""
WHAT: Workflow parsing and information. See https://github.com/NCATSTranslator/OperationsAndWorkflows for details and
https://github.com/NCATSTranslator/OperationsAndWorkflows/blob/main/schema/operation.json for operations' schema.
WHY: Removes this logic from the view, and puts in a testable class
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2022-03-13

TODO: Fill out the remaining operations, implement in QueryManager
"""
from .clsOperations import FillOperation, BindOperation, CompleteResultsOperation


class Workflow:
    OPERATION_CLASS_MAP = {
        "fill": FillOperation,
        "bind": BindOperation,
        "complete_results": CompleteResultsOperation
    }

    def __init__(self, workflow_definition):
        """
        ASSUMES the workflow definition has already been validated!
        :param workflow_definition: Nested dictionary of operation rules to parse.
        """
        self.definition = workflow_definition
        self.operations = []

    def parse(self):
        for operation_definition in self.definition:
            if operation_definition["id"] == "lookup":
                # Lookup is defines as a fill-bind-complete_results shorthand that contains no parameters
                # since a list MUST be provided, create a denylist with a bogus KP name so all KPs are matched
                self.parse_operation({"id": "fill", "parameters": {"denylist": [""]}})
                self.parse_operation({"id": "bind", "parameters": {}})
                self.parse_operation({"id": "complete_results", "parameters": {}})
            else:
                self.parse_operation(operation_definition)

    def parse_operation(self, operation_definition):
        """
        Instantiate a class handler for the operation and have it parse any parameters supplied
        :param operation_definition: Definition nested dictionary for the operation. Must always have an ID according to the specification.
        :return: Appends an Operation-type class with fully parsed data to the operations list.
        """
        operation_id = operation_definition["id"]
        operation_class = self.OPERATION_CLASS_MAP.get(operation_id, None)
        if operation_class:
            operation = operation_class(operation_definition)
            operation.parse()
            self.operations.append(operation)
