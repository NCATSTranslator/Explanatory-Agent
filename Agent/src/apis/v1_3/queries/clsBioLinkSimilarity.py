"""
WHAT: Collection of functions to calculate similarity scores
WHY:
ASSUMES:
FUTURE IMPROVEMENTS:
WHO: YR 2021-08-13
"""

from modDatabase import db
from .clsKnowledgeType import clsKnowledgeType
from bmt import Toolkit
import logging
from time import time
import pandas as pd
import numpy as np
import os
from typing import List

# t = Toolkit()


class clsBiolinkSimilarity:
    """
    See header
    """
    sqlGenerateSimilarityScore = \
        """
        select
            x."Similarity_score"
            from "xARA_LocalSimNodes" x
            where
            x."Node_1"=:node1
            and x."Node_2"=:node2
        """

    sqlGetAllNodeSimilarityScore = \
        """
        select
            x."NEW_CASE_NODE",
            x."CANDIDATE_CASE_NODE",
            x."SIMILARITY_SCORE"
            from "xARA_LocalSimNodes" x
        """

    sqlGetAllPredicateSimilarityScore = \
        """
        select
            x."NEW_CASE_PREDICATE",
            x."CANDIDATE_CASE_PREDICATE",
            x."SIMILARITY_SCORE"
            from "xARA_LocalSimPredicates" x
        """

    timeoutSeconds = 60

    def __init__(self, _app):
        """
        Constructor
        :param _app: Flask application context, used to send requests to the database.
        """
        self.app = _app

        self.node_similarities = None
        self.predicate_similarities = None

        self.logs = None

        self.cache_node_similarity()
        self.cache_predicate_similarity()

        self.allow_list: List[str] | None = None
        self.deny_list: List[str] | None = None

        self.second_highest_max_reuse = 20  # to be updated from xARA_Config table

        # read pickled case problems from project's root folder
        pkl_path = os.path.join(os.getcwd(), 'case_problems.pkl')
        try:
            self.case_problems_df = pd.read_pickle(pkl_path)
        except FileNotFoundError:
            self.case_problems_df = None

    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls, None)
        return cls._instance

    def cache_node_similarity(self):
        """
        Retrieves all rows from "xARA_LocalSimNodes" table and stores in-memory for faster access. This data is used for every request thousands of times,
        so hitting a DB is inefficient.

        Generates a dictionary of node pairs as keys (node1, node2) and their similarity as the value.
        :return: None
        """
        with self.app.app_context():
            sim_score_results = db.session.execute(statement=self.sqlGetAllNodeSimilarityScore).fetchall()
        self.node_similarities = {}

        for result in sim_score_results:
            node_pair = (result[0], result[1])
            node_pair_inverse = (result[1], result[0])
            similarity = result[2]

            self.node_similarities[node_pair] = similarity
            self.node_similarities[node_pair_inverse] = similarity

    def cache_predicate_similarity(self):
        """
        Retrieves all rows from "xARA_LocalSimPredicates" table and stores in-memory for faster access. This data is used for every request thousands of times,
        so hitting a DB is inefficient.

        Generates a dictionary of predicate pairs as keys (predicate1, predicate2) and their similarity as the value.
        :return: None
        """
        with self.app.app_context():
            sim_score_results = db.session.execute(statement=self.sqlGetAllPredicateSimilarityScore).fetchall()
        self.predicate_similarities = {}

        for result in sim_score_results:
            predicate_pair = (result[0], result[1])
            similarity = result[2]

            self.predicate_similarities[predicate_pair] = similarity

    def get_local_sim_score_nodes(self, node1, node2):
        """
        This function calculates the local similarity between the nodes
        If the passed nodes exist in the file local_sim_file, the similarity score will be selected from it.
        Else, equalizer will be used.. if node1 == node 2, return 1 else 0
        :param node1: new node
        :param node2: candidate node
        :return: Local similarity between the passed nodes
        """

        node_pair = (node1, node2)
        # If the node pair is not found in the file, directly compare the nodes
        score = self.node_similarities.get(node_pair, int(node1 == node2))

        # As per "still pruning responses" on 2022-02-07 4:38 pm if score is 0, set to -20
        if score == 0:
            score = -20

        return score

    def get_ancestors(self, pred1: str, level=0, hier=[]):
        if pred1 == 'None':
                return hier, level
        else:
            element = t.get_element(pred1)
            parent = str(element.is_a)
            hier.append(parent)
            return self.get_ancestors(parent, level=level + 1, hier=hier)

    def get_hier_predicates(self, pred1: str, pred2: str):
        """
            Checks the hier of predicates based on passed parameters
            :param  pred1: New Predicate
                    pred2: Candidate Predicate
            :return: Tuple of 2 elements. First is level of #1 Predicate and Second if of #2
                    Returns None, None if either one is not a predicate
        """
        pred1 = pred1.replace('_', ' ')
        pred2 = pred2.replace('_', ' ')

        if not t.is_predicate(pred1):
            return 'Not Predicate'
        if not t.is_predicate(pred2):
            return 'Not Predicate'

        pred1_ancestors = self.get_ancestors(pred1, hier=[])
        pred2_ancestors = self.get_ancestors(pred2, hier=[])

        pred1_level = pred1_ancestors[1]
        pred2_level = pred2_ancestors[1]

        if pred1_level < pred2_level:
            # Curated to remove "biolink:" string
            c_pred1 = pred1.split(":", 1)[1]

            # Checking if pred1 is ancestor of pred2
            if c_pred1 in pred2_ancestors[0]:
                return pred1_level, pred2_level
            else:
                return 99999, 99999  # Arbitrary large number since they are not in the same tree

        elif pred2_level == pred1_level:
            # Checking if both are same predicates
            if pred1 == pred2:
                return 0, 0
            else:
                return 99999, 99999  # Arbitrary large number since they are not in the same tree
        else:
            return 99999, 99999  # Arbitrary large number since they are not in the same tree

    def get_top_global_sim_cases(self, global_similarity: pd.DataFrame, query_threshold, global_precision, max_cases: int, knowledge_type: str, max_similarity_lt: float = None):
        """
        Sort Global_Similarity
        return top  caseid's from global_similarity
        """
        all_sorted_global_similarity = global_similarity.sort_values(['global_sim', 'CASE_ID'], ascending=[False, True])

        # Step Sim P1a3
        # Keep all cases above or equal to query_threshold
        sorted_global_similarity = all_sorted_global_similarity[all_sorted_global_similarity["global_sim"] >= query_threshold]
        if max_similarity_lt:
            sorted_global_similarity = sorted_global_similarity[sorted_global_similarity["global_sim"] < max_similarity_lt]

        # if all cases (or all but one) have been filtered, then we can return immediately. The next logic operates assuming 2+ cases are present.
        if len(sorted_global_similarity) <= 1:
            selected_cases = sorted_global_similarity
        else:
            # if executing Regular Mode:
            if knowledge_type == clsKnowledgeType.LOOKUP:
                # Execute all solutions from all cases with GSS at the first highest score greater than the REGULAR_GLOBAL_QUERY_THRESHOLD
                top_score = sorted_global_similarity['global_sim'].unique()[0]
                selected_cases = sorted_global_similarity[sorted_global_similarity['global_sim'] == top_score]
            # if executing Creative Mode:
            elif knowledge_type == clsKnowledgeType.CREATIVE_MODE:
                # IF the second highest GSS in the list is above 0.9499
                # THEN execute all solutions from all cases with GSS at the first and second highest similarity scores except for those with GSS=1 
                # ELSE execute all solutions from all cases with GSS at the first highest score greater than the CREATIVE_GLOBAL_QUERY_THRESHOLD except for those with GSS=1

                # Use all cases with the top score. If the second highest score is > 0.9499 include all of those cases as well.
                top_two_scores = sorted_global_similarity['global_sim'].unique()[:2]

                top_score = top_two_scores[0]

                # if only one score was viable, set the runner up score to -1 so that logic won't be triggered
                if len(top_two_scores) == 1:
                    runner_up_score = -1
                else:
                    runner_up_score = top_two_scores[1]

                selected_cases = sorted_global_similarity[sorted_global_similarity['global_sim'] == top_score]
                if runner_up_score > 0.9499:
                    runner_up_selected_cases = sorted_global_similarity[sorted_global_similarity['global_sim'] == runner_up_score].head(self.second_highest_max_reuse)
                    selected_cases = pd.concat((selected_cases, runner_up_selected_cases))
            # otherwise we're in a mode that isnt regular or creative? That's bad
            else:
                raise NotImplementedError

        # return top n caseId from sorted list, based on the knowledge type
        self.selected_case_ids_and_similarities = list(selected_cases.iloc[:max_cases][['CASE_ID', 'global_sim']].to_records(index=False))

        final_cases = [x[0] for x in self.selected_case_ids_and_similarities]
        return final_cases

    def get_local_sim_score_preds(self, pred1, pred2):
        """
        This function uses check_predicate_hier to get the distance between different predicates, and local similarity is
        calculated.
        local similarity = ( 1 / (distance between preds + 1) ) -> Further the distance, lesser the similarity
        :param pred1: new predicate
        :param pred2: Candidate predicate
        :return: Local similarity between the predicates
        """

        if pred1 == "ANY" or pred2 == "ANY":
            return 1

        predicate_pair = (pred1, pred2)
        # If the node pair is not found in the file, directly compare the nodes
        score = self.predicate_similarities.get(predicate_pair, int(pred1 == pred2))

        # Removed as per Slack conversation on 2023-02-15
        # As per "still pruning responses" on 2022-02-07 4:38 pm if score is 0, set to -20
        # if score == 0:
        #     score = -20

        return score

    def fetch_cases_from_db(self, origins, exclude_matching_n0_n1):
        logging.debug('Fetching cases FROM DB!!!')
        with self.app.app_context():
            if exclude_matching_n0_n1:
                query = 'SELECT "N00_NODE_CATEGORY", "N01_NODE_CATEGORY", "E00_EDGE_PREDICATE", "CASE_ID", "ORIGIN" FROM "xARA_CaseProblems" WHERE "N00_NODE_CATEGORY" != "N01_NODE_CATEGORY" AND "ORIGIN" = ANY(array[:origins]);'
            else:
                query = 'SELECT "N00_NODE_CATEGORY", "N01_NODE_CATEGORY", "E00_EDGE_PREDICATE", "CASE_ID", "ORIGIN" FROM "xARA_CaseProblems" WHERE "ORIGIN" = ANY(array[:origins]);'
            data = db.session.execute(statement=query, params={"origins": list(origins)}).fetchall()
            return pd.DataFrame(data=data, columns=["N00_NODE_CATEGORY", "N01_NODE_CATEGORY", "E00_EDGE_PREDICATE", "CASE_ID", "ORIGIN"])

    def fetch_cases_from_df(self, origins, exclude_matching_n0_n1):
        logging.debug('Fetching cases FROM DF!!!')
        df1 = self.case_problems_df[self.case_problems_df.ORIGIN.isin(origins)]
        if exclude_matching_n0_n1:
            df1 = df1[df1.N00_NODE_CATEGORY != df1.N01_NODE_CATEGORY]
        return df1

    def fetch_cases(self, origins, exclude_matching_n0_n1):
        return self.fetch_cases_from_db(origins, exclude_matching_n0_n1)

    def get_global_sim_triplets(self, new_subject, new_object, new_predicate, origins, knowledge_type: str, max_similarity_lt: float = None):
        """
        :param new_subject:
        :param new_object:
        :param new_predicate:
        :param origins: List of origin types to search on.
        :param knowledge_type: "Creative mode" flag. Will use a different query threshold and max cases based on the value
        :param max_similarity_lt: If the maximum similarity in get_top_global_sim_cases should be less than a value
        :return:
        """

        self.caseProblemsCount = None
        self.candidate_subject = []
        self.candidate_object = []
        self.candidate_predicate = []
        self.candidate_caseId = []

        # Get all xARA_caseproblems data
        with self.app.app_context():
            # len_rows_xARA_caseproblems = db.session.execute('SELECT COUNT("CASE_ID") FROM "xARA_CaseProblems";').fetchall()
            weights_results = db.session.execute('SELECT * FROM "xARA_QueryWeights";').fetchall()
            config_query = clsKnowledgeType.config_query(knowledge_type=knowledge_type)
            config_result = db.session.execute(config_query).fetchall()[0]
            query_threshold = config_result[0]
            global_precision = config_result[1]
            max_cases = int(config_result[2])
            self.second_highest_max_reuse = int(config_result[3])

        SUBJECT_NODE_WEIGHT, OBJECT_NODE_WEIGHT, PREDICATE_WEIGHT = weights_results[0]
        weightSum = sum(list(weights_results[0]))

        start = time()
        # As per "RE: 2 ITEMS", exclude any case problems with matching n0 and n1 categories IFF the new subject and object categories are not the same
        # As per discussion on 2-14-2023, we can remove the limitation of exact matches for n00 categories
        cases = self.fetch_cases(origins, exclude_matching_n0_n1=(new_subject != new_object))
        logging.debug(f"Fetched {len(cases)} cases in {time() - start}")

        start = time()
        cases['subject_local_sim'] = cases['N00_NODE_CATEGORY'].map(lambda x: self.get_local_sim_score_nodes(new_subject, x))
        cases['object_local_sim'] = cases['N01_NODE_CATEGORY'].map(lambda x: self.get_local_sim_score_nodes(new_object, x))
        cases['pred_local_sim'] = cases['E00_EDGE_PREDICATE'].map(lambda x: self.get_local_sim_score_preds(new_predicate, x))
        cases['global_sim'] = ((cases['subject_local_sim'] * float(SUBJECT_NODE_WEIGHT) + cases['object_local_sim']
                                * float(OBJECT_NODE_WEIGHT) + cases['pred_local_sim'] * float(PREDICATE_WEIGHT)) / float(weightSum))
        logging.debug(f'Calculated global similarity in {time() - start}')

        return self.get_top_global_sim_cases(cases, query_threshold, global_precision, max_cases, knowledge_type=knowledge_type, max_similarity_lt=max_similarity_lt)


def direct_compare(new_category, candidate_category):
    return int(new_category == candidate_category)
