"""
WHAT: A class which generates the user response metadata
WHY: Removes this logic from the view, and puts in a testable class
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-11
"""

from modDatabase import db


class clsMetaKnowledgeGraphManager:
    """
    See header
    """

    sqlGenerateUserResponseMetaKnowledgeGraph = \
        """
        SELECT "N00_NODE_CATEGORY" as "Subject", "N01_NODE_CATEGORY" as "Object", "E00_EDGE_PREDICATE" as "Predicate" FROM public."xARA_CaseProblems";
        """

    def __init__(self):
        """
        Constructor
        """
        self.userResponseMetaKnowledgeGraph = None

    def generateUserResponseMetaKnowledgeGraph(self):
        """
        Fetch distinct Subject, Object, Predicate results from GlobalSimilarity table and cross reference with CaseSolutions table
        :return: None
        """

        self.userResponseMetaKnowledgeGraph = {'nodes': {}, 'edges': []}

        results = db.session.execute(statement=self.sqlGenerateUserResponseMetaKnowledgeGraph).fetchall()
        if len(results) == 0: return

        # get all distinct triplets
        seen = set()
        seen_add = seen.add
        deduped_results = [x for x in results if not (x in seen or seen_add(x))]

        nodeIds = set()
        for result in deduped_results:
            self.userResponseMetaKnowledgeGraph['edges'].append({
                "subject": result["Subject"],
                "predicate": result["Predicate"],
                "object": result["Object"],
                "relations": None
            })

            nodeIds.add(result["Subject"])
            nodeIds.add(result["Object"])

        for nodeId in sorted(list(nodeIds)):
            self.userResponseMetaKnowledgeGraph['nodes'][nodeId] = {"id_prefixes": ["ALL"]}
