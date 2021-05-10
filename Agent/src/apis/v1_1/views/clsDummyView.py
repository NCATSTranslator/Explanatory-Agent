"""
todo
"""

from flask_restx import Resource, Namespace
from modDatabase import db

namespace = Namespace("dummy", description="Dummy Endpoints")


@namespace.route("/")
class clsDummyView(Resource):
    """
    See header
    """

    def get(self):
        """
        HTTP GET request
        * Returns current timestamp for dummy testing
        :return: current_timestamp from postgres
        """

        result = db.session.execute("select current_timestamp").fetchone()[0]
        return {"message": str(result)}, 200
