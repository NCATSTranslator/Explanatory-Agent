"""
WHAT: A module for the primary entry point of the API
WHY: This is the Flask standard entry point, using an 'modApp.py'
ASSUMES: Listens on IP and ports listed below
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-10
"""

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from controllers import api


app = Flask(__name__)  # gives a name to the app
app.wsgi_app = ProxyFix(app.wsgi_app)  # required so we can get client IP address in logs
api.init_app(app)  # wraps flask_restx around standard flask


if __name__ == '__main__':
    import modConfig
    import logging
    from utils.clsRequestFormatter import clsRequestFormatter

    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = clsRequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    handler.setFormatter(formatter)
    rootLogger.addHandler(handler)

    app.run(host=modConfig.host, port=modConfig.port)
