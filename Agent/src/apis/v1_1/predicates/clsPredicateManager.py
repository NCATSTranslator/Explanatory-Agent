"""
WHAT: A class which generates the user response metadata
WHY: Removes this logic from the view, and puts in a testable class
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-19
"""

from modDatabase import db
from ..metaKnowledgeGraphs.clsMetaKnowledgeGraphManager import clsMetaKnowledgeGraphManager
import json


class clsPredicateManager:
    """
    See header
    """

    # same sql statement as meta_knowledge_graph endpoint
    sqlGenerateUserResponsePredicates = clsMetaKnowledgeGraphManager.sqlGenerateUserResponseMetaKnowledgeGraph

    def __init__(self):
        """
        Constructor
        """
        self.userResponsePredicates = None

    def generateUserResponsePredicates(self):
        """
        Fetch distinct Subject, Object, Predicate results from GlobalSimilarity table and cross reference with CaseSolutions table
        :return: None
        """

        self.userResponsePredicates = {}

        results = db.session.execute(statement=self.sqlGenerateUserResponsePredicates).fetchall()
        if len(results) == 0: return

        userResponsePredicates = {}
        for result in results:
            subject = result['Subject']
            object = result['Object']
            predicate = result['Predicate']
            if subject not in userResponsePredicates:
                userResponsePredicates[subject] = {}
            if object not in userResponsePredicates[subject]:
                userResponsePredicates[subject][object] = []
            userResponsePredicates[subject][object].append(predicate)

        userResponsePredicates = json.loads(json.dumps(userResponsePredicates, sort_keys=True))

        # convert all finalized sets to sorted lists for consistency.
        for subject, objectPredicates in userResponsePredicates.items():
            for object in objectPredicates.keys():
                userResponsePredicates[subject][object] = sorted(list(userResponsePredicates[subject][object]))

        self.userResponsePredicates = userResponsePredicates
