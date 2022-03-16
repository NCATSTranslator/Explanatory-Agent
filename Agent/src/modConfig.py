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
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_size': 20,
    }
}

bert_checkpoints_folder = "/media/storage/biobert/re_outputs" if isDocker else "/media/engineer1/Data/virtualbox_share/Work_In_Progress/xARA/Transfer_In/biobert/biobert/re_outputs/"

maxThreadCount = 4

# Request on 2021-12-05 RE: xARA Update to set result score to very small value instead of zero.
ZERO_RESULT_SCORE = 0.0001

defaultLoggingLevel = logging.DEBUG