"""
WHAT: Queries the Genetics Provider and returns results.
WHY: Genetics Provider provides data such as genes associated with a disease, which is used in some of the Agent's cases.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from ..knowledgeProviders.clsKnowledgeProvider import clsKnowledgeProvider


class clsGeneticsKnowledgeProvider(clsKnowledgeProvider):
    """
    See header
    """

    url = "https://translator.broadinstitute.org/genetics_provider/trapi/v1.0/query"

    def __init__(self, requestBody: dict):
        """
        Constructor
        :param requestBody: TRAPI Message JSON object to send to the Genetics Provider
        """
        super().__init__(requestBody=requestBody)
