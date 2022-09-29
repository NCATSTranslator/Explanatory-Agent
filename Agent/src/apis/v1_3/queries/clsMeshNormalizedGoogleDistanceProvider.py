"""
WHAT: Requests and returns data from a synonyms lookup service.
WHY: Synonyms are needed for explanations.
ASSUMES: None
FUTURE IMPROVEMENTS:
WHO: TZ 2021-09-25
"""

from extensions.requests_extension import request_with_global_timeout
from typing import Optional


class clsMeshNormalizedGoogleDistanceProvider:
    """
    See header
    """
    timeoutSeconds = 30

    url = "https://arax.ncats.io/api/arax/v1.3/PubmedMeshNgd/"

    def __init__(self, subject_name: str, object_name: str, raise_on_status=False):
        """
        Constructor
        :param subject_name: Name (NOT CURIE) of the subject to compare
        :param object_name: Name (NOT CURIE) of the object to compare
        :param raise_on_status: Raise an error if the response was not 200
        """
        self.subject_name: str = subject_name
        self.object_name: str = object_name
        self.response = None
        self.responseBody = None
        self.error_message: Optional[str] = None
        self.response_code: Optional[str] = None
        self.value: Optional[float] = None
        self.request_url: str = f"{self.url}{self.subject_name}/{self.object_name}"
        self.raise_on_status: bool = raise_on_status

    def get_value(self):
        """
        Gets the Normalized Google Distance between the subject and object.
        :return: None
        """
        self.response = request_with_global_timeout(
            method="GET",
            url=self.request_url,
            # global_timeout=self.timeoutSeconds,
            global_timeout=None
        )

        if self.raise_on_status:
            self.response.raise_for_status()

        if self.response.ok is False:
            return

        self.responseBody = self.response.json()

        self.response_code = self.responseBody["response_code"]

        if "value" in self.responseBody:
            self.value = self.responseBody["value"]
        else:
            self.error_message = self.responseBody["message"]
