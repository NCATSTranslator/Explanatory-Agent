from .clsBioLinkSimilarity import clsBiolinkSimilarity
from .clsExplanationMissing import ExplanationMissing
from .clsExplanationNone import ExplanationNone
from .clsExplanationX00001 import ExplanationX00001
from .clsExplanationX00002 import ExplanationX00002
from .clsExplanationX00003 import ExplanationX00003
from .clsExplanationX00004 import ExplanationX00004
from .clsExplanationX00005 import ExplanationX00005
from .clsExplanationX00006 import ExplanationX00006
from .clsExplanationX00007 import ExplanationX00007
from .clsExplanationX00008 import ExplanationX00008
from .clsExplanationX00009 import ExplanationX00009
from .clsExplanationX00010 import ExplanationX00010
from .clsExplanationX00011 import ExplanationX00011
from .clsExplanationX00012 import ExplanationX00012
from .clsExplanationX00013 import ExplanationX00013
from .clsExplanationX00014 import ExplanationX00014
from .clsExplanationX00015 import ExplanationX00015
from .clsExplanationX00016 import ExplanationX00016
from modDatabase import db


class ExplanationSolutionFinder(clsBiolinkSimilarity):
    sqlRetrieveExplanationProblems = \
        """
        SELECT "CASE_ID", "CASE_NAME", "KP_NAME", "SUBJECT_NODE", "OBJECT_NODE", "PREDICATE",
        "SELECTION CRITERION 1", "SELECTION CRITERION 2"
        FROM public."xARA_ExplanationCaseProblems";
        """

    sqlRetrieveExplanationExcludedKPs = \
        """
        SELECT "KP" FROM public."xARA_KP_ExplanationExclusions";
        """

    sqlRetrieveResultWeights = \
        """
        SELECT "XCASE_ID", "SUBJECT_NODE_WEIGHT", "OBJECT_NODE_WEIGHT", "PREDICATE_WEIGHT", "KP_WEIGHT"
        FROM public."xARA_ResultWeights";
        """

    sqlRetrieveGlobalResultThreshold = \
        """
        SELECT "GLOBAL_RESULT_THRESHOLD" FROM public."xARA_Config";
        """

    def __init__(self, _app):
        super().__init__(_app)

        self.explanation_problems = None
        self.cache_explanation_problems()

        self.explanation_excluded_kps = None
        self.cache_explanation_excluded_kps()

        self.explanation_weights = None
        self.cache_explanation_weights()

        self.explanation_similarity_threshold = None
        self.cache_explanation_similarity_threshold()

    def cache_explanation_problems(self):
        """

        :return:
        """
        with self.app.app_context():
            self.explanation_problems = db.session.execute(ExplanationSolutionFinder.sqlRetrieveExplanationProblems).mappings().all()

    def cache_explanation_excluded_kps(self):
        """

        :return:
        """
        self.explanation_excluded_kps = set()
        with self.app.app_context():
            results = db.session.execute(ExplanationSolutionFinder.sqlRetrieveExplanationExcludedKPs).mappings().all()

        for result in results:
            self.explanation_excluded_kps.add(result["KP"])

    def cache_explanation_weights(self):
        """

        :return:
        """
        self.explanation_weights = dict()
        with self.app.app_context():
            results = db.session.execute(ExplanationSolutionFinder.sqlRetrieveResultWeights).mappings().all()

        for result in results:
            # convert the weights from decimal to float
            weights = dict()
            for key in ["SUBJECT_NODE_WEIGHT", "OBJECT_NODE_WEIGHT", "PREDICATE_WEIGHT", "KP_WEIGHT"]:
                value = result[key]
                if value is not None:
                    weights[key] = float(value)
                else:
                    weights[key] = value

            self.explanation_weights[result['XCASE_ID']] = weights

    def cache_explanation_similarity_threshold(self):
        """

        :return:
        """
        self.explanation_similarity_threshold = 1.0
        with self.app.app_context():
            self.explanation_similarity_threshold = float(db.session.execute(ExplanationSolutionFinder.sqlRetrieveGlobalResultThreshold).fetchall()[0][0])

    def string_similarity(self, compared, candidate):
        """
        Compares two strings.
        :param compared:
        :param candidate:
        :return:
        """
        if compared == candidate:
            return 1.0
        else:
            return 0.0

    def search(self, source_subject, source_object, source_predicate, knowledge_graph, kp_name, similarity_threshold=None):
        """
        Get Case solutions based on similarity, identical to biolink similarity logic


        :param query_graph:
        :param knowledge_graph:
        :param kp_name:
        :param similarity_threshold:
        :return:
        """
        if kp_name in self.explanation_excluded_kps:
            return ExplanationX00014(kp_name)

        if len(knowledge_graph["edges"]) <= 0:
            return ExplanationX00014(kp_name)

        new_subject = source_subject[0]
        new_object = source_object[0]
        new_predicate = source_predicate[0]

        explanation_similarities = []

        for explanation_problem in self.explanation_problems:
            weights = self.explanation_weights.get(
                explanation_problem['CASE_ID'],
                {"SUBJECT_NODE_WEIGHT": None, "OBJECT_NODE_WEIGHT": None, "PREDICATE_WEIGHT": None, "KP_WEIGHT": None}
            )

            # currently not implemented due to missing database data
            if explanation_problem['CASE_ID'] == "X00004":
                continue

            # if there are no weights (not just a missing case ID, they can also be nulls in the DB) skip this explanation case
            if weights['SUBJECT_NODE_WEIGHT'] is None and weights['OBJECT_NODE_WEIGHT'] is None and \
                    weights['PREDICATE_WEIGHT'] is None and weights['KP_WEIGHT'] is None:
                continue

            kps = self.string_similarity(kp_name, explanation_problem['KP_NAME'])

            """
            Obtain value for Explanation Predicate Local Similarity, XPS, by performing a lookup in the LocalSimPredicates Table in the xARA_DB to obtain 
            the corresponding similarity score for (NRpredicate, CxCpredicate)
            """
            xps = self.get_local_sim_score_preds(new_predicate, explanation_problem['PREDICATE'])

            """
            2011-11-05 update:
            Obtain Explanation Node Local Similarity, XNLS, 
            XNLS = MAX ( 
                         Average(
                Lookup(NR_subject_node_category, CxC_subject_node_category),   
                Lookup(NR_object_node_category, CxC_object_node_category)
                                        ),  
                        Average(
                Lookup(NR_subject_node_category, CxC_object_node_category),  
                Lookup(NR_object_node_category, CxC_subject_node_category)
                                      )
                         )
            """

            subject_similarity = self.get_local_sim_score_nodes(new_subject, explanation_problem['SUBJECT_NODE'])
            object_similarity = self.get_local_sim_score_nodes(new_object, explanation_problem['OBJECT_NODE'])
            avg_node_similiarity = (subject_similarity + object_similarity) / 2

            subject_x_object_similarity = self.get_local_sim_score_nodes(new_subject, explanation_problem['OBJECT_NODE'])
            object_x_subject_similarity = self.get_local_sim_score_nodes(new_object, explanation_problem['SUBJECT_NODE'])
            avg_x_node_similiarity = (subject_x_object_similarity + object_x_subject_similarity) / 2

            xnls = max(avg_node_similiarity, avg_x_node_similiarity)
            xnls_weight = (weights['SUBJECT_NODE_WEIGHT'] + weights['OBJECT_NODE_WEIGHT']) / 2

            """
            Compute the explanation global edge definition similarity of CxCi (XGESi) as a list: 
              GXSi = (XNLS*w1i + XPS*w2i + KPS*w3i)/SUM(w1i, w2i, w3i)
               Sort GXSi in descending order 
            """
            case_similarity = ((float(kps) * weights['KP_WEIGHT'] +
                                float(xnls) * xnls_weight +
                                float(xps) * weights['PREDICATE_WEIGHT']) /
                               sum((weights['KP_WEIGHT'], xnls_weight, weights['PREDICATE_WEIGHT'])))

            explanation_similarities.append((explanation_problem['CASE_ID'], case_similarity))

        """
        IF there is atleast one GXSi >  GLOBAL_RESULT_THRESHOLD:
            RETURN the CXC with the highest GXS 
        ELSE
            GOTO Sim P 2 STEP 1c1 RESULT SIM FUNCTION ATTRIBUTES
        """
        sorted_explanation_similarities = sorted(explanation_similarities, key=lambda x: x[1], reverse=True)
        top_explanation = sorted_explanation_similarities[0]
        if top_explanation[1] > self.explanation_similarity_threshold:
            return self.retrieve_explanation_solution(top_explanation[0], kp_name)

        """
        For each NR edge e
            For each candidate case CXC attribute a
                Search for a in the list of attributes a in edge e
                    IF all 'a' attributes are found in attributes assoicated with 'e' 
                        Choose Case CXC
                IF no case found applicable to 'e': 
                               Choose CaseX000014
        """
        for explanation_problem in self.explanation_problems:
            soultion_class = self.retrieve_explanation_solution(explanation_problem['CASE_ID'], kp_name)

            # an attribute in the edge needs to be valid, not ALL edges!
            edges_valid = False
            for edge in knowledge_graph["edges"].values():
                edge_valid = soultion_class.edgeAttributeValidate(edge)
                if edge_valid is True:
                    edges_valid = True
                    break

            if edges_valid:
                return soultion_class

        return ExplanationX00014(kp_name)

    def retrieve_explanation_solution(self, case_id, kp_name):
        """
        :param case_id:
        :param kp_name:
        :return class:
        """
        # storing it as lambdas so the dict values don't get computed right away
        case_explanations = {
            "X00001": lambda: ExplanationX00001(
                edge_values={"MAGMA_GENE", "RC_GENES", "INTEGRATED_GENETICS"},
                value_combinations={
                    frozenset(): (
                        "Disease-Gene association could not be determined.",
                        0.0
                    ),
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
            ),
            "X00002": lambda: ExplanationX00002(self.app),
            "X00003": lambda: ExplanationX00003("CMAP:similarity_score", kp_name),
            "X00004": lambda: ExplanationX00004(kp_name),
            "X00005": lambda: ExplanationX00005("ln_ratio", kp_name),
            "X00006": lambda: ExplanationX00006("auc_roc", kp_name),
            "X00007": lambda: ExplanationX00007("biolink:Contribution", kp_name),
            "X00008": lambda: ExplanationX00008("biolink:p_value", kp_name),
            "X00009": lambda: ExplanationX00009(kp_name),
            "X00010": lambda: ExplanationX00010("enrichment_p", kp_name),
            "X00011": lambda: ExplanationX00011(kp_name),
            "X00012": lambda: ExplanationX00012(kp_name),
            "X00013": lambda: ExplanationX00013(kp_name),
            "X00014": lambda: ExplanationX00014(kp_name),
            "X00015": lambda: ExplanationX00015(kp_name),
            "X00016": lambda: ExplanationX00016(kp_name)
        }

        return case_explanations.get(case_id, lambda: ExplanationX00014(kp_name))()
