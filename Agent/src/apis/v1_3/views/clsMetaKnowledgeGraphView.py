"""
WHAT: A class which represents a view for all metadata related operations
WHY: Need an api view
ASSUMES: No user input
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-11
"""

from flask_restx import Resource, Namespace
from ..metaKnowledgeGraphs.clsMetaKnowledgeGraphManager import clsMetaKnowledgeGraphManager
import logging

namespace = Namespace("meta_knowledge_graph", description="Meta Knowledge Graph Endpoints")


@namespace.route("/")
class clsMetaKnowledgeGraphView(Resource):
    """
    See header
    """

    def get(self):
        """
        HTTP GET request
        * Query database to determine supported metadata
        :return: Meta Knowledge Graph view model
        """

        metaKnowledgeGraphManager = clsMetaKnowledgeGraphManager()
        metaKnowledgeGraphManager.generateUserResponseMetaKnowledgeGraph()

        userRequestBodyValidationResults = metaKnowledgeGraphManager.userRequestBodyValidation()
        if not userRequestBodyValidationResults["isValid"]:
            logging.critical(f"Generating invalid MetaKG response:\n{userRequestBodyValidationResults['error']}\n{metaKnowledgeGraphManager.userResponseMetaKnowledgeGraph}")
            metaKnowledgeGraphManager.generateEmptyResponseMetaKnowledgeGraph()
            return metaKnowledgeGraphManager.userResponseMetaKnowledgeGraph, 500

        return metaKnowledgeGraphManager.userResponseMetaKnowledgeGraph, 200
