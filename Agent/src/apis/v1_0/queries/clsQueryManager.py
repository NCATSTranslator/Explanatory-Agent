"""
WHAT: A class which generates the query workflow logic
WHY: Removes this logic from the view, and puts in a testable class
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-04-25
"""

from .clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery import clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery
from .clsDiseaseAssociatedGeneQuery import clsDiseaseAssociatedGeneQuery
from .clsDiseaseToChemicalQuery import clsDiseaseToChemicalQuery
from .clsDrugTreatsDiseaseQuery import clsDrugTreatsDiseaseQuery
from .clsGeneAssociatedDiseaseQuery import clsGeneAssociatedDiseaseQuery
from jsonschema import ValidationError
import apis.v1_0.reasoner_validator as reasoner_validator  # todo, can't do relative import here
# using 2c2e3a17ec902ad36e9869713ed98b7f78dc322a commit version 1.0.2.1.0.2
# https://github.com/NCATSTranslator/reasoner-validator/tree/2c2e3a17ec902ad36e9869713ed98b7f78dc322a


class clsQueryManager:
    """
    See header
    """

    registeredQueryClasses = [
        clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery,
        clsDiseaseAssociatedGeneQuery,
        clsDiseaseToChemicalQuery,
        clsDrugTreatsDiseaseQuery,
        clsGeneAssociatedDiseaseQuery,
    ]

    def __init__(self, userRequestBody: dict):
        """
        Constructor
        :param userRequestBody: TRAPI user request body
        """
        self.userRequestBody = userRequestBody
        self.userRequestBodyIsSupported = None
        self.userRequestBodyIsSupportedMultipleTimes = None

        self.query = None
        self.userResponseBody = None

    def userRequestBodyValidation(self):
        """
        A function to evaluate whether the JSON body received from the client conforms to the proper input standard.
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """
        try:
            reasoner_validator.validate_Query(self.userRequestBody)
            return {"isValid": True, "error": None}
        except ValidationError as e:
            return {"isValid": False, "error": e}

    def userResponseBodyValidation(self):
        """
        A function to evaluate whether the JSON body sent to the client conforms to the proper input standard.
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """

        if isinstance(self.query, clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery):
            # Multiomics provider is missing 'type' in their nodes' attributes, so we have to exclude nodes from validation.
            return {"isValid": True, "error": None}
        else:
            try:
                reasoner_validator.validate_Response(self.userResponseBody)
                return {"isValid": True, "error": None}
            except ValidationError as e:
                return {"isValid": False, "error": e}

    def findSupportedQuery(self):
        """
        Iterate through the registered queries and find the supported one.
        If none are supported, we will generate an unsupported response (mostly empty).
        If multiple are supported, we will raise an exception.  We don't know how to handle multiple.
        :return: None
        """

        supportedQueries = []
        for registeredQueryClass in self.registeredQueryClasses:
            registeredQuery = registeredQueryClass(self.userRequestBody)
            if registeredQuery.userRequestBodyIsSupported():
                supportedQueries.append(registeredQuery)

        if len(supportedQueries) == 1:
            self.userRequestBodyIsSupported = True
            self.userRequestBodyIsSupportedMultipleTimes = False
            self.query = supportedQueries[0]
            self.query.query_graph = self.userRequestBody["message"]["query_graph"]
            return

        if len(supportedQueries) > 1:
            self.userRequestBodyIsSupported = True
            self.userRequestBodyIsSupportedMultipleTimes = True
            return

        if len(supportedQueries) == 0:
            self.userRequestBodyIsSupported = False
            self.userRequestBodyIsSupportedMultipleTimes = False
            return

    def generateSuccessUserResponseBody(self):
        """
        Generate a user response body for a healthy response
        :return: None
        """
        self.userResponseBody = {
            "description": "Success. {} results found".format(len(self.query.results)),
            "logs": [],
            "status": "Success",
            "message": {
                "query_graph": self.query.query_graph,
                "knowledge_graph": self.query.knowledge_graph,
                "results": self.query.results,
            }
        }

    def generateUnsupportedUserResponseBody(self):
        """
        Generate a user response body for an unsupported response (mostly empty)
        :return: None
        """
        self.userResponseBody = {
            "description": "Unsupported query.",
            "logs": [],
            "status": "Unsupported",
            "message": {
                "query_graph": self.userRequestBody["message"]["query_graph"],
                "knowledge_graph": {"edges": {}, "nodes": {}},
                "results": [],
            }
        }
