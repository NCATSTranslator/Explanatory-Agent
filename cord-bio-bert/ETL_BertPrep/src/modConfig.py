"""
WHAT: Defining application specific configuration
WHY: Need to define input/output paths whether running in Docker or running directly on a Windows/Mac/Linux OS, paths would be different
ASSUMES: Docker environment if running from the Dockerfile because IS_DOCKER is injected there
FUTURE IMPROVEMENTS: Figure out how to download use requests package for Google Drive files
WHO: SL 2020-08-13
"""

import os

isDocker = True if os.getenv("IS_DOCKER") == "TRUE" else False
mountPath = "/mnt" if isDocker else os.path.join(os.path.dirname(os.getcwd()), "mnt")

logFilePath = os.path.join(mountPath, "status.log")

outputFolderPath = os.path.join(mountPath, "output")
documentsFolderPath = os.path.join(outputFolderPath, "documents")
documentsFileCount = 100  # number of chunks to break up the documents

# this file had to be manually downloaded since it wouldn't allow for a web request download
downloadBaseUrl = "https://storage.googleapis.com/bert_models/2018_10_18/"
downloadFileName = "uncased_L-12_H-768_A-12.zip"
downloadUrl = downloadBaseUrl + downloadFileName

downloadFilePath = os.path.join(mountPath, "download", downloadFileName)
unpackedFolderPath = os.path.join(mountPath, "unpacked", downloadFileName.replace(".zip", "").replace(".tar.gz", ""))

vocabOriginalFilePath = os.path.join(unpackedFolderPath, 'uncased_L-12_H-768_A-12', 'vocab.txt')
vocabModifiedFilePath = vocabOriginalFilePath.replace('vocab.txt', 'vocab_modified.txt')

bertConfigOriginalFilePath = os.path.join(unpackedFolderPath, 'uncased_L-12_H-768_A-12', 'bert_config.json')
bertConfigModifiedFilePath = bertConfigOriginalFilePath.replace('bert_config.json', 'bert_config_modified.json')
