"""
WHAT: A class which represents a view for all query related operations
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: 'Agent' is short for 'Explanatory Autonomous Relay Agent'
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-10
"""

from flask import request
from flask_restx import Resource, Namespace, fields
from apis.v1_0.models.clsQuery import clsQuery
import requests
import json
from werkzeug.exceptions import BadRequest, InternalServerError

namespace = Namespace("query", description="Query Endpoints")

sampleBody = \
{
    "message": {
        "query_graph": {
            "edges": {
                "e00": {
                    "subject": "n00",
                    "object": "n01",
                    "predicate": "biolink:condition_associated_with_gene"
                }
            },
            "nodes": {
                "n00": {
                    "id": "EFO:0000275",
                    "category": "biolink:Disease"
                },
                "n01": {
                    "category": "biolink:Gene"
                }
            }
        }
    }
}

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

knowledgeProviderUrl = "https://translator.broadinstitute.org/genetics_provider/trapi/v1.0/query"


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

        query = clsQuery()

        try:
            userRequestBody = request.json if request.is_json else json.loads(request.data)
        except json.decoder.JSONDecodeError:
            raise BadRequest("Supplied request body does not conform to TRAPI v1.0.0 standard.")
        if not query.userRequestBodyIsValid(userRequestBody):
            raise BadRequest("Supplied request body does not conform to TRAPI v1.0.0 standard.")

        query.applyQueryGraphFromUserRequestBody(userRequestBody)

        if not query.userRequestBodyIsSupported(userRequestBody):
            query.generateEmptyKnowledgeGraph()
            query.generateEmptyResults()
            return query.generateMessage(), 200

        try:
            response = requests.post(url=knowledgeProviderUrl, json=userRequestBody)
            response.raise_for_status()
        except Exception:
            return json.loads(response.text), response.status_code

        del userRequestBody

        try:
            knowledgeProviderResponseBody = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            raise InternalServerError("Knowledge Provider response body does not conform, have they changed their API?")
        if not query.knowledgeProviderResponseBodyIsValid(knowledgeProviderResponseBody):
            raise InternalServerError("Knowledge Provider response body does not conform, have they changed their API?")

        query.applyKnowledgeGraphFromKnowledgeProviderResponseBody(knowledgeProviderResponseBody)
        del knowledgeProviderResponseBody

        query.generateResults()

        response_message = query.generateMessage()

        if not query.userRequestBodyIsValid(response_message):
            raise BadRequest("An error occurred during processing.")

        return response_message, 200
