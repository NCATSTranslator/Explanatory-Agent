"""
(FOR every edge:) Assign "The score was obtained based on level of maturity of methods that identify associations." to the value of "attribute_type_id": "biolink:description"

(FOR every edge:) Call function Sol P 3 : Score_by_edge_name() with 5 parameters:

a) Number of EdgeValues: 3
b) Array of EdgeValues Names: ["MAGMA_GENE", "RC_GENES", "INTEGRATED_GENETICS"]
c) Combination Order: ["MAGMA_GENE", "RC_GENES", "INTEGRATED_GENETICS","MAGMA_GENE, RC_GENES","MAGMA_GENE, INTEGRATED_GENETICS", "RC_GENES, INTEGRATED_GENETICS", "MAGMA_GENE, RC_GENES, INTEGRATED_GENETICS"]
d) Array of Explanation Text (7 values):
["Disease-Gene association was identified via  MAGMA_GENE (a standard method for identifying gene-condition associations from variant-level associations using  proximity-based assignments from GWAS data), but was not confirmed by any of the two other methods used, namely, RC_GENES and INTEGRATED_GENETICS. These methods are still  experimental. Considering MAGMA_GENE is a standard method in the field, we still maintain acceptable confidence in these results."
,"Disease-Gene association was identified only by RC_GENES (an experimental method for identifying gene-condition associations using a novel  combination of established methods). Results were not confirmed using the  standard MAGMA_GENE method. RC_GENES is an experimental method, and false positives may be present. For more details see: https://www.biorxiv.org/content/10.1101/2020.06.28.171561v2 For this reason,  we consider these results to be the associations with lowest confidence."
,"Disease-Gene association was identified only by INTEGRATED_GENETICS (an experimental method for identifying  gene-condition associations using a novel combination of established methods).  Results were not confirmed using the standard MAGMA_GENE method.  INTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present. For this reason, we consider these results to be  the associations with lowest confidence."
,"Disease-Gene association was identified via MAGMA_GENE (a  standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data) AND was also identified by RC_GENES (an experimental but highly principled method for identifying gene-condition associations using a novel combination of established methods). RC_GENES is still in development and  undergoing optimization; false-positives may be present. Confirmation of the  association with both available methods from this KP gives us high confidence  in these results."
,"Disease-Gene association was identified via MAGMA_GENE (a standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data) AND was also identified by INTEGRATED_GENETICS (an experimental  method for identifying gene-condition associations using a novel combination of established methods). INTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present. Confirmation of the  association with both available methods from this KP gives us high confidence in these results."
,"Disease-Gene association was identified by RC_GENES and INTEGRATED_GENETICS (both are experimental methods for identifying  gene-condition associations using a novel combination of established methods). Results were not confirmed using the standard MAGMA_GENE method. INTEGRATED_GENETICS and RC_GENES are experimental method, and false positives may be present. For more details see: https://www.biorxiv.org/content/10.1101/2020.06.28.171561v2 For this reason,  we consider these results to be the associations with low confidence."
,"Disease-Gene association was identified via MAGMA_GENE (a  standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data) AND was also identified by RC_GENES (an experimental but highly principled method for identifying gene-condition associations using a novel combination of established methods) AND was also identified by INTEGRATED_GENETICS (an experimental  method for identifying gene-condition associations using a novel combination of established methods).  RC_GENES and INTEGRATED_GENETICS is still in development and  undergoing optimization; false-positives may be present. Confirmation of the  association with all available methods from this KP gives us high confidence in these results."]
e) Array of Explanation Scores: [0.75,0.5,0.25,1.0,1.0,0.6,1]





STEP 1 SCORE BY EDGE
 INPUT: Five parameters:
  1) Number of EdgeValues (N),
  2) Array of EdgeValues name,
  3) Combination Order (CO) ,
  4) Explanation Text for each combination of EdgeValues (ExpText) and
  5) Explanation Scores for each combination of EdgeValues (Score)  

For example: If there are 3 EdgeValues, there would be 23 -1  = 7 combination.
Input parameter example: 
  Param1: 3
   Param2: [EdgeValue1, EdgeValue2, EdgeValue3]
   Param3: [(EdgeValue1), (EdgeValue2), (EdgeValue3), (EdgeValue1, EdgeValue2), (EdgeValue1, EdgeValue3), (EdgeValue2, EdgeValue3), (EdgeValue1, EdgeValue2, EdgeValue3)   
  Param4: [ExpText1, ExpText2, ExpText3, ExpText4, ExpText5, ExpText6, ExpText7]
   Param5: [Score1, Score2, Score3, Score4, Score5, Score6, Score7]

 PROCESS: Based on the edge name values, fill attribute 'value_for_score' and 'biolink:has_evidence' for 2N -1 combination of N number of ordinal EdgeValues. 
Explanation score and Explanation text are assigned based on the Combination Order of EdgeValues.

For example, consider 3 EdgeValues input,  
1) If EdgeValue1 is found in the selected edge name prefix, assign attribute 'value_for_score': Score1 and 'biolink:has_evidence': ExpText1
2) If EdgeValue2 is foun in the selected edge name prefix, assign attribute 'value_for_score': Score2 and 'biolink:has_evidence': ExpText2
 3) If EdgeValue3 is found in the selected edge name prefix, assign attribute 'value_for_score': Score3 and 'biolink:has_evidence': ExpText3
 4) If combination (EdgeValue1, EdgeValue2) are found in the selected edge name prefix, assign attribute 'value_for_score': Score4 and 'biolink:has_evidence': ExpText4
 5) If combination (EdgeValue1, EdgeValue3) are found in the selected edge name prefix, assign attribute 'value_for_score': Score5 and 'biolink:has_evidence': ExpText5 
6) If combination (EdgeValue2, EdgeValue3) are found in the selected edge name prefix, assign attribute 'value_for_score': Score6 and 'biolink:has_evidence': ExpText6 
7) If combination (EdgeValue1, EdgeValue2, EdgeValue3) are found in the selected edge name prefix, assign attribute 'value_for_score': Score7 and 'biolink:has_evidence': ExpText7  

Combination Order, Explanation Text and Explanation Scores  correspond to each other, meaning CombinationOrder1's  explanation text is ExpText1's and has score
  Score1, CombinationOrder2's explanation text is ExpText2's and has score of Score2 and so on.

  ALGORITHM: For each CombinationOrder (COi): 
    If edge name value matches with combination in COi: 
        Assign attributes
        'value_for_score': Scorei and 'biolink:has_evidence': ExpTexti

ASSUMPTIONS: There is always at least one EdgeValue passed as parameter.
 DEPENDENCY: N/A
 OUTPUT:
value_for_score: Scorei (based on the combination of EdgeValues found)
 value of attribute_type_id: "biolink:has_evidence" is filled with explanation texts (ExpTexti) based on the combination of EdgeValues found.
"""

from collections import OrderedDict
from utils.clsLog import clsLogEvent
import logging


class ExplanationX00001:
    def __init__(self, edge_values: set, value_combinations: dict, rationale: str):
        self.case_id = "X00001"
        self.edge_values = edge_values
        self.value_combinations = value_combinations
        self.rationale = rationale
        self.logs = []

    def identify_edge(self, edge_id):
        """
        Match the edge names present in the edge id
        :param edge_id:
        :return:
        """
        found_edge_values = set()

        for edge_value in self.edge_values:
            if edge_value in edge_id.upper():
                found_edge_values.add(edge_value)

        explanation, score = self.value_combinations[frozenset(found_edge_values)]

        return explanation, score


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

            explanation, score = self.identify_edge(edgeId)

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
            result['score'] = score
            result['attributes'] = [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": self.rationale,
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "original_attribute_name": "Explanation Text",
                    "attribute_type_id": "biolink:has_evidence",
                    "value": explanation,
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


if __name__ == "__main__":
    x = ExplanationX00001(
                edge_values={"MAGMA_GENE", "RC_GENES", "INTEGRATED_GENETICS"},
                value_combinations={
                    frozenset(("MAGMA_GENE",)): (
                        "Disease-Gene association was identified via  MAGMA_GENE (a standard method for identifying gene-condition associations from variant-level associations using  proximity-based assignments from GWAS data), but was not confirmed by any of the two other methods used, namely, RC_GENES and INTEGRATED_GENETICS. These methods are still  experimental. Considering MAGMA_GENE is a standard method in the field, we still maintain acceptable confidence in these results.",
                        0.75
                    ),
                    frozenset(("RC_GENES",)): (
                        "Disease-Gene association was identified only by RC_GENES (an experimental method for identifying gene-condition associations using a novel  combination of established methods). Results were not confirmed using the  standard MAGMA_GENE method. RC_GENES is an experimental method, and false positives may be present. For more details see: https://www.biorxiv.org/content/10.1101/2020.06.28.171561v2 For this reason,  we consider these results to be the associations with lowest confidence.",
                        0.5
                    ),
                    frozenset(("INTEGRATED_GENETICS",)): (
                        "Disease-Gene association was identified only by INTEGRATED_GENETICS (an experimental method for identifying  gene-condition associations using a novel combination of established methods).  Results were not confirmed using the standard MAGMA_GENE method.  INTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present. For this reason, we consider these results to be  the associations with lowest confidence.",
                        0.25
                    ),
                    frozenset(("MAGMA_GENE", "RC_GENES")): (
                        "Disease-Gene association was identified via MAGMA_GENE (a  standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data) AND was also identified by RC_GENES (an experimental but highly principled method for identifying gene-condition associations using a novel combination of established methods). RC_GENES is still in development and  undergoing optimization; false-positives may be present. Confirmation of the  association with both available methods from this KP gives us high confidence  in these results.",
                        1.0
                    ),
                    frozenset(("MAGMA_GENE", "INTEGRATED_GENETICS")): (
                        "Disease-Gene association was identified via MAGMA_GENE (a standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data) AND was also identified by INTEGRATED_GENETICS (an experimental  method for identifying gene-condition associations using a novel combination of established methods). INTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present. Confirmation of the  association with both available methods from this KP gives us high confidence in these results.",
                        1.0
                    ),
                    frozenset(("RC_GENES", "INTEGRATED_GENETICS")): (
                        "Disease-Gene association was identified by RC_GENES and INTEGRATED_GENETICS (both are experimental methods for identifying  gene-condition associations using a novel combination of established methods). Results were not confirmed using the standard MAGMA_GENE method. INTEGRATED_GENETICS and RC_GENES are experimental method, and false positives may be present. For more details see: https://www.biorxiv.org/content/10.1101/2020.06.28.171561v2 For this reason,  we consider these results to be the associations with low confidence.",
                        0.6
                    ),
                    frozenset(("MAGMA_GENE", "RC_GENES", "INTEGRATED_GENETICS")): (
                        "Disease-Gene association was identified via MAGMA_GENE (a  standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data) AND was also identified by RC_GENES (an experimental but highly principled method for identifying gene-condition associations using a novel combination of established methods) AND was also identified by INTEGRATED_GENETICS (an experimental  method for identifying gene-condition associations using a novel combination of established methods).  RC_GENES and INTEGRATED_GENETICS is still in development and  undergoing optimization; false-positives may be present. Confirmation of the  association with all available methods from this KP gives us high confidence in these results.",
                        1.0
                    ),
                },
                rationale="The score was obtained based on level of maturity of methods that identify associations."
            )

    results = x.create_results_and_explain({
        "edges": {
            "magma_gene_20210805NCBIGene:23037MONDO:0100096": {"subject": "", "object": ""},
            "RC_GENES_20210805NCBIGene:23037MONDO:0100096": {"subject": "", "object": ""},
            "INTEGRATED_GENETICS_20210805NCBIGene:23037MONDO:0100096": {"subject": "", "object": ""},
            "MAGMA_GENE_rc_genes_20210805NCBIGene:23037MONDO:0100096": {"subject": "", "object": ""},
            "magma_gene_INTEGRATED_genetics20210805NCBIGene:23037MONDO:0100096": {"subject": "", "object": ""},
            "RC_GENES_INTEGRATED_GENETICS_20210805NCBIGene:23037MONDO:0100096": {"subject": "", "object": ""},
            "magma_gene_RC_GENES_INTEGRATED_GENETICS_20210805NCBIGene:23037MONDO:0100096": {"subject": "", "object": ""},
            "magma_gene_2": {"subject": "", "object": ""},
            "magma_gene_3": {"subject": "", "object": ""},
            "magma_gene_4": {"subject": "", "object": ""},
        }
    })

    q = 0