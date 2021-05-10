from modDatabase import db
from .clsCaseSolution import clsCaseSolution
from .clsCaseSolutionPath import clsCaseSolutionPath
from .clsKnowledgeProvider import clsKnowledgeProvider


class clsCaseSolutionManager:

    def __init__(self, userRequestBody: dict):

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

        sql = \
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

        result = db.session.execute(
            statement=sql,
            params={
                "similarSubjectsVar": tuple(self.similarSubjects),
                "similarObjectsVar": tuple(self.similarObjects),
                "similarPredicatesVar": tuple(self.similarPredicates)
            }
        ).fetchone()
        if result is None: return
        columns = list(result.keys())
        self.caseId = result[columns.index("CaseId")]
        self.caseValue = result[columns.index("CaseValue")]

    def findCaseSolution(self):

        if self.caseId is None: return

        sql = \
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

        result = db.session.execute(statement=sql, params={"caseIdVar": self.caseId}).fetchone()
        if result is None: return
        columns = list(result.keys())

        knowledgeProviderPathCount = result[columns.index("KnowledgeProviderPathCount")]
        if knowledgeProviderPathCount not in [1, 2]:
            raise AttributeError("Number of knowledge provider paths supported is either 1 or 2")

        self.caseSolution = clsCaseSolution()
        self.caseSolution.id = result[columns.index("Id")]
        self.caseSolution.similarPredicates = self.similarPredicates
        self.caseSolution.subjectCurieIds = self.subjectCurieIds
        self.caseSolution.objectCurieIds = self.objectCurieIds
        self.caseSolution.subjectConstraints = self.subjectConstraints
        self.caseSolution.objectConstraints = self.objectConstraints

        caseSolutionPath1 = clsCaseSolutionPath()
        caseSolutionPath1.subject = result[columns.index("Node1Path1Category")]
        caseSolutionPath1.object = result[columns.index("Node2Path1Category")]
        caseSolutionPath1.predicate = result[columns.index("Edge1Path1Predicate")]
        caseSolutionPath1.knowledgeProvider = clsKnowledgeProvider(
            name=result[columns.index("KnowledgeProviderPath1Name")],
            url=result[columns.index("KnowledgeProviderPath1Url")]
        )

        self.caseSolution.paths = [caseSolutionPath1]

        if knowledgeProviderPathCount == 1: return

        caseSolutionPath2 = clsCaseSolutionPath()
        caseSolutionPath2.subject = result[columns.index("Node1Path2Category")]
        caseSolutionPath2.object = result[columns.index("Node2Path2Category")]
        caseSolutionPath2.predicate = result[columns.index("Edge1Path2Predicate")]
        caseSolutionPath2.knowledgeProvider = clsKnowledgeProvider(
            name=result[columns.index("KnowledgeProviderPath2Name")],
            url=result[columns.index("KnowledgeProviderPath2Url")]
        )

        self.caseSolution.paths.append(caseSolutionPath2)

    def execute(self):

        self.caseSolution.solve()
        self.query_graph = self.caseSolution.query_graph
        self.knowledge_graph = self.caseSolution.knowledge_graph
        self.results = self.caseSolution.results
