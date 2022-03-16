"""
Assign "The score was obtained based on the average accuracy given by the area under the curve informed by the Clinical Risk KP."
to the value of "attribute_type_id": "biolink:description"

Assign Explanation Score = [value given to slot "value" in the attribute where attribute_type_id: "biolink:auc_roc"]
"""

from collections import OrderedDict
from modConfig import ZERO_RESULT_SCORE
from .clsExplanationBase import clsExplanationBase


class ExplanationX00006(clsExplanationBase):
    def __init__(self, score_attribute: str, kp_name: str):
        self.case_id = "X00006"
        self.score_attribute = score_attribute
        self.kp_name = kp_name

    def create_results_and_explain(self, case_solution):
        knowledge_graph = case_solution.knowledge_graph

        e00_id, n00_id, n01_id = self.find_node_edge_ids(case_solution.query_graph)
        results = []
        score_attribute_lower = self.score_attribute.lower()

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
            similarity_score = self.find_edge_similarity_scores(edge, score_attribute_lower)
            if len(similarity_score) <= 0:
                continue

            score = similarity_score[-1]

            if score == 0:
                score = ZERO_RESULT_SCORE

            result['score'] = score
            result['attributes'] = [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "The score was obtained based on the average accuracy given by the area under the curve informed by the Clinical Risk KP.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "original_attribute_name": "Explanation Text",
                    "attribute_type_id": "biolink:has_evidence",
                    "value": result['score'],
                    "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
                }
            ]

            results.append(result)

        return results

    def edgeAttributeValidate(self, edge):
        """
        criteria 1: "attribute_type_id": "biolink:primary_knowledge_source" "value": “infores:biothings-multiomics-clinical-risk"
        criteria 2: “attribute_type_id” = “biolink:auc_roc” AND "value" = NOT EMPTY
        """
        criteria_1_met = False
        criteria_2_met = False
        for attribute in edge["attributes"]:
            if attribute['attribute_type_id'] == 'biolink:aggregator_knowledge_source' and self.attribute_has_value(attribute['value'], 'infores:biothings-multiomics-clinical-risk'):
                criteria_1_met = True
            elif attribute['attribute_type_id'] == 'auc_roc' and self.value_not_empty(attribute):
                criteria_2_met = True
        return criteria_1_met and criteria_2_met


if __name__ == "__main__":
    x = ExplanationX00006("auc_roc", "awesome_kp")