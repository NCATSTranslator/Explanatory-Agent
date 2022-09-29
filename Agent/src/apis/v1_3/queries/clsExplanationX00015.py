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


class ExplanationX00015(clsExplanationBase):
    def __init__(self, kp_name: str):
        self.case_id = "X00015"
        self.kp_name = kp_name

    def edgeAttributeValidate(self, edge):
        """
        "attribute_source": "infores:chembl" AND "attribute_type_id": "biolink:has_confidence_level" AND "original_attribute_name":"phase" AND "value" = NOT EMPTY
        :param edge:
        :return:
        """
        criteria_1_met = False
        for attribute in edge["attributes"]:
            if (
                    'attribute_source' in attribute and
                    attribute['attribute_source'] == 'infores:chembl' and
                    attribute['attribute_type_id'] == "biolink:has_confidence_level" and
                    'original_attribute_name' in attribute and
                    attribute['original_attribute_name'] == "phase" and
                    self.value_not_empty(attribute)
            ):
                criteria_1_met = True
        return criteria_1_met

    def create_results_and_explain(self, case_solution):
        """
        Assign "The score was obtained based on the confidence level value from Chembl" to the value of "attribute_type_id": "biolink:description"
        IF "attribute_source": "infores:chembl" AND "attribute_type_id": "biolink:has_confidence_level" AND "original_attribute_name":"phase" AND "value" = 4
        THEN Assign Explanation Score = 1;
        ELSEIF "attribute_source": "infores:chembl" AND "attribute_type_id": "biolink:has_confidence_level" AND
        "original_attribute_name":"phase" AND
        "value" = 3
        THEN Assign Explanation Score = 0.75;
        ELSEIF "attribute_source": "infores:chembl" AND "attribute_type_id": "biolink:has_confidence_level" AND
        "original_attribute_name":"phase" AND
        "value" = 2
        THEN Assign Explanation Score = 0.5;
        ELSEIF "attribute_source": "infores:chembl" AND "attribute_type_id": "biolink:has_confidence_level" AND
        "original_attribute_name":"phase" AND
        "value" = 1
        THEN Assign Explanation Score = 0.25;
        ELSE  Assign Explanation Score = 0
        Assign:
        {
          "attribute_type_id": "biolink:has_evidence",
          "value":  "This result was given a score of [[Explanation Score]] based on the clinical trial phase, as supplied by CHEMBL. The value associations are:
          0     : Phase 0 - Pharmacokinetics; particularly oral bioavailability and half-life of the drug
          0.25 : Phase I - Dose-ranging on healthy volunteers for safety
          0.5  : Phase II  - Testing of drug on participants to assess efficacy and side effects
          0.75 : Phase III  - Testing of drug on participants to assess efficacy, effectiveness and safety
          1     : Phase IV - Post marketing surveillance in public ",
          "original_attribute_name": "Explanation Text",
          "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
        }
        :param case_solution:
        :return:
        """
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

            value_attribute = None
            for attribute in edge["attributes"]:
                if (
                        'attribute_source' in attribute and
                        attribute['attribute_source'] == 'infores:chembl' and
                        attribute['attribute_type_id'] == "biolink:has_confidence_level" and
                        'original_attribute_name' in attribute and
                        attribute['original_attribute_name'] == "phase"
                ):
                    value_attribute = attribute
                    break

            score = 0
            if "value" in value_attribute:
                if value_attribute["value"] == 4:
                    score = 1
                elif value_attribute["value"] == 3:
                    score = 0.75
                elif value_attribute["value"] == 2:
                    score = 0.5
                elif value_attribute["value"] == 1:
                    score = 0.25

            if score == 0:
                score = ZERO_RESULT_SCORE

            result["score"] = score
            result['attributes'] = [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "The score was obtained based on the confidence level value from Chembl.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "attribute_type_id": "biolink:has_evidence",
                    "value": f"""This result was given a score of {result["score"]} based on the clinical trial phase, as supplied by CHEMBL. The value associations are:
0     : Phase 0 - Pharmacokinetics; particularly oral bioavailability and half-life of the drug
0.25 : Phase I - Dose-ranging on healthy volunteers for safety
0.5  : Phase II  - Testing of drug on participants to assess efficacy and side effects
0.75 : Phase III  - Testing of drug on participants to assess efficacy, effectiveness and safety
1     : Phase IV - Post marketing surveillance in public""",
                    "original_attribute_name": "Explanation Text",
                    "description": "Describes to user the reason this specific edge receives a score w.r.t Rationale."
                }
            ]

            results.append(result)

        return results


if __name__ == "__main__":
    x = ExplanationX00015("awesome_kp")
