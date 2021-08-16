"""
WHAT: Defining application specific configuration
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: Docker environment if running from the Dockerfile because IS_DOCKER is injected there
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-10
"""

import os
from utils.modTextUtils import resolveDefaultValue

# injected into container image build in Azure DevOps with: '--build-arg BUILD_NUMBER_ARG=$(Build.BuildNumber)'
buildNumber = resolveDefaultValue(value=os.getenv("BUILD_NUMBER"), default="LOCAL BUILD")

defaultVersion = "v1.1"  # redirect swagger

isDocker = True if os.getenv("IS_DOCKER") == "TRUE" else False
host = '0.0.0.0' if isDocker else 'localhost'
port = int(resolveDefaultValue(value=os.getenv("PORT"), default=80))

dbUserName = resolveDefaultValue(value=os.getenv("DB_USERNAME"), default="postgres")
dbPassword = resolveDefaultValue(value=os.getenv("DB_PASSWORD"), default="postgres")
dbHost = resolveDefaultValue(value=os.getenv("DB_HOST"), default="localhost")
if dbHost == "localhost" and isDocker and buildNumber == "LOCAL BUILD":
    dbHost = "host.docker.internal"
dbPort = int(resolveDefaultValue(value=os.getenv("DB_PORT"), default=5432))
dbSchema = resolveDefaultValue(value=os.getenv("DB_SCHEMA"), default="xARA")
dbConfig = {
    'SQLALCHEMY_DATABASE_URI': f'postgresql://{dbUserName}:{dbPassword}@{dbHost}:{dbPort}/{dbSchema}',
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
}

maxThreadCount = 4
