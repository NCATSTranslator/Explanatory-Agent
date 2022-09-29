"""
Assign "The score was obtained based on the existence of publications as informed by Automat CTD"
to the value of "attribute_type_id": "biolink:description"
Assign Explanation Score = 1
Assign:
{
  "attribute_type_id": "biolink:has_evidence",
  "value":  "This result was given a score of 1 because the Automat CTD knowledge provider producing this result has indicated a publication in its support",
  "original_attribute_name": "Explanation Text",
  "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
}
"""

from collections import OrderedDict
from modConfig import ZERO_RESULT_SCORE
from .clsExplanationBase import clsExplanationBase

class ExplanationX00009(clsExplanationBase):
    def __init__(self, kp_name: str):
        self.case_id = "X00009"
        self.kp_name = kp_name

    def create_results_and_explain(self, case_solution):
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

            score = 1

            if score == 0:
                score = ZERO_RESULT_SCORE

            result["score"] = score
            result['attributes'] = [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "The score was obtained based on the existence of publications as informed by Automat CTD",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "attribute_type_id": "biolink:has_evidence",
                    "value":  "This result was given a score of 1 because the Automat CTD knowledge provider producing this result has indicated a publication in its support",
                    "original_attribute_name": "Explanation Text",
                    "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
                }
            ]

            results.append(result)

        return results

    def edgeAttributeValidate(self, edge):
        """
        Criteria 1: "original_attribute_name": "biolink:original_knowledge_source" "value": "infores:ctd"
        Criteria 2: "attribute_type_id": "publications" AND "value" = NOT EMPTY
        """
        criteria_1_met = False
        criteria_2_met = False
        for attribute in edge["attributes"]:
            if 'original_attribute_name' in attribute and attribute['original_attribute_name'] == 'biolink:original_knowledge_source' and attribute['value'] == 'infores:ctd':
                criteria_1_met = True
            elif attribute['attribute_type_id'] == 'biolink:publications' and self.value_not_empty(attribute):
                criteria_2_met = True
        return criteria_1_met and criteria_2_met


if __name__ == "__main__":
    x = ExplanationX00009("awesome_kp")
