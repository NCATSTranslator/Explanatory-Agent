"""
WHAT: Defining application specific configuration
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: Docker environment if running from the Dockerfile because IS_DOCKER is injected there
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""

import os

isDocker = True if os.getenv("IS_DOCKER") == "TRUE" else False
mountPath = "/mnt" if isDocker else os.path.join(os.path.dirname(os.getcwd()), "mnt")

logFilePath = os.path.join(mountPath, "status.log")

outputFolderPath = os.path.join(mountPath, "output")
cordDocumentsOutputFilePath = os.path.join(outputFolderPath, "cordDocuments.csv")