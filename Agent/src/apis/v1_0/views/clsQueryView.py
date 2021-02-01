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
from apis.v1_0.views.clsDiseaseAssociatedGeneView import DiseaseAssociatedGeneView
from apis.v1_0.views.clsGeneAssociatedDiseaseView import GeneAssociatedDiseaseView
from apis.v1_0.views.clsDrugTreatsDiseaseView import DrugTreatsDiseaseView
from apis.v1_0.views.clsDiseaseAssociatedGeneContributesChemicalSubstanceView import DiseaseAssociatedGeneContributesChemicalSubstanceView
from apis.v1_0.views.clsDiseaseToChemicalView import DiseaseToChemicalView
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


@namespace.route("/")
class clsQueryView(Resource):
    """
    See header
    """

    registered_query_views = [DiseaseAssociatedGeneView, GeneAssociatedDiseaseView, DrugTreatsDiseaseView, DiseaseAssociatedGeneContributesChemicalSubstanceView,
                              DiseaseToChemicalView]
    KP_ERROR_RESPONSE = "An error occurred while accessing a Knowledge Provider."

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
            raise BadRequest("Request contains invalid JSON.")
        trapi_validation = query.userRequestBodyValidate(userRequestBody)
        if trapi_validation is not None:
            raise BadRequest("Supplied request body does not conform to TRAPI v1.0.0 standard. Error: {}".format(trapi_validation.message,))

        query.applyQueryGraphFromUserRequestBody(userRequestBody)

        matched_views = set()
        for view in clsQueryView.registered_query_views:
            view_instance = view(query)
            if view_instance.supports_query(userRequestBody):
                matched_views.add(view_instance)

        # TODO: Logic for deciding which view to select if multiples are supported? For now this shouldn't happen, because we don't have any overlapping views.
        if len(matched_views) > 0:
            selected_view_instance = sorted(list(matched_views))[0]

            try:
                workflow = selected_view_instance
                workflow.run()
            except requests.exceptions.HTTPError as http_error:
                raise InternalServerError(clsQueryView.KP_ERROR_RESPONSE)
            except Exception as e:
                raise InternalServerError("Internal server error")
        else:
            query.generateEmptyKnowledgeGraph()
            query.generateEmptyResults()
            return query.generateTRAPIUnsupportedResponse(), 200

        response_message = query.generateTRAPISuccessResponse()

        # Multiomics provider does not provide valid knowledge graph nodes, so we have to forgo trapi response checking
        if not query.userResponseBodyIsValid(response_message) and not isinstance(selected_view_instance, DiseaseAssociatedGeneContributesChemicalSubstanceView):
            raise BadRequest("An error occurred during processing.")

        return response_message, 200
