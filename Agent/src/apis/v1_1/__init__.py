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
from .views.clsMetaKnowledgeGraphView import namespace as clsMetaKnowledgeGraphNamespace
from .views.clsPredicatesView import namespace as clsPredicatesNamespace

version = "v1.1"
blueprint = Blueprint(version, __name__, url_prefix=f'/{version}')
namespaces = Api(
    blueprint,
    title=f"Explanatory Agent API (TRAPI {version})",
    version=modConfig.buildNumber,
    description="REST API"
)
# list alphabetical
namespaces.add_namespace(clsMetaKnowledgeGraphNamespace)
namespaces.add_namespace(clsPredicatesNamespace)
namespaces.add_namespace(clsQueryNamespace)
