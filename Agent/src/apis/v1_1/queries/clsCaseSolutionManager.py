"""
WHAT: A class to manage the case solutions(s) found in the database.
WHY: Need to separate concerns.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-12
"""

from modDatabase import db
from .clsCaseSolution import clsCaseSolution
from .clsCaseSolutionPath import clsCaseSolutionPath
from .clsKnowledgeProvider import clsKnowledgeProvider
from utils.multithreading.clsElement import clsElement


class clsCaseSolutionManager(clsElement):
    """
    See header
    """

    sqlFindMostSimilarCase = \
        """
        select
            g."CaseId",
            g."CaseValue"
        from "v1_1_GlobalSimilarity" g
        where g."Subject" in :similarSubjectsVar
        and g."Object" in :similarObjectsVar
        and g."Predicate" in :similarPredicatesVar
        and g."CaseValue" > 0 --make sure we don't have dissimilar
        order by g."CaseValue" desc
        limit 1;
        """

    sqlFindCaseSolution = \
        """
        with CaseSolutionsWithUrls as (
            select
                c.*,
                k1."Url" as "KnowledgeProviderPath1Url",
                null as "KnowledgeProviderPath2Url"
            from "v1_1_CaseSolutions" c
            inner join "v1_1_KnowledgeProviders" k1
                on c."KnowledgeProviderPath1Name" = k1."Name"
            where c."KnowledgeProviderPathCount" = 1
            union all
            select
                c.*,
                k1."Url" as "KnowledgeProviderPath1Url",
                k2."Url" as "KnowledgeProviderPath2Url"
            from "v1_1_CaseSolutions" c
            inner join "v1_1_KnowledgeProviders" k1
                on c."KnowledgeProviderPath1Name" = k1."Name"
            inner join "v1_1_KnowledgeProviders" k2
                on c."KnowledgeProviderPath2Name" = k2."Name"
            where c."KnowledgeProviderPathCount" = 2
        )

        select
            m.*
        from CaseSolutionsWithUrls m
        where m."CaseId" = :caseIdVar
        order by m."Id" asc
        limit 1;
        """

    def __init__(self, dispatchId: int, dispatchDescription: str, userRequestBody: dict):
        """
        Constructor
        :param userRequestBody: the request body the user sends
        """

        super().__init__(dispatchId=dispatchId, dispatchDescription=dispatchDescription)
        self.userRequestBody = userRequestBody

        self.similarSubjects = None
        self.similarObjects = None
        self.similarPredicates = None

        self.subjectCurieIds = None
        self.objectCurieIds = None

        self.edgeConstraints = None
        self.subjectConstraints = None
        self.objectConstraints = None

        self.caseId = None
        self.caseValue = None
        self.caseSolution = None  # in the future this will be multiple

        # outputs
        self.query_graph = None
        self.knowledge_graph = None
        self.results = None

        self.logs = None

        # pass current_app._get_current_object() as reference inside threading
        self.app = None

    def extractMetadataFromUserRequestBody(self):

        # extract edge metadata
        edges = self.userRequestBody['message']['query_graph']['edges']
        edge = edges[list(edges.keys())[0]]

        self.similarPredicates = edge['predicates']
        if 'constraints' in edge:
            self.edgeConstraints = edge['constraints']

        # extract nodes metadata
        nodes = self.userRequestBody['message']['query_graph']['nodes']
        subjectNode = nodes[edge['subject']]
        objectNode = nodes[edge['object']]

        self.similarSubjects = subjectNode['categories']
        self.similarObjects = objectNode['categories']

        if 'ids' in subjectNode:
            self.subjectCurieIds = subjectNode['ids']
        if 'ids' in objectNode:
            self.objectCurieIds = objectNode['ids']

        if 'constraints' in subjectNode:
            self.subjectConstraints = subjectNode['constraints']
        if 'constraints' in objectNode:
            self.objectConstraints = objectNode['constraints']

    def findMostSimilarCase(self):

        with self.app.app_context():
            result = db.session.execute(
                statement=self.sqlFindMostSimilarCase,
                params={
                    "similarSubjectsVar": tuple(self.similarSubjects),
                    "similarObjectsVar": tuple(self.similarObjects),
                    "similarPredicatesVar": tuple(self.similarPredicates)
                }
            ).fetchone()
        if result is None: return
        self.caseId = result["CaseId"]
        self.caseValue = result["CaseValue"]

    def findCaseSolution(self):

        if self.caseId is None: return
        with self.app.app_context():
            result = db.session.execute(
                statement=self.sqlFindCaseSolution,
                params={
                    "caseIdVar": self.caseId
                }
            ).fetchone()
        if result is None: return

        knowledgeProviderPathCount = result["KnowledgeProviderPathCount"]
        if knowledgeProviderPathCount not in [1, 2]:
            raise AttributeError("Number of knowledge provider paths supported is either 1 or 2")

        self.caseSolution = clsCaseSolution()
        self.caseSolution.dispatchIdSuffix = "" if self.dispatchId == 0 else ("-" + str(self.dispatchId))
        self.caseSolution.logs = self.logs
        self.caseSolution.id = result["Id"]
        self.caseSolution.similarPredicates = self.similarPredicates
        self.caseSolution.subjectCurieIds = self.subjectCurieIds
        self.caseSolution.objectCurieIds = self.objectCurieIds
        self.caseSolution.subjectConstraints = self.subjectConstraints
        self.caseSolution.objectConstraints = self.objectConstraints

        caseSolutionPath1 = clsCaseSolutionPath()
        caseSolutionPath1.logs = self.logs
        caseSolutionPath1.subject = result["Node1Path1Category"]
        caseSolutionPath1.object = result["Node2Path1Category"]
        caseSolutionPath1.predicate = result["Edge1Path1Predicate"]
        caseSolutionPath1.knowledgeProvider = clsKnowledgeProvider(
            name=result["KnowledgeProviderPath1Name"],
            url=result["KnowledgeProviderPath1Url"]
        )
        caseSolutionPath1.knowledgeProvider.logs = self.logs

        self.caseSolution.paths = [caseSolutionPath1]

        if knowledgeProviderPathCount == 1: return

        caseSolutionPath2 = clsCaseSolutionPath()
        caseSolutionPath2.logs = self.logs
        caseSolutionPath2.subject = result["Node1Path2Category"]
        caseSolutionPath2.object = result["Node2Path2Category"]
        caseSolutionPath2.predicate = result["Edge1Path2Predicate"]
        caseSolutionPath2.knowledgeProvider = clsKnowledgeProvider(
            name=result["KnowledgeProviderPath2Name"],
            url=result["KnowledgeProviderPath2Url"]
        )
        caseSolutionPath2.knowledgeProvider.logs = self.logs

        self.caseSolution.paths.append(caseSolutionPath2)

    def execute(self):

        self.extractMetadataFromUserRequestBody()
        self.findMostSimilarCase()
        self.findCaseSolution()
        if self.caseSolution is None: return
        self.caseSolution.solve()
        self.query_graph = self.caseSolution.query_graph
        self.knowledge_graph = self.caseSolution.knowledge_graph
        self.results = self.caseSolution.results
