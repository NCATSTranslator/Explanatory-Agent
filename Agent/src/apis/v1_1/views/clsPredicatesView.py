"""
WHAT: A class which represents a view for all predicate related operations
WHY: Need to keep deprecated endpoint around in v1.1
ASSUMES: Same sql query as meta_knowledge_graph endpoint
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-05-19
"""

from flask_restx import Resource, Namespace
from ..predicates.clsPredicateManager import clsPredicateManager

namespace = Namespace("predicates", description="Predicates Endpoints")


@namespace.route("/")
@namespace.deprecated
class clsPredicatesView(Resource):
    """
    See header
    """

    def get(self):
        """
        HTTP GET request
        * Returns biological predicates supported by this api
        :return: Predicate view model
        """

        predicateManager = clsPredicateManager()
        predicateManager.generateUserResponsePredicates()

        return predicateManager.userResponsePredicates, 200
