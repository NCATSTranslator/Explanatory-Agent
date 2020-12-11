"""
WHAT: Defining application specific configuration
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: Docker environment if running from the Dockerfile because IS_DOCKER is injected there
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""

import os
import requests_cache

isDocker = True if os.getenv("IS_DOCKER") == "TRUE" else False
mountPath = "/mnt" if isDocker else os.path.join(os.path.dirname(os.getcwd()), "mnt")

logFilePath = os.path.join(mountPath, "status.log")
downloadFolderPath = os.path.join(mountPath, "download")
inputFolderPath = os.path.join(mountPath, "input")

proteinFilePath = os.path.join(inputFolderPath, "proteins.json")
diseaseFilePath = os.path.join(inputFolderPath, "diseases.json")

cacheFilePath = os.path.join(downloadFolderPath, "cache")
requests_cache.install_cache(cache_name=cacheFilePath, allowable_methods=['GET', 'POST'])

# eUtils documentation https://www.ncbi.nlm.nih.gov/books/NBK25497/
eUtilsUrl = "https://www.ncbi.nlm.nih.gov/entrez/eutils/"
eUtilsSearchUrl = eUtilsUrl + "esearch.fcgi"
eUtilsApiKey = "7c319352487a9223ef99c9529dcf33de9c08"
eUtilsAssayDatabase = "pcassay"

# pubchem documentation https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest
pcUrl = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
pcAssayDatabase = "bioassay"
pcCompoundDatabase = "compound"
pcSubstanceDatabase = "substance"

outputFolderPath = os.path.join(mountPath, "output")
biologicalWordsOutputFilePath = os.path.join(outputFolderPath, "biologicalWords.csv")

maxRequestTryCount = 3  # number of times to try a request
requestTryDelaySeconds = 10  # amount of time in seconds to wait before re-trying
