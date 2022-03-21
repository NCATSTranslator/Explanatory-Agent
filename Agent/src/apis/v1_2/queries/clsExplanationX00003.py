"""
STEP 1 SCORE BY NUMERIC ATTRIBUTE 

INPUT: Parameters are qg and kg, kg and the name of the numeric 'attribute_type_id' to be used: (kg,Numeric_attribute_type_id_value);   

PROCESS:  Receives an entire kg to compute a normalized score for a numeric 'attribute_type_id', which is passed as parameter, by getting all the numeric
  values  given in the 'value' slot for the 'attribute_type_id' ="Numeric_attribute_type_id_value" for all edges in the kg, and normalize them to 0-1 to
  produce the score. The text will include the value and explain that the score was computed based on all the other scores in this set of results.  
  For example, 'attribute_type_id' ="CMAP:similarity score"
  'value' = 0.9975  

ALGORITHM:
 a) Extract all the numeric values found in every edge for the "value" slot (which will be a number) corresponding to the
  'attribute_type_id' =Numeric_attribute_type_id_value (given as parameter).  
b) Compute the minimum, maximum, and compute score as the similarity score value divided by the maximum.
c) Populate text for filling the slot value below with the following text: "This result was given a score of [[score value]] based on the range
  (i.e, [[minimum]] to [[maximum]]) observed in the current set of results for the attribute [[attribute_type_id]] supplied by
  [[biolink:aggregator_knowledge_source]]  ." 
  Present information created above as follows: 
  {
      "attribute_type_id": "biolink:has_evidence",
      "value":  "see above.",
      "original_attribute_name": "Explanation Text",
      "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
  }

  ASSUMPTIONS: biolink:aggregator_knowledge_source is given within the kg. The underlined variables within the ALGORITHM are then used to fill slots in the
  output text where these slots are indicated with the underlined variable names between double square brackets.

 DEPENDENCY: N/A

 OUTPUT:
Score and   "attribute_type_id": "biolink:has_evidence",
  "value":  "[few sentences corresponding to explanation]"
"""

from collections import OrderedDict
from utils.clsLog import clsLogEvent
from modConfig import ZERO_RESULT_SCORE
import logging

from .clsExplanationBase import clsExplanationBase

class ExplanationX00003(clsExplanationBase):
    def __init__(self, score_attribute: str, kp_name: str):
        self.case_id = "X00003"
        self.score_attribute = score_attribute
        self.kp_name = kp_name
        self.logs = []

    def create_results_and_explain(self, case_solution):
        query_graph = case_solution.query_graph
        knowledge_graph = case_solution.knowledge_graph

        e00_id, n00_id, n01_id = self.find_node_edge_ids(case_solution.query_graph)

        results = []
        score_attribute_lower = self.score_attribute.lower()
        # MolePro changed their attribute value to "CMAP:similarity score" (no underscores) so test for that, as well.
        score_attribute_lower_no_underscores = score_attribute_lower.replace("_", " ")

        # first pass on edges to get all scores
        min_similarity_score, max_similarity_score = self.find_min_max_similarity_scores(knowledge_graph, score_attribute_lower)
        if min_similarity_score is None:
            return []

        # sorting for deterministic results. This can go away after index isn't used for rank.
        for index, (edgeId, edge) in self.enumerate_edges(knowledge_graph):
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
                    "value": "The score was obtained based on the similarity score produced by CMAP (portals.broadinstitute.org/cmap).",
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

        self.logs.append(clsLogEvent(
            identifier=self.case_id,
            level="DEBUG",
            code="",
            message=f"Explained all {len(knowledge_graph['edges'])} edges."
        ))

        return results

    def edgeAttributeValidate(self, edge):
        """
        criteria 1: "attribute_type_id": "biolink:aggregator_knowledge_source" "value": "infores:molepro"
        criteria 2: “attribute_type_id” = “CMAP:similarity_score” AND "value" = NOT EMPTY
        """
        criteria_1_met = False
        criteria_2_met = False
        for attribute in edge["attributes"]:
            if attribute['attribute_type_id'] == 'biolink:aggregator_knowledge_source' and attribute['value'] ==  'infores:molepro':
                criteria_1_met = True
            elif attribute['attribute_type_id'] == 'CMAP:similarity_score' and self.value_not_empty(attribute):
                criteria_2_met = True
        return criteria_1_met and criteria_2_met


if __name__ == "__main__":
    x = ExplanationX00003("CMAP:similarity_score", "awesome_kp")

    edges = {
        "e1": {"subject": "s1", "object": "o1", "attributes": [
            {"attribute_type_id": "CMAP:similarity_score", "value": 100.0},
            {"attribute_type_id": "something else", "value": 1.0},
        ]},
        "e2": {"subject": "s1", "object": "o1", "attributes": [
            {"attribute_type_id": "something else", "value": 1.0},
            {"attribute_type_id": "CMAP:similarity_score", "value": 50.0},
        ]},
        "e3": {"subject": "s1", "object": "o1", "attributes": [
            {"attribute_type_id": "CMAP:similarity_score", "value": 10.0},
            {"attribute_type_id": "something else", "value": 1.0},
        ]}
    }
    # results = x.create_results_and_explain({'edges': edges})

    res = 0
    for edge in edges.values():
        res += x.edgeAttributeValidate(edge)
    assert res == 3