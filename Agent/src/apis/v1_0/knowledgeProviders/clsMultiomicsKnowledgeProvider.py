"""
WHAT: Queries the Multiomics Provider and returns results.
WHY: todo
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from ..knowledgeProviders.clsKnowledgeProvider import clsKnowledgeProvider


class clsMultiomicsKnowledgeProvider(clsKnowledgeProvider):
    """
    See header
    """

    url = "https://api.bte.ncats.io/v1/smartapi/adf20dd6ff23dfe18e8e012bde686e31/query"

    def __init__(self, requestBody: dict):
        """
        Constructor
        :param requestBody: TRAPI Message JSON object to send to the Multiomics Provider
        """
        super().__init__(requestBody=requestBody)
