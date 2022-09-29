"""
No explanation at all. Invoked when a KP is present in the Explanation Excluded KP table.
"""

from collections import OrderedDict
from utils.clsLog import clsLogEvent
import logging
from .clsExplanationBase import clsExplanationBase


class ExplanationNone(clsExplanationBase):
    def __init__(self):
        self.case_id = "None"
        self.logs = []

    def create_results_and_explain(self, case_solution):
        query_graph = case_solution.query_graph
        knowledge_graph = case_solution.knowledge_graph

        e00_id = list(query_graph["edges"].keys())[0]
        node_ids = sorted(list(query_graph["nodes"].keys()))
        n00_id = node_ids[0]
        n01_id = node_ids[1]

        results = []

        # sorting for deterministic results. This can go away after index isn't used for rank.
        for index, (edgeId, edge) in enumerate(sorted(list(knowledge_graph['edges'].items()), key=lambda i: i[0])):
            if index == 0:
                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="DEBUG",
                    code="",
                    message=f"Starting explanations for {len(knowledge_graph['edges'])} edges."
                ))
            if index % 50 == 0 and index > 0:
                logging.debug(f"{self.case_id} edge {index} of {len(knowledge_graph['edges'])}")
                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="DEBUG",
                    code="",
                    message=f"Explained {index} of {len(knowledge_graph['edges'])} edges."
                ))

            result = OrderedDict()
            result['edge_bindings'] = {
                e00_id: [{
                    "id": edgeId,
                }]
            }
            result['node_bindings'] = {
                n00_id: [{"id": edge['subject']}],
                n01_id: [{"id": edge['object']}],
            }
            result['score'] = 0.0
            result['attributes'] = []

            results.append(result)

        self.logs.append(clsLogEvent(
            identifier=self.case_id,
            level="DEBUG",
            code="",
            message=f"Explained all {len(knowledge_graph['edges'])} edges."
        ))

        return results
