"""
todo
"""

from flask_restx import Resource, Namespace
from ..metaKnowledgeGraphs.clsMetaKnowledgeGraphManager import clsMetaKnowledgeGraphManager

namespace = Namespace("meta_knowledge_graph", description="Meta Knowledge Graph Endpoints")


@namespace.route("/")
class clsMetaKnowledgeGraphView(Resource):
    """
    See header
    """

    def get(self):
        """
        HTTP GET request
        * todo
        :return: Meta Knowledge Graph view model
        """

        metaKnowledgeGraphManager = clsMetaKnowledgeGraphManager()
        metaKnowledgeGraphManager.generateUserResponseMetaKnowledgeGraph()

        return metaKnowledgeGraphManager.userResponseMetaKnowledgeGraph, 200
