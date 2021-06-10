"""
WHAT: A class which represents a view for all query related operations
WHY: Need an api view
ASSUMES: 'Agent' is short for 'Explanatory Autonomous Relay Agent'
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-11
"""

from flask import request
from flask_restx import Resource, Namespace, fields
from ..queries.clsQueryManager import clsQueryManager
import requests
import json


namespace = Namespace("query", description="Query Endpoints")

sampleBodyOnePathCaseIdQ000019 = \
    {
        "message": {
            "query_graph": {
                "edges": {
                    "e00": {
                        "subject": "n00",
                        "predicates": [
                            "biolink:correlated_with"
                        ],
                        "object": "n01",
                        "constraints": [
                            {
                                "id": "CHP:PredicateProxy",
                                "name": "Predicate Proxy",
                                "operator": "==",
                                "value": [
                                    "EFO:0000714"
                                ],
                                "unit_id": None,
                                "unit_name": None
                            }
                        ]
                    }
                },
                "nodes": {
                    "n00": {
                        "names": [
                            "Aspirin"
                        ],
                        "constraints": [
                            {
                                "id": "CHP:PredicateProxy",
                                "name": "Predicate Proxy",
                                "operator": "==",
                                "value": [
                                    "EFO:0000714"
                                ],
                                "unit_id": None,
                                "unit_name": None
                            }
                        ]
                    },
                    "n01": {
                        "categories": [
                            "biolink:Gene"
                        ]
                    }
                }
            }
        },
        "log_level": "ERROR"
    }

sampleBodyTwoPathsCaseIdQ000094 = \
    {
        "message": {
            "query_graph": {
                "nodes": {
                    "n00": {
                        "ids": [
                            "PUBCHEM.COMPOUND:2244"
                        ],
                        "categories": [
                            "biolink:ChemicalSubstance"
                        ]
                    },
                    "n01": {
                        "categories": [
                            "biolink:Disease"
                        ]
                    }
                },
                "edges": {
                    "e00": {
                        "subject": "n00",
                        "object": "n01",
                        "predicates": [
                            "biolink:affected_by"
                        ]
                    }
                }
            }
        }
    }

sampleBodyThread0OnePathCaseIdQ000019Thread1TwoPathCaseIdQ000127 = \
    {
        "message": {
            "query_graph": {
                "edges": {
                    "e00": {
                        "subject": "n00",
                        "predicates": [
                            "biolink:correlated_with",
                            "biolink:affected_by"
                        ],
                        "object": "n01",
                        "constraints": [
                            {
                                "id": "CHP:PredicateProxy",
                                "name": "Predicate Proxy",
                                "operator": "==",
                                "value": [
                                    "EFO:0000714"
                                ],
                                "unit_id": None,
                                "unit_name": None
                            }
                        ]
                    }
                },
                "nodes": {
                    "n00": {
                        "names": [
                            "Aspirin"
                        ],
                        "constraints": [
                            {
                                "id": "CHP:PredicateProxy",
                                "name": "Predicate Proxy",
                                "operator": "==",
                                "value": [
                                    "EFO:0000714"
                                ],
                                "unit_id": None,
                                "unit_name": None
                            }
                        ]
                    },
                    "n01": {
                        "categories": [
                            "biolink:Gene"
                        ]
                    }
                }
            }
        },
        "log_level": "ERROR"
    }

sampleBody = sampleBodyThread0OnePathCaseIdQ000019Thread1TwoPathCaseIdQ000127

query_graph = namespace.model(
    name="query_graph",
    model=
    {
        'edges': fields.Raw(example=sampleBody["message"]["query_graph"]["edges"], type=json, required=True),
        'nodes': fields.Raw(example=sampleBody["message"]["query_graph"]["nodes"], type=json, required=True)
    }
)

message = namespace.model(
    name="message",
    model={
        "query_graph": fields.Nested(query_graph, required=True)
    }
)

body = namespace.model(
    name="body",
    model=
    {
        'message': fields.Nested(message, required=True)
    }
)


@namespace.route("/")
class clsQueryView(Resource):
    """
    See header
    """

    @namespace.doc(body=body)
    def post(self):
        """
        HTTP POST request
        * Initializes query model
        * Checks user request body is valid
        * Checks user request body is supported
        * Forwards request body to knowledge provider POST
        * Checks knowledge provider response body is valid
        * Generates results
        * Returns entire query view model back to client
        :return: Query view model
        """

        # initialize query manager class
        queryManager = clsQueryManager()

        # make sure user request body is valid json
        try:
            queryManager.userRequestBody = request.json if request.is_json else json.loads(request.data)
        except json.decoder.JSONDecodeError:
            queryManager.generateEmptyUserResponseBody(status="BadRequest", description="Request contains invalid JSON.")
            return queryManager.userResponseBody, 400

        # make sure user request body is supported by TRAPI standard
        userRequestBodyValidationResults = queryManager.userRequestBodyValidation()
        if not userRequestBodyValidationResults["isValid"]:
            queryManager.generateEmptyUserResponseBody(status="BadRequest", description="Supplied request body does not conform to TRAPI v1.1.0 standard. Error: {}".format(userRequestBodyValidationResults["error"].message))
            return queryManager.userResponseBody, 400

        # make sure user request body only supports 2 nodes and 1 edge
        if not queryManager.userRequestBodyStructureIsSupported:
            queryManager.generateEmptyUserResponseBody(status="Unsupported", description="Unsupported query structure.")
            return queryManager.userResponseBody, 200

        # get curie ids (if applicable)
        try:
            queryManager.getCurieIds()
        except requests.exceptions.RequestException as requestError:
            queryManager.generateEmptyUserResponseBody(status="CurieIdsError", description="An error occurred while accessing a Curie Ids Provider.")
            return queryManager.userResponseBody, 500

        # get categories (if applicable)
        try:
            queryManager.getCategories()
        except requests.exceptions.RequestException as requestError:
            queryManager.generateEmptyUserResponseBody(status="CategoriesError", description="An error occurred while accessing a Categories Provider.")
            return queryManager.userResponseBody, 500

        # find the unique edge predicates to dispatch
        queryManager.extractUniqueEdgePredicates()

        # initialize one case solution manager per edge predicate
        queryManager.createCaseSolutionManagers()

        # solve solution
        try:
            queryManager.execute()
        except requests.exceptions.RequestException as requestError:
            queryManager.generateEmptyUserResponseBody(status="KPError", description="An error occurred while accessing a Knowledge Provider.")
            return queryManager.userResponseBody, 500
        except Exception as error:
            queryManager.generateEmptyUserResponseBody(status="Error", description="An error occurred executing a query, not related to a Knowledge Provider.")
            return queryManager.userResponseBody, 500

        # couldn't find any matching records in the database
        if not queryManager.userRequestBodyHasAtLeastOneSupportedCaseSolutionManager:
            queryManager.generateEmptyUserResponseBody(status="Unsupported", description="No knowledge provider supports query.")
            return queryManager.userResponseBody, 200

        # merge all case solution managers together
        queryManager.mergeCaseSolutionManagers()

        # generate a successful user response body
        queryManager.generateSuccessUserResponseBody()

        # validate our response is supported by the TRAPI standard (not valid should never happen)
        userResponseBodyValidationResults = queryManager.userResponseBodyValidation()
        if not userResponseBodyValidationResults["isValid"]:
            queryManager.generateEmptyUserResponseBody(status="ExitValidationError", description="An error occurred during processing.")
            return queryManager.userResponseBody, 500

        # return results
        return queryManager.userResponseBody, 200
