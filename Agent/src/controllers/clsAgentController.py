"""
WHAT: A class which represents a controller for all agent related operations
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: 'clsAgent' is short for 'Explanatory Autonomous Relay clsAgent'
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-10
"""

from flask import request
from flask_restx import Resource, Namespace, fields
from models.clsAgent import clsAgent
import requests
import json
from werkzeug.exceptions import BadRequest, InternalServerError

namespace = Namespace("agent", description="Agent Endpoints")

sampleBody = \
{
    "message": {
        "query_graph": {
            "edges": [
                {
                    "id": "e00",
                    "source_id": "n00",
                    "target_id": "n01",
                    "type": "associated"
                }
            ],
            "nodes": [
                {
                    "curie": "EFO:0004465",
                    "id": "n00",
                    "type": "disease"
                },
                {
                    "id": "n01",
                    "type": "gene"
                }
            ]
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

knowledgeProviderUrl = "https://translator.broadinstitute.org/genetics_data_provider/query"

@namespace.route("/")
class AgentController(Resource):
    """
    See header
    """

    @namespace.doc(body=body)
    def post(self):
        """
        HTTP POST request
        * Initializes agent model
        * Checks user request body is valid
        * Forwards request body to knowledge provider POST
        * Checks knowledge provider response body is valid
        * Generates results
        * Returns entire agent view model back to client
        :return: Agent view model
        """

        agent = clsAgent()

        try:
            userRequestBody = request.json if request.is_json else json.loads(request.data)
        except json.decoder.JSONDecodeError:
            raise BadRequest("Supplied request body does not conform")
        if not agent.userRequestBodyIsValid(userRequestBody):
            raise BadRequest("Supplied request body does not conform")

        agent.applyQueryGraphFromUserRequestBody(userRequestBody)

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
        if not agent.knowledgeProviderResponseBodyIsValid(knowledgeProviderResponseBody):
            raise InternalServerError("Knowledge Provider response body does not conform, have they changed their API?")

        agent.applyKnowledgeGraphFromKnowledgeProviderResponseBody(knowledgeProviderResponseBody)
        del knowledgeProviderResponseBody

        agent.generateResults()

        return vars(agent), 200
