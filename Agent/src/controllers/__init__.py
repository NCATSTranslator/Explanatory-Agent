"""
WHAT: Defining namespaces for multiple controllers
WHY: Common practice to use __init__.py to manage this in Flask
ASSUMES: No namespace clashes between controllers
FUTURE IMPROVEMENTS: Add a better API description for swagger documentation
WHO: SL 2020-09-10
"""

import modConfig
from flask_restx import Api
import controllers.clsAgentController

api = Api(title="Explanatory Agent API with CICD", version=modConfig.buildNumber, description="REST API")
api.add_namespace(controllers.clsAgentController.namespace)
