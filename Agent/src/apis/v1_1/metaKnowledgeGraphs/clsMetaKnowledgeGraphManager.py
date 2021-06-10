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
        select distinct
            g."Subject",
            g."Object",
            g."Predicate"
        from "v1_1_GlobalSimilarity" g
        where g."CaseValue" > 0
        and g."CaseId" in (
            select c."CaseId" from "v1_1_CaseSolutions" c
        )
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

        nodeIds = set()
        for result in results:
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
