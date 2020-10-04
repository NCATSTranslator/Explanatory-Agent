"""
WHAT: Defining application specific configuration
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: Docker environment if running from the Dockerfile because IS_DOCKER is injected there
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-10
"""

import os

isDocker = True if os.getenv("IS_DOCKER") == "TRUE" else False
host = '0.0.0.0' if isDocker else 'localhost'
port = 80

# injected into container image build in Azure DevOps with: '--build-arg BUILD_NUMBER_ARG=$(Build.BuildNumber)'
buildNumber = os.getenv("BUILD_NUMBER", "LOCAL BUILD")
