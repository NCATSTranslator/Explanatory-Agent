"""
WHAT: Defining namespaces for multiple controllers
WHY: Common practice to use __init__.py to manage this in Flask
ASSUMES: No namespace clashes between controllers
FUTURE IMPROVEMENTS: Add a better API description for swagger documentation
WHO: SL 2020-09-10
"""

from flask_restx import Api
import controllers.clsAgentController

api = Api(title="Explanatory Agent API with CICD", version="1.0", description="API")
api.add_namespace(controllers.clsAgentController.namespace)
