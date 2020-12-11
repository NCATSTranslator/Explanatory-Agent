# Explanatory Agent API

A web API which accepts a TRAPI (https://github.com/NCATSTranslator/ReasonerAPI) request and returns a TRAPI Response.

Currently, the agent answers queries in the form of "What Genes are associated with a specified Disease?"

Access remotely via http://explanatory-agent.azurewebsites.net/. A Swagger interface is available for sending test TRAPI queries.

To run locally, ensure Docker is installed, port 80 is available, grant execute permissions to the run script via `chmod +x run.sh`, then execute `run.sh`. Open a browser and navigate to http://localhost/ to view the Swagger interface for the API.