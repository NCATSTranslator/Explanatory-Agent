"""
Assign "The score was obtained based on the contribution value provided by Connection Hypothesis Provider."
to the value of "attribute_type_id": "biolink:description"

Call function Sol P 5: score_by_numeric_attribute () with 2 parameters:
 a) knowledge graph
 b) attribute_type_id: "biolink:Contribution"
"""

from collections import OrderedDict
from modConfig import ZERO_RESULT_SCORE
from .clsExplanationBase import clsExplanationBase

class ExplanationX00007(clsExplanationBase):
    def __init__(self, score_attribute: str, kp_name: str):
        self.case_id = "X00007"
        self.score_attribute = score_attribute
        self.kp_name = kp_name

    def create_results_and_explain(self, case_solution):
        knowledge_graph = case_solution.knowledge_graph

        e00_id, n00_id, n01_id = self.find_node_edge_ids(case_solution.query_graph)

        results = []
        score_attribute_lower = self.score_attribute.lower()
        min_similarity_score, max_similarity_score = self.find_min_max_similarity_scores(knowledge_graph, score_attribute_lower)
        if min_similarity_score is None:
            return []

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

            score = similarity_score[-1] / max_similarity_score

            if score == 0:
                score = ZERO_RESULT_SCORE

            result['score'] = score
            result['attributes'] = [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "The score was obtained based on the contribution value provided by Connection Hypothesis Provider.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "original_attribute_name": "Explanation Text",
                    "attribute_type_id": "biolink:has_evidence",
                    "value": f"This result was given a score of {result['score']} based on the range (i.e, {min_similarity_score} to {max_similarity_score}) observed in the current set of results for the attribute {self.score_attribute} supplied by {self.kp_name}.",
                    "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
                }
            ]

            results.append(result)

        return results

    def edgeAttributeValidate(self, edge):
        """
        Criteria 1: "attribute_type_id": "biolink:primary_knowledge_source" "attribute_source": "infores:connections-hypothesis"
        Criteria 2: “attribute_type_id” = “Contribution” AND "value" = NOT EMPTY
        """
        criteria_1_met = False
        criteria_2_met = False
        for attribute in edge["attributes"]:
            if attribute['attribute_type_id'] == 'biolink:primary_knowledge_source' and 'attribute_source' in attribute and attribute['attribute_source'] == 'infores:connections-hypothesis':
                criteria_2_met = True
            elif attribute['attribute_type_id'] == 'Contribution' and self.value_not_empty(attribute):
                criteria_2_met = True
        return criteria_1_met and criteria_2_met


if __name__ == "__main__":
    x = ExplanationX00007("biolink:Contribution", "awesome_kp")
