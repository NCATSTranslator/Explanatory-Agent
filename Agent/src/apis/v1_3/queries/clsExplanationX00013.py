"""
Assign "The score was obtained based on the identification of a clinical trial obtained in CHEMBL. "
to the value of "attribute_type_id": "biolink:description"

Assign Explanation Score = 1
Assign:
{
  "attribute_type_id": "biolink:has_evidence",
  "value":  "This result was given a score of 1 because the knowledge provider producing this result has identified a clinical trial (obtained via CHEMBL) in its support.",
  "original_attribute_name": "Explanation Text",
  "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
}
"""

from collections import OrderedDict
from modConfig import ZERO_RESULT_SCORE
from .clsExplanationBase import clsExplanationBase

class ExplanationX00013(clsExplanationBase):
    def __init__(self, kp_name: str):
        self.case_id = "X00013"
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
                    "value": "The score was obtained based on the identification of a clinical trial obtained in CHEMBL.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "attribute_type_id": "biolink:has_evidence",
                    "value":  "This result was given a score of 1 because the knowledge provider producing this result has identified a clinical trial (obtained via CHEMBL) in its support.",
                    "original_attribute_name": "Explanation Text",
                    "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
                }
            ]

            results.append(result)

        return results

    def edgeAttributeValidate(self, edge):
        """
        Criteria 1: "attribute_source": "infores:chembl" AND "attribute_type_id": "biolink:Publication" AND "original_attribute_name": "ClinicalTrials" AND "value" = NOT EMPTY
        """
        criteria_1_met = False
        for attribute in edge["attributes"]:
            if (
                'attribute_source' in attribute and
                attribute['attribute_source'] == 'infores:chembl' and
                attribute['attribute_type_id'] == "biolink:Publication" and
                'original_attribute_name' in attribute and
                attribute['original_attribute_name'] == "ClinicalTrials" and
                self.value_not_empty(attribute)
            ):
                criteria_1_met = True
        return criteria_1_met


if __name__ == "__main__":
    x = ExplanationX00013("awesome_kp")
