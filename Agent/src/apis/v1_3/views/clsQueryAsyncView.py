"""
WHAT: A class which represents a view for all query related operations async
WHY: Need an api view for async operations so that the user can come back later to monitor their long running request
ASSUMES: 'Agent' is short for 'Explanatory Autonomous Relay Agent'
FUTURE IMPROVEMENTS: N/A
WHO: SL 2022-04-07
"""
import multiprocessing
from flask_restx import Resource, Namespace
from ..queries.modQuerySync import querySync
from .clsQueryView import body as post_body
from multiprocessing.dummy import Pool as ThreadPool
from flask import current_app
from flask import request
from modDatabase import db
from ..models.clsXaraQueryResults import tableName
import uuid as uuid_module
import modConfig
from ..queries.clsQueryManager import clsQueryManager
from ..queries.modQuerySync import querySyncPreSteps


namespace = Namespace("query_async", description="Query Async Endpoints")


get_body = {
    "uuid": {"in": "query", "description": "UUID for the query", "default": "some-random-uuid-string"}
}


@namespace.route("/")
class clsQueryAsyncView(Resource):
    """
    See header
    """

    @namespace.doc(body=post_body)
    def post(self):
        """
        Same behavior as the sync POST, except the user can poll the UUID via result_url
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

        uuid = str(uuid_module.uuid4())

        queryManager = clsQueryManager(app=current_app._get_current_object(), uuid=uuid)
        queryManager.processing_timeout = 1 * 60 * 60  # 1 hour

        preStepResults = querySyncPreSteps(queryManager=queryManager)
        if not isinstance(preStepResults, clsQueryManager):
            return preStepResults

        queryManager = preStepResults
        queryManager.insertUuidIntoDatabaseIfApplicable()

        pool = ThreadPool(processes=1)
        asyncResult = pool.apply_async(func=querySync, kwds={"queryManager": queryManager})
        try:
            result = asyncResult.get(timeout=queryManager.async_timeout)
        except multiprocessing.TimeoutError:
            return queryManager.userResponseBodyPendingAsync, 201

        return result

    @namespace.doc(params=get_body)
    def get(self):
        """
        A HTTP get to poll a long-running async query via the result_url which contains a UUID
        * Parses a provided UUID
        * Queries the database for the given UUID
        * Returns 404 if the UUID was not found
        * Returns null payload if the query did not finish
        * Returns full payload if the query finished
        :return: Query view model from the database
        """

        uuid = request.args.get("uuid")

        if not uuid or not isinstance(uuid, str):
            return {"message": "Invalid uuid"}, 400

        sql = \
            f"""
            select
                "UUID",
                "PAYLOAD"
            from "{tableName}"
            where "UUID" = :uuid
            """
        session = db.create_scoped_session(options={'bind': db.get_engine(app=current_app, bind=modConfig.dbAppName)})
        result = session.execute(sql, params={"uuid": uuid}).fetchone()
        if not result:
            return {"message": f"uuid {uuid} not found"}, 404

        assert result[0] == uuid
        payload = result[1]
        return payload, 200
