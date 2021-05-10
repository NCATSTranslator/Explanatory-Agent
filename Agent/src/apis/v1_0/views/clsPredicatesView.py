"""
WHAT: A class which represents a view for all predicate related operations
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: No user input
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-12-14
"""

from flask_restx import Resource, Namespace
from ..predicates.clsPredicateManager import clsPredicateManager

namespace = Namespace("predicates", description="Predicates Endpoints")


@namespace.route("/")
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
