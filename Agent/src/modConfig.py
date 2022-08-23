"""
WHAT: Defining application specific configuration
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: Docker environment if running from the Dockerfile because IS_DOCKER is injected there
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-10
"""

import os
from utils.modTextUtils import resolveDefaultValue
import logging

# injected into container image build in Azure DevOps with: '--build-arg BUILD_NUMBER_ARG=$(Build.BuildNumber)'
buildNumber = resolveDefaultValue(value=os.getenv("BUILD_NUMBER"), default="LOCAL BUILD")

defaultVersion = "v1.2"  # redirect swagger

isDocker = True if os.getenv("IS_DOCKER") == "TRUE" else False
host = '0.0.0.0' if isDocker else 'localhost'
port = int(resolveDefaultValue(value=os.getenv("PORT"), default=80))

# Primary "xARA" database connection settings
xARA_dbUserName = resolveDefaultValue(value=os.getenv("DB_USERNAME"), default="postgres")
xARA_dbPassword = resolveDefaultValue(value=os.getenv("DB_PASSWORD"), default="postgres")
xARA_dbHost = resolveDefaultValue(value=os.getenv("DB_HOST"), default="localhost")
if xARA_dbHost == "localhost" and isDocker and buildNumber == "LOCAL BUILD":
    xARA_dbHost = "host.docker.internal"
xARA_dbPort = int(resolveDefaultValue(value=os.getenv("DB_PORT"), default=5432))
xARA_dbEtlName = resolveDefaultValue(value=os.getenv("DB_NAME"), default="xARA")  # primary
dbEtlName = xARA_dbEtlName

# Secondary "xARA_app" database connection settings
xARA_app_dbUserName = resolveDefaultValue(value=os.getenv("XARA_APP_DB_USERNAME"), default="postgres")
xARA_app_dbPassword = resolveDefaultValue(value=os.getenv("XARA_APP_DB_PASSWORD"), default="postgres")
xARA_app_dbHost = resolveDefaultValue(value=os.getenv("XARA_APP_DB_HOST"), default="localhost")
if xARA_app_dbHost == "localhost" and isDocker and buildNumber == "LOCAL BUILD":
    xARA_app_dbHost = "host.docker.internal"
xARA_app_dbPort = int(resolveDefaultValue(value=os.getenv("XARA_APP_DB_PORT"), default=5432))
xARA_app_dbEtlName = resolveDefaultValue(value=os.getenv("XARA_APP_DB_NAME"), default="xARA_app")  # secondary
dbAppName = xARA_app_dbEtlName

dbConfig = {
    'SQLALCHEMY_DATABASE_URI': f'postgresql://{xARA_dbUserName}:{xARA_dbPassword}@{xARA_dbHost}:{xARA_dbPort}/{xARA_dbEtlName}',
    'SQLALCHEMY_BINDS': {
        dbAppName: f'postgresql://{xARA_app_dbUserName}:{xARA_app_dbPassword}@{xARA_app_dbHost}:{xARA_app_dbPort}/{xARA_app_dbEtlName}',
    },
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_size': 20,
    }
}

# todo, figure out dynamic way to retrieve host name from azure app service
if xARA_dbHost == "explanatory-agent-dev.postgres.database.azure.com":
    externalApiHost = "https://explanatory-agent-dev.azurewebsites.net"
elif xARA_dbHost == "explanatory-agent.postgres.database.azure.com":
    externalApiHost = "https://explanatory-agent.azurewebsites.net"
else:
    externalApiHost = "http://127.0.0.1"

bert_checkpoints_folder = "/media/storage/biobert/re_outputs" if isDocker else "/media/engineer1/Data/virtualbox_share/Work_In_Progress/xARA/Transfer_In/biobert/biobert/re_outputs/"

maxThreadCount = 4

# Request on 2021-12-05 RE: xARA Update to set result score to very small value instead of zero.
ZERO_RESULT_SCORE = 0.0001

defaultLoggingLevel = logging.DEBUG