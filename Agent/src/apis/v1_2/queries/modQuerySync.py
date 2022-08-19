"""
WHAT: A module which containers the synchronous components of both the async and sync query versions
WHY: Some logic for both has to be done synchronously always
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2022-04-07
"""
from typing import Tuple, Union
from flask import request
from ..queries.clsQueryManager import clsQueryManager
import requests
import json
from ..modSettings import trapi_version


def querySyncPreSteps(queryManager: clsQueryManager) -> Union[Tuple[dict, int], clsQueryManager]:
    """
    The synchronous steps that are done at the beginning of a sync or async query.
    Steps that need to be done immediately without waiting, such as:
    * fetching database version
    * checking user request is a valid json
    * checking user request is a valid trapi query
    * determine async query timeout (if applicable)
    * building workflow object
    * checking if query is supported

    :param queryManager:
    :return: the updated queryManager instance
    """

    # query the database to get the version / timestamp
    queryManager.fetchDatabaseVersion()

    # make sure user request body is valid json
    try:
        queryManager.userRequestBody = request.json if request.is_json else json.loads(request.data)
    except json.decoder.JSONDecodeError:
        queryManager.generateEmptyUserResponseBody(status="BadRequest", description="Request contains invalid JSON.")
        return queryManager.userResponseBody, 400

    # make sure user request body is supported by TRAPI standard
    userRequestBodyValidationResults = queryManager.userRequestBodyValidation()
    if not userRequestBodyValidationResults["isValid"]:
        queryManager.generateEmptyUserResponseBody(status="BadRequest",
                                                   description="Supplied request body does not conform to TRAPI v{} standard. Error: {}".format(
                                                       trapi_version,
                                                       userRequestBodyValidationResults["error"].message))
        return queryManager.userResponseBody, 400

    # this is meaningful only when called from async endpoint, otherwise this is unused
    queryManager.async_timeout = 220 if queryManager.userRequestBody.get("should_wait") else 0  # azure max limit is 230 seconds

    workflowResults = queryManager.extractWorkflow()
    if "error" in workflowResults:
        queryManager.generateEmptyUserResponseBody(status="Error",
                                                   description="An error occurred while parsing the workflow.")
        return queryManager.userResponseBody, 400

    # make sure user request body only supports 2 nodes and 1 edge
    if not queryManager.userRequestBodyStructureIsSupported:
        queryManager.generateEmptyUserResponseBody(status="Unsupported", description="Unsupported query structure.")
        return queryManager.userResponseBody, 200

    return queryManager


def querySync(queryManager: clsQueryManager) -> Tuple[dict, int]:
    """
    The synchronous steps that are done inside a sync or async call stack.
    Async call stack this function will continue on past the timeout.
    HTTP POST request
    * Initializes query model
    * Checks user request body is valid
    * Checks user request body is supported
    * Forwards request body to knowledge provider POST
    * Checks knowledge provider response body is valid
    * Generates results
    * Returns entire query view model back to client
    :return: tuple of response and http code
    """

    # get curie ids (if applicable)
    try:
        queryManager.getCurieIds()
    except requests.exceptions.RequestException as requestError:
        queryManager.generateEmptyUserResponseBody(status="CurieIdsError",
                                                   description="An error occurred while accessing a Curie Ids Provider.")
        return queryManager.userResponseBody, 500

    # get categories (if applicable)
    try:
        queryManager.getCategories()
    except requests.exceptions.RequestException as requestError:
        queryManager.generateEmptyUserResponseBody(status="CategoriesError",
                                                   description="An error occurred while accessing a Categories Provider.")
        return queryManager.userResponseBody, 500

    queryManager.deriveQueryPaths()

    # find the unique edge predicates to dispatch
    queryManager.extractUniqueEdgePredicates()

    # initialize one case solution manager per edge predicate
    queryManager.createCaseSolutionManagers()

    # solve solution
    try:
        queryManager.execute()
    except requests.exceptions.RequestException as requestError:
        queryManager.generateEmptyUserResponseBody(status="KPError",
                                                   description="An error occurred while accessing a Knowledge Provider.")
        return queryManager.userResponseBody, 500
    except Exception as error:
        print("Execute exception: {}".format(error, ))
        queryManager.generateEmptyUserResponseBody(status="Error",
                                                   description="An error occurred executing a query, not related to a Knowledge Provider.")
        return queryManager.userResponseBody, 500

    # couldn't find any matching records in the database
    if not queryManager.userRequestBodyHasAtLeastOneSupportedCaseSolution:
        queryManager.generateEmptyUserResponseBody(status="Unsupported",
                                                   description="No knowledge provider supports query.")
        return queryManager.userResponseBody, 200

    # merge all case solution managers together
    queryManager.mergeCaseSolutions()

    # generate a successful user response body
    queryManager.generateSuccessUserResponseBody()

    # validate our response is supported by the TRAPI standard (not valid should never happen)
    userResponseBodyValidationResults = queryManager.userResponseBodyValidation()
    if not userResponseBodyValidationResults["isValid"]:
        queryManager.generateEmptyUserResponseBody(status="ExitValidationError",
                                                   description="An error occurred during processing.")
        return queryManager.userResponseBody, 500

    # only upload the results if it originated async
    queryManager.uploadResultsIntoDatabaseIfApplicable()

    # return results
    return queryManager.userResponseBody, 200
