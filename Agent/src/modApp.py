"""
WHAT: A module for the primary entry point of the API
WHY: This is the Flask standard entry point, using an 'modApp.py'
ASSUMES: Listens on IP and ports listed below
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-10
"""

import modConfig
import sys
from flask import Flask, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from apis.v0_9 import blueprint as blueprint_v0_9
from apis.v1_0 import blueprint as blueprint_v1_0

app = Flask(__name__)  # gives a name to the app
app.wsgi_app = ProxyFix(app.wsgi_app)  # required so we can get client IP address in logs

app.register_blueprint(blueprint_v0_9)
app.register_blueprint(blueprint_v1_0)


@app.route('/')
def redirect_version():
    return redirect(url_for('%s.doc' % modConfig.defaultVersion))


if __name__ == '__main__':
    import logging
    from apis.common.utils.clsRequestFormatter import clsRequestFormatter

    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = clsRequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    handler.setFormatter(formatter)
    rootLogger.addHandler(handler)

    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = modConfig.port

    app.run(host=modConfig.host, port=port)
