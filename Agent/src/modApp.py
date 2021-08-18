"""
WHAT: A module for the primary entry point of the API
WHY: This is the Flask standard entry point, using an 'modApp.py'
ASSUMES: Listens on IP and ports listed below
FUTURE IMPROVEMENTS: Remove "waitress" and replace with "uwsgi" for better web app serving and control
WHO: SL 2020-09-10
"""

import modConfig
from waitress import serve
from paste.translogger import TransLogger
from flask import Flask, redirect, url_for
from flask_compress import Compress
from modDatabase import db
from werkzeug.middleware.proxy_fix import ProxyFix
from apis.v0_9 import blueprint as blueprint_v0_9
from apis.v1_0 import blueprint as blueprint_v1_0
from apis.v1_1 import blueprint as blueprint_v1_1


def appFactory():
    """
    Method to create the flask app without binding to the database to:
    * separate concerns
    * avoid circular import references
    :return: Flask app object
    """

    # create flask app object with a name
    app = Flask(__name__)

    # add compression
    Compress(app)

    # required so we can get client IP address in logs
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # register versions
    app.register_blueprint(blueprint_v0_9)
    app.register_blueprint(blueprint_v1_0)
    app.register_blueprint(blueprint_v1_1)

    # store database config
    app.config.update(modConfig.dbConfig)

    return app


app = appFactory()  # create flask app object
db.init_app(app)  # bind to database


@app.route('/')
def redirectVersion():
    """
    Redirects user to the swagger page of the latest version of the api
    :return: A redirect
    """
    return redirect(url_for('%s.doc' % modConfig.defaultVersion))


@app.route('/health')
def healthCheck():
    """
    An endpoint that checks the api is responding and the database is responding
    :return: message json with 200 response
    """
    try:
        serverTimestamp = db.engine.execute("select current_timestamp").fetchone()[0]
    except Exception as tb:
        return {"message": f"API is up but Database host {modConfig.dbHost} is down."}, 500
    return {"message": f"API and Database are up! Database host {modConfig.dbHost} with timestamp: {str(serverTimestamp)}"}, 200


if __name__ == '__main__':
    import logging

    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    # https://docs.pylonsproject.org/projects/waitress/en/stable/arguments.html
    # waitress is lightweight and cross platform
    # performance is not as fast as uwsgi or gunicorn, but still "very acceptable"
    serve(
        app=TransLogger(
            application=app,
            setup_console_handler=False
        ),
        host=modConfig.host,
        port=modConfig.port,
        threads=modConfig.maxThreadCount
    )
