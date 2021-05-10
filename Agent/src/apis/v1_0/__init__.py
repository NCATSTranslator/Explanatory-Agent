"""
WHAT: Defining namespaces for multiple views
WHY: Common practice to use __init__.py to manage this in Flask
ASSUMES: No namespace clashes between views
FUTURE IMPROVEMENTS: Add a better API description for swagger documentation
WHO: SL 2020-09-10
"""

import modConfig
from flask_restx import Api
from flask import Blueprint
from .views.clsQueryView import namespace as clsQueryNamespace
from .views.clsPredicatesView import namespace as clsPredicatesNamespace

version = "v1.0"
blueprint = Blueprint(version, __name__, url_prefix=f'/{version}')
namespaces = Api(
    blueprint,
    title=f"Explanatory Agent API (TRAPI {version})",
    version=modConfig.buildNumber,
    description="REST API"
)
namespaces.add_namespace(clsQueryNamespace)
namespaces.add_namespace(clsPredicatesNamespace)
