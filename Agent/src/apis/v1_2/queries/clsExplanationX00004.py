"""
Assign "Score assigned was zero because no evidence, provenance, or confidence information was available to compute a score."
to the value of "attribute_type_id": "biolink:description"

Assign Explanation Score = 0
Assign:
{
    "attribute_type_id": "biolink:has_evidence",
    "value":  "No explanation as this edge is not scored",
    "original_attribute_name": "Explanation Text",
    "description": "Describes to user the reason this specific edge receives a score w.r.t Rationale."
}
"""

from collections import OrderedDict
from modConfig import ZERO_RESULT_SCORE
from .clsExplanationBase import clsExplanationBase


class ExplanationX00004(clsExplanationBase):
    def __init__(self, kp_name: str):
        self.case_id = "X00004"
        self.kp_name = kp_name

    def edgeAttributeValidate(self, edge):
        """
        No attribute criteria, so this explanation should not be used.
        :param edge:
        :return:
        """
        return False

    def create_results_and_explain(self, case_solution):
        """
        (FOR every edge:) Assign "The score was obtained based on the relationship between biomedical entities found in published literature." to the value of "attribute_type_id": "biolink:description"

        (FOR every edge:)
            Call function Voc P 8: find_node_synonyms () with 1 parameter:
                a) NodeID - (Subject Node the first time)
            RETURN Subject Node Synonyms List
            Call function Voc P 8: find_node_synonyms () with 1 parameter:
                a) NodeID - (Object Node the first time)
            RETURN Object Node Synonyms List
            Call function Sol P 4: relationship_finder() with 4 parameters:
                a) Subject Node Category
                b) Subject Node Synonyms List
                c) Object Node Category
                d) Object Node Synonyms List
        :param case_solution:
        :return:
        """
        raise NotImplementedError("Missing Disease TOKS table")
        knowledge_graph = case_solution.knowledge_graph

        e00_id, n00_id, n01_id = self.find_node_edge_ids(case_solution.query_graph)

        results = []

        for index, (edgeId, edge) in self.enumerate_edges(knowledge_graph):
            result = OrderedDict({
                'edge_bindings': {
                    e00_id: [{"id": edgeId}]
                },
                'node_bindings': {
                    n00_id: [{"id": edge['subject']}],
                    n01_id: [{"id": edge['object']}],
                }
            })

            score = 0

            if score == 0:
                score = ZERO_RESULT_SCORE

            result["score"] = score
            result['attributes'] = [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "Score assigned was zero because no evidence, provenance, or confidence information was available to compute a score.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "attribute_type_id": "biolink:has_evidence",
                    "value":  "No explanation as this edge is not scored",
                    "original_attribute_name": "Explanation Text",
                    "description": "Describes to user the reason this specific edge receives a score w.r.t Rationale."
                }
            ]

            results.append(result)

        return results


if __name__ == "__main__":
    x = ExplanationX00004("awesome_kp")
