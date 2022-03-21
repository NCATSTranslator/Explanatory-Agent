"""
WHAT: Tests the Workflow class for parsing all operations provided. Also doubles as tests for the Operation classes themselves.
WHY: Ensures workflows are parsed correctly.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2022-03-13
"""

import unittest
from apis.v1_2.models.workflow.clsWorkflow import Workflow
from apis.v1_2.models.workflow.clsOperations import FillOperation, BindOperation, CompleteResultsOperation


class TestWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_nominal_fill(self):
        workflow_definition = [
            {
                "id": "fill",
                "parameters": {
                    "denylist": ["KP1", "KP2"]
                }
            }
        ]
        workflow = Workflow(workflow_definition)
        workflow.parse()

        expected_fill = FillOperation({"id": "fill", "parameters": {"denylist": ["KP1", "KP2"]}})
        expected_fill.allow_list = None
        expected_fill.deny_list = ["KP1", "KP2"]
        expected_operations = [expected_fill]

        self.assertEqual(len(workflow.operations), len(expected_operations))
        for i, operation in enumerate(expected_operations):
            self.assertEqual(workflow.operations[i], operation)

    def test_fill_list_assert(self):
        workflow_definition = [
            {
                "id": "fill",
                "parameters": {}
            }
        ]

        try:
            workflow = Workflow(workflow_definition)
            workflow.parse()
            raise ValueError("An assertion should have been reached!")
        except AssertionError as e:
            self.assertEqual(str(e), "An allowlist or denylist must be provided!")

    def test_nominal_fill_bind_complete_with_allowlist(self):
        workflow_definition = [
            {
                "id": "fill",
                "parameters": {
                    "allowlist": ["icees"]
                }
            },
            {
                "id": "bind",
                "parameters": {}
            },
            {
                "id": "complete_results",
                "parameters": {}
            }
        ]
        workflow = Workflow(workflow_definition)
        workflow.parse()

        expected_fill = FillOperation({"id": "fill", "parameters": {"allowlist": ["icees"]}})
        expected_fill.allow_list = ["icees"]
        expected_fill.deny_list = None
        expected_operations = [
            expected_fill,
            BindOperation({"id": "bind", "parameters": {}}),
            CompleteResultsOperation({"id": "complete_results", "parameters": {}})
        ]

        self.assertEqual(len(workflow.operations), len(expected_operations))
        for i, operation in enumerate(expected_operations):
            self.assertEqual(workflow.operations[i], operation)

    def test_nominal_lookup(self):
        workflow_definition = [
            {
                "id": "lookup",
                "parameters": {}
            }
        ]
        workflow = Workflow(workflow_definition)
        workflow.parse()

        expected_fill = FillOperation({"id": "fill", "parameters": {"denylist": [""]}})
        expected_fill.allow_list = None
        expected_fill.deny_list = [""]
        expected_operations = [
            expected_fill,
            BindOperation({"id": "bind", "parameters": {}}),
            CompleteResultsOperation({"id": "complete_results", "parameters": {}})
        ]

        self.assertEqual(len(workflow.operations), len(expected_operations))
        for i, operation in enumerate(expected_operations):
            self.assertEqual(workflow.operations[i], operation)
