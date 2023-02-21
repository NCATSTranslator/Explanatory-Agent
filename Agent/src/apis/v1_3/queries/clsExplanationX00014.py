"""
Lookup Subject ID in SRI name resolver to obtain the subject label: Subject_Name
Lookup Object ID in SRI name resolver to obtain the object label: Object_Name
Post on “https://arax.ncats.io/api/arax/v1.2/PubmedMeshNgd/” + ”Subject_Name/” + “Object_Name” and note the score within variable "value"

Assign "Score assigned based on Normalized Google Distance (NGD) computed between the two terms using the ARAX SmartAPI endpoint" to the value of "attribute_type_id": "biolink:description"
Assign Explanation Score = score within variable "value"
Assign:
    {"attribute_type_id": "biolink:has_evidence",
     "value":  "This result was given a score corresponding to the Normalized Google Distance (NGD) between the terms.",
     "original_attribute_name": "Explanation Text",
     "description": "Describes to user the reason this specific edge receives a score w.r.t Rationale." }
"""

from collections import OrderedDict
from modConfig import ZERO_RESULT_SCORE
from .clsExplanationBase import clsExplanationBase
from .clsNameResolutionProvider import clsNameResolutionProvider
from .clsMeshNormalizedGoogleDistanceProvider import clsMeshNormalizedGoogleDistanceProvider
import requests
from utils.clsLog import clsLogEvent
from itertools import product
from typing import List, Optional
import logging


class ExplanationX00014(clsExplanationBase):
    def __init__(self, kp_name: str):
        self.case_id = "X00014"
        self.kp_name = kp_name
        self.logs = []
        # number of synonyms of each subject and object to try and find NGD of.
        self.synonym_try_count = 3

    def edgeAttributeValidate(self, edge):
        """
        No attribute criteria, so this explanation should not be used.
        :param edge:
        :return:
        """
        return False

    def get_ngd(self, subject_synonyms: List[str], object_synonyms: List[str]) -> Optional[float]:
        """
        Return the Normalized Google distance
        :param subject_synonyms:
        :param object_synonyms:
        :return: Value of the first matched NGD, None if no values were found
        """
        for subject_name, object_name in product(subject_synonyms, object_synonyms):

            ngd_provider = clsMeshNormalizedGoogleDistanceProvider(subject_name, object_name)
            ngd_provider.get_value()
            logging.debug(f"Subject: {subject_name} Object: {object_name} Value: {ngd_provider.value}")
            if ngd_provider.value:
                return ngd_provider.value

        return None

    def create_results_and_explain(self, case_solution):
        knowledge_graph = case_solution.knowledge_graph

        e00_id, n00_id, n01_id = self.find_node_edge_ids(case_solution.query_graph)

        results = []

        # sorting edge IDs for deterministic results.
        edges = sorted(list(knowledge_graph['edges'].items()), key=lambda i: i[0])

        # bulk get all canonical identifiers for all node ids
        node_identifiers = set()
        for index, (edgeId, edge) in enumerate(edges):
            edge_subject = edge["subject"]
            edge_object = edge["object"]
            node_identifiers.add(edge_subject)
            node_identifiers.add(edge_object)
        logging.debug(f"Getting node identifiers")
        self.logs.append(clsLogEvent(
            identifier=self.case_id,
            level="DEBUG",
            code="",
            message=f"Getting all ({len(node_identifiers)}) node identifiers."
        ))
        name_resolution_provider = clsNameResolutionProvider(sorted(list(node_identifiers)))
        name_resolution_provider.get_synonyms()
        synonyms = name_resolution_provider.synonyms

        for index, (edgeId, edge) in list(self.enumerate_edges(knowledge_graph))[:10]:
            result = OrderedDict({
                'edge_bindings': {
                    e00_id: [{"id": edgeId}]
                },
                'node_bindings': {
                    n00_id: [{"id": edge['subject']}],
                    n01_id: [{"id": edge['object']}],
                }
            })

            # collect up to three synonyms for each subject and object
            subject_synonyms = synonyms.get(edge['subject'], [edge['subject']])[:self.synonym_try_count]
            object_synonyms = synonyms.get(edge['object'], [edge['object']])[:self.synonym_try_count]

            # test each combination until we get a valid NGD result
            ngd_value = self.get_ngd(subject_synonyms, object_synonyms)

            if ngd_value:
                score = ngd_value
                result['attributes'] = [
                    {
                        "original_attribute_name": "Explanation Rationale",
                        "attribute_type_id": "biolink:description",
                        "value": "Score assigned based on Normalized Google Distance (NGD) computed between the two terms using the ARAX SmartAPI endpoint.",
                        "description": "Describes to user the Rationale for explaining the ranking"
                    },
                    {
                        "original_attribute_name": "Explanation Text",
                        "attribute_type_id": "biolink:has_evidence",
                        "value": "This result was given a score corresponding to the Normalized Google Distance (NGD) between the terms.",
                        "description": "Describes to user the reason this specific edge receives a score w.r.t Rationale."
                    }
                ]
            else:
                self.logs.append(clsLogEvent(
                    identifier=self.case_id,
                    level="DEBUG",
                    code="",
                    message=f"NGD failed for subject synonyms: {subject_synonyms} object synonyms: {object_synonyms}"
                ))
                score = 0
                result['attributes'] = [
                    {
                        "original_attribute_name": "Explanation Rationale",
                        "attribute_type_id": "biolink:description",
                        "value": "No explanation as this edge is not scored.",
                        "description": "Describes to user the Rationale for explaining the ranking"
                    },
                    {
                        "original_attribute_name": "Explanation Text",
                        "attribute_type_id": "biolink:has_evidence",
                        "value": "Explanatory Agent is unable to confirm the quality of this result due to a lack of response from the NGD service hosted on the ARAX SmartAPI endpoint.",
                        "description": "Describes to user the reason this specific edge receives a score w.r.t Rationale."
                    }
                ]

            if score == 0:
                score = ZERO_RESULT_SCORE

            result["score"] = score

            results.append(result)

        return results


if __name__ == "__main__":
    x = ExplanationX00014("awesome_kp")
