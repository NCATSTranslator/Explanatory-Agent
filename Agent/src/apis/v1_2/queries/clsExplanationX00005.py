"""
Assign "The score was obtained based on averaging the confidence level of the subject and object nodes as informed by COHD."
to the value of "attribute_type_id": "biolink:description"

Call function Sol P 5: score_by_numeric_attribute () with 2 parameters:
 a) knowledge graph
 b) attribute_type_id: "ln_ratio"
"""

from collections import OrderedDict
from modConfig import ZERO_RESULT_SCORE
from .clsExplanationBase import clsExplanationBase


class ExplanationX00005(clsExplanationBase):
    def __init__(self, score_attribute: str, kp_name: str):
        self.case_id = "X00005"
        self.score_attribute = score_attribute
        self.kp_name = kp_name

    def create_results_and_explain(self, case_solution):
        knowledge_graph = case_solution.knowledge_graph

        e00_id, n00_id, n01_id = self.find_node_edge_ids(case_solution.query_graph)
        results = []
        score_attribute_lower = self.score_attribute.lower()
        min_similarity_score, max_similarity_score = self.find_min_max_similarity_scores(knowledge_graph, score_attribute_lower, score_attribute_key='original_attribute_name')
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
            similarity_score = self.find_edge_similarity_scores(edge, score_attribute_lower, score_attribute_key='original_attribute_name')
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
                    "value": "The score was obtained based on averaging the confidence level of the subject and object nodes as informed by COHD.",
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
        criteria 1: "attribute_source": "infores:cohd" AND “attribute_type_id” = “has_evidence” AND "original_attribute_name" = "ln_ratio" AND "value" = NOT EMPTY
        """
        criteria_1_met = False
        for attribute in edge["attributes"]:
            if (
                'attribute_source' in attribute and
                'attribute_type_id' in attribute and
                'original_attribute_name' in attribute and
                attribute['attribute_source'] == "infores:cohd" and
                attribute['attribute_type_id'] == "biolink:has_evidence" and
                attribute['original_attribute_name'] == "ln_ratio" and
                self.value_not_empty(attribute)
            ):
                criteria_1_met = True
        return criteria_1_met


if __name__ == "__main__":
    from collections import namedtuple

    query_graph = {
      "edges": {
        "e01": {
            "object": "n0",
            "subject": "n1"
        },
     },
      "nodes": {
            "n0": {"categories": ["biolink:Gene"]},
            "n1": {"categories": ["biolink:Gene"]}
        }
    }
    knowledge_graph = {
        "edges": {
            "knowledge_graph_edge1": {
                "subject": "n1",
                "object": "n2",
                "attributes": [
                    {"attribute_type_id": "ln_ratio", "value": 1, "attribute_source": "", "original_attribute_name": ""},
                    {"attribute_type_id": "ln_ratio", "value": 2, "attribute_source": "", "original_attribute_name": ""},
                    {"attribute_type_id": "ln_ratio", "value": 3, "attribute_source": "", "original_attribute_name": ""},
                    {"attribute_type_id": "ln_ratio", "value": 4, "attribute_source": "", "original_attribute_name": ""},
                    {"attribute_type_id": "ln_ratio", "value": 5, "attribute_source": "", "original_attribute_name": ""},
                    {
                      "attribute_source": "infores:cohd",
                      "attribute_type_id": "biolink:has_evidence",
                      "description": "Observed-expected frequency ratio. http://cohd.io/about.html",
                      "original_attribute_name": "ln_ratio",
                      "value": 4.147823023620047,
                      "value_type_id": "EDAM:data_1772"
                    },
                ]
            }
        }
    }
    CaseSolutionMock = namedtuple('CaseSolutionMock', ['query_graph', 'knowledge_graph'])
    case_solution = CaseSolutionMock(query_graph, knowledge_graph)

    x = ExplanationX00005("ln_ratio", "awesome_kp")
    res = x.create_results_and_explain(case_solution)[0]
    assert res == {
        'edge_bindings': {
            'e01': [{'id': 'knowledge_graph_edge1'}]
        },
        'node_bindings': {
            'n0': [{'id': 'n1'}],
            'n1': [{'id': 'n2'}]
        },
        'score': 1.0,
        'attributes': [
            {
                'original_attribute_name': 'Explanation Rationale',
                'attribute_type_id': 'biolink:description',
                'value': 'The score was obtained based on averaging the confidence level of the subject and object nodes as informed by COHD.',
                'description': 'Describes to user the Rationale for explaining the ranking'
            },
            {
                'original_attribute_name': 'Explanation Text',
                'attribute_type_id': 'biolink:has_evidence',
                'value': 'This result was given a score of 1.0 based on the range (i.e, 1 to 5) observed in the current set of results for the attribute ln_ratio supplied by awesome_kp.',
                'description': 'Describes the reason this specific edge receives a score w.r.t Rationale'
            }
        ]
    }
    assert x.edgeAttributeValidate(knowledge_graph["edges"]["knowledge_graph_edge1"]) == 1