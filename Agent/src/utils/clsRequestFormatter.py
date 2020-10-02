"""
WHAT: A class to supplement standard python logging
WHY: Need the request url and request ip address in the log
ASSUMES: Uses flask: https://flask.palletsprojects.com/en/1.1.x/logging/
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-15
"""

import logging
from flask import has_request_context, request


class clsRequestFormatter(logging.Formatter):
    """
    See header
    """

    def format(self, record):
        """
        Override standard logger format and add request url and ip address
        :param record: A request record
        :return: A formatted log record
        """
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None
        return super().format(record)
