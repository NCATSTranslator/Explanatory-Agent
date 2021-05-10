"""
WHAT: A class which represents a view for all query related operations
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: 'Agent' is short for 'Explanatory Autonomous Relay Agent'
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-10
"""

from flask import request
from flask_restx import Resource, Namespace, fields
from ..queries.clsQueryManager import clsQueryManager
import requests
import json
from werkzeug.exceptions import BadRequest, InternalServerError

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
                        "ids": [
                            "PUBCHEM.COMPOUND:2244"
                        ],
                        "categories": [
                            "biolink:ChemicalSubstance"
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
                            "PUBCHEM.COMPOUND:2244",
                        ],
                        "categories": [
                            "biolink:ChemicalSubstance"
                        ],
                    },
                    "n01": {
                        "categories": [
                            "biolink:Disease"
                        ],
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

sampleBody = sampleBodyOnePathCaseIdQ000019

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

        try:
            userRequestBody = request.json if request.is_json else json.loads(request.data)
        except json.decoder.JSONDecodeError:
            raise BadRequest("Request contains invalid JSON.")

        queryManager = clsQueryManager(userRequestBody=userRequestBody)
        userRequestBodyValidationResults = queryManager.userRequestBodyValidation()
        if not userRequestBodyValidationResults["isValid"]:
            raise BadRequest("Supplied request body does not conform to TRAPI v1.1.0 standard. Error: {}".format(userRequestBodyValidationResults["error"].message))

        # only support 2 nodes and 1 edge
        if not queryManager.userRequestBodyStructureIsSupported:
            queryManager.generateUnsupportedStructureUserResponseBody()
            return queryManager.userResponseBody, 200

        queryManager.findSupportedCaseSolution()

        # couldn't find any matching records in the database
        if not queryManager.userRequestBodyCaseIsSupported:
            queryManager.generateUnsupportedCaseUserResponseBody()
            return queryManager.userResponseBody, 200

        # if queryManager.userRequestBodyIsSupportedMultipleTimes:
        #     raise InternalServerError("Multiple query workflows found")

        try:
            queryManager.caseSolutionManager.execute()
        except requests.exceptions.HTTPError as httpError:
            raise InternalServerError("An error occurred while accessing a Knowledge Provider.")
        except Exception as e:
            raise InternalServerError("An error occurred executing a query, not related to a Knowledge Provider.")

        queryManager.generateSuccessUserResponseBody()

        userResponseBodyValidationResults = queryManager.userResponseBodyValidation()
        # if not userResponseBodyValidationResults["isValid"]:
        #     raise InternalServerError("An error occurred during processing.")

        return queryManager.userResponseBody, 200
