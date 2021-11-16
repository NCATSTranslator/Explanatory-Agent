"""
WHAT: Collection of functions to calculate similarity scores
WHY:
ASSUMES:
FUTURE IMPROVEMENTS:
WHO: YR 2021-08-13
"""

from modDatabase import db
from bmt import Toolkit
import logging

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
            similarity = result[2]

            self.node_similarities[node_pair] = similarity

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
        If the passed nodes exist int the file local_sim_file, the similarity score will be selected from it.
        Else, equalizer will be used.. if node1 == node 2, return 1 else 0
        :param node1: new node
        :param node2: candidate node
        :return: Local similarity between the passed nodes
        """

        node_pair = (node1, node2)
        similarity = self.node_similarities.get(node_pair, None)
        if similarity:
            return similarity
        else:
            # If the node pair is not found in the file, directly compare the nodes
            if node1 == node2:
                return 1
            else:
                return 0

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

    def get_top_global_sim_cases(self, global_similarity, query_threshold, global_precision, max_cases: int):
        """
        Sort Global_Similarity
        return top  caseid's from global_similarity
        """
        # filtered_global_similarities = list(filter(lambda x: (x[1] - query_threshold) > global_precision, global_similarity))
        # Per "RE: 2 ITEMS" email, remove any filter logic.
        filtered_global_similarities = global_similarity
        # sorts by prio then case id BOTH descending!
        # sorted_global_similarity = sorted(filtered_global_similarities, key=lambda x: (float(x[1]), x[0]), reverse=True)
        # sorts prio desc 1st, then case asc
        new_sort = sorted(filtered_global_similarities, key=lambda x: x[0])
        new_sort.sort(key=lambda x: x[1], reverse=True)
        sorted_global_similarity = new_sort

        # Use all cases with the top score. If the second highest score is > 0.9499 include all of those cases as well.
        top_score = sorted_global_similarity[0][1]
        selected_cases = list(filter(lambda x: x[1] == top_score, sorted_global_similarity))

        # get a list of all coses that don't have the top score
        runner_up_sorted_global_similarity = list(filter(lambda x: x[1] != top_score, sorted_global_similarity))
        runner_up_score = runner_up_sorted_global_similarity[0][1]
        if runner_up_score > 0.9499:
            selected_cases += list(filter(lambda x: x[1] == runner_up_score, runner_up_sorted_global_similarity))

        # get top n caseId from sorted list
        self.selected_case_ids_and_similarities = selected_cases[:max_cases]

        return [x[0] for x in self.selected_case_ids_and_similarities]

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
        similarity = self.predicate_similarities.get(predicate_pair, None)
        if similarity:
            return similarity
        else:
            # If the node pair is not found in the file, directly compare the nodes
            if pred1 == pred2:
                return 1
            else:
                return 0

    def get_global_sim_triplets(self, new_subject, new_object, new_predicate, origins):
        """
        :param new_subject:
        :param new_object:
        :param new_predicate:
        :param origins: List of origin types to search on.
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
            config_result = db.session.execute('SELECT "GLOBAL_QUERY_THRESHOLD", "GLOBAL_PRECISION", "MAX_REUSE" FROM public."xARA_Config";').fetchall()[0]
            query_threshold = config_result[0]
            global_precision = config_result[1]
            max_cases = int(config_result[2])
 
        ( SUBJECT_NODE_WEIGHT, OBJECT_NODE_WEIGHT, PREDICATE_WEIGHT ) = weights_results[0]
        weightSum = sum(list(weights_results[0]))
        
        # self.caseProblemsCount = [row[0] for row in len_rows_xARA_caseproblems]
        subject_local_sim=[]
        object_local_sim=[]
        pred_local_sim=[]
        global_similarity=[]
        self.cases = None
        # Selecting cols from tables as list with limit 200, remove limit to get all records from table
        with self.app.app_context():
            # As per "RE: 2 ITEMS", exclude any case problems with matching n0 and n1 categories IFF the new subject and object categories are not the same
            if new_subject != new_object:
                query = 'SELECT "N00_NODE_CATEGORY", "N01_NODE_CATEGORY", "E00_EDGE_PREDICATE", "CASE_ID", "ORIGIN" FROM "xARA_CaseProblems" WHERE "N00_NODE_CATEGORY" != "N01_NODE_CATEGORY" AND "ORIGIN" = ANY(array[:origins]);'
            else:
                query = 'SELECT "N00_NODE_CATEGORY", "N01_NODE_CATEGORY", "E00_EDGE_PREDICATE", "CASE_ID", "ORIGIN" FROM "xARA_CaseProblems" WHERE "ORIGIN" = ANY(array[:origins]);'
            results = db.session.execute(statement=query, params={"origins": list(origins)}).fetchall()

            # Exclude derived results if there are any fromKP results
            has_from_kp = False
            for result in results:
                if result[4] == "fromKP":
                    has_from_kp = True
                    break

            if has_from_kp:
                results = filter(lambda x: x[4] != "derived", results)

            self.cases = list(results)

            # for item in results:
            #     self.candidate_subject.append(item[0])
            #     self.candidate_object.append(item[1])
            #     self.candidate_predicate.append(item[2])
            #     self.candidate_caseId.append(item[3])

        logging.debug(f"Retrieved {len(self.cases)} cases")

        # for i in range(0, len(self.candidate_subject)):
        for case in self.cases:
            candidate_subject = case[0]
            candidate_object = case[1]
            candidate_predicate = case[2]
            candidate_caseId = case[3]

            # Calculate the subject_local_sim for new_subject and all the candidate_subject in col N00_NODE_CATEGORY in xARA_CaseProblems table
            subject_local_sim = direct_compare(new_subject, candidate_subject)

            # Calculate the subject_local_sim for new_object and all the candidate_object in col N01_NODE_CATEGORY in xARA_CaseProblems table
            object_local_sim = self.get_local_sim_score_nodes(new_object, candidate_object)

            # Calculate the subject_local_sim for new_predicate and all the candidate_predicate in col E00_EDGE_PREDICATE in xARA_CaseProblems table
            pred_local_sim = self.get_local_sim_score_preds(new_predicate, candidate_predicate)
          
            calc_global_similarity = ((float(subject_local_sim) * float(SUBJECT_NODE_WEIGHT) + float(object_local_sim)
                                       * float(OBJECT_NODE_WEIGHT) + float(pred_local_sim) * float(PREDICATE_WEIGHT)) / float(weightSum))
            
            # Add case id, calc_global_similarity to global similarity
            global_similarity.append((candidate_caseId, calc_global_similarity))

        logging.debug("Calculated similarity for all cases")

        return self.get_top_global_sim_cases(global_similarity, query_threshold, global_precision, max_cases)

        """
        sample output:
        ['Q000001', 'Q000037', 'Q000039', 'Q000040', 'Q000043', 'Q000045', 
        'Q000046', 'Q000049', 'Q000136', 'Q000116']
        """

    
def direct_compare(new_category, candidate_category):
    if new_category == candidate_category:
        return 1
    else:
        return 0