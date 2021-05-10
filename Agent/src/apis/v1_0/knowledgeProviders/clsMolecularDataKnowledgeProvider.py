"""
WHAT: Queries the Molecular Data Knowledge Provider and returns results.
WHY: todo
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from ..knowledgeProviders.clsKnowledgeProvider import clsKnowledgeProvider


class clsMolecularDataKnowledgeProvider(clsKnowledgeProvider):
    """
    See header
    """

    url = "https://translator.broadinstitute.org/molepro/trapi/v1.0/query"

    def __init__(self, requestBody: dict):
        """
        Constructor
        :param requestBody: TRAPI Message JSON object to send to the Knowledge Provider
        """
        super().__init__(requestBody=requestBody)
