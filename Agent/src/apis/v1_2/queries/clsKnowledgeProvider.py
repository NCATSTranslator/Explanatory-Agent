"""
WHAT: A class for communicating with knowledge providers.
WHY: Need to separate concerns.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-04-25
"""
import logging

import requests
from extensions.requests_extension import request_with_global_timeout

from jsonschema import ValidationError
from datetime import datetime
from utils.clsLog import clsLogEvent
from ..modSettings import trapi_version



class clsKnowledgeProvider:
    """
    See header
    """
    timeoutSeconds = 60

    def __init__(self, name: str, url: str):
        """
        Constructor
        :param name: Common name of knowledge provider
        :param url: Url to request
        """
        self.name = name
        self.url = url

        self.requestBody = None
        self.responseBody = None
        self.explanations = None

        self.logs = None

    def validateRequestBody(self):
        """
        Verify its a valid TRAPI request
        :return: None
        :raises: Will raise if not valid
        """
        try:
            import reasoner_validator
        except requests.HTTPError as e:
            logging.critical("Reasoner validator web request failing! Assuming all responses are good!")
            self.logs.append(clsLogEvent(identifier="", level="CRITICAL", code="", message=f"Reasoner validator github request is down! {e}").dict())
            return

        reasoner_validator.validate(self.requestBody, "Query", trapi_version)
        # don't log this crash, it's our fault

    def execute(self):
        """
        Sends a query to the Knowledge Provider and sets the responseBody property
        :return: None
        """
        self.validateRequestBody()
        try:
            if self.url is None:
                raise ValueError(f"No URL identified for Knowledge Provider '{self.name}'")

            self.logs.append(clsLogEvent(
                identifier=self.name,
                level="DEBUG",
                code="",
                message=f"Sending request to Knowledge Provider {self.url}..."
            ))
            response = request_with_global_timeout(
                method="post",
                url=self.url,
                global_timeout=None,
                # global_timeout=self.timeoutSeconds,
                json=self.requestBody
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            self.logs.append(clsLogEvent(
                identifier=self.name,
                level="ERROR",
                code="KPTimeout",
                message=f"Knowledge Provider {self.url} timed out after {self.timeoutSeconds} seconds"
            ))
            raise
        except requests.exceptions.HTTPError:
            self.logs.append(clsLogEvent(
                identifier=self.name,
                level="ERROR",
                code="KPNotAvailable",
                message=f"Knowledge Provider {self.url} returned HTTP error code {str(response.status_code)} for message: {self.requestBody}"
            ))
            raise
        self.logs.append(clsLogEvent(
            identifier=self.name,
            level="DEBUG",
            code="",
            message=f"KP 200 response in {response.elapsed}. Content size: {len(response.content)}."
        ))
        self.responseBody = response.json()
        self.validateResponseBody()
        self.checkForEmptyResponseBody()

    def validateResponseBody(self):
        """
        Verify its a valid TRAPI response
        :return: None
        :raises: Will raise InvalidSchema if not valid
        """
        try:
            import reasoner_validator
        except requests.HTTPError as e:
            logging.critical("Reasoner validator web request failing! Assuming all responses are good!")
            self.logs.append(clsLogEvent(identifier="", level="CRITICAL", code="", message=f"Reasoner validator github request is down! {e}").dict())
            return

        try:
            # reasoner_validator.validate_Response(self.responseBody)
            reasoner_validator.validate(self.responseBody, "Response", trapi_version)
        except ValidationError as e:
            self.logs.append(clsLogEvent(
                identifier=self.name,
                level="ERROR",
                code="KPMalformedResponse",
                message=f"Knowledge Provider {self.url} did not return a valid TRAPI v1.2 response for message: {self.requestBody}"
            ))
            error_message = str(e).split('\n')[0]
            raise requests.exceptions.InvalidSchema(f"Knowledge Provider {self.url} did not return a valid TRAPI v1.2 response: {error_message} for message: {self.requestBody}")  # force raise a request.exception to know its the KP's fault

    def checkForEmptyResponseBody(self):
        """
        Just log if the response body is empty, helpful for the users
        :return: None
        """
        if self.responseBody is None:
            self.logs.append(clsLogEvent(
                identifier=self.name,
                level="ERROR",
                code="Error",
                message=f"Knowledge Provider {self.url} did not return a message"
            ))
            return True

        knowledge_graph = self.responseBody['message']['knowledge_graph']
        if knowledge_graph is None:
            # todo, this is a bug, some of the knowledge providers return a None, which seems to valid by TRAPI v1.1
            knowledge_graph = {'edges': {}, 'nodes': {}}
            self.responseBody['message']['knowledge_graph'] = knowledge_graph
        if len(knowledge_graph['edges']) == 0 or len(knowledge_graph['nodes']) == 0:
            self.logs.append(clsLogEvent(
                identifier=self.name,
                level="WARNING",
                code="KPEmptyResponse",
                message=f"Knowledge Provider {self.url} returned an empty knowledge graph for message: {self.requestBody}"
            ))

            return True
        else:
            return False
