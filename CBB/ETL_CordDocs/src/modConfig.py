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

releaseDate = "2020-07-30"
downloadBaseUrl = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/"
downloadFileName = "cord-19_%s.tar.gz" % releaseDate
downloadUrl = downloadBaseUrl + downloadFileName

downloadFilePath = os.path.join(mountPath, "download", downloadFileName)
unpackedFolderPath = os.path.join(mountPath, "unpacked", downloadFileName.replace(".tar.gz", ""))
unpackedRootFolderPath = os.path.join(unpackedFolderPath, releaseDate)

packedEmbeddingsFilePath = os.path.join(unpackedRootFolderPath, "cord_19_embeddings.tar.gz")
packedParsingsFilePath = os.path.join(unpackedRootFolderPath, "document_parses.tar.gz")
unpackedEmbeddingsFolderPath = os.path.join(unpackedRootFolderPath, "embeddings")
unpackedParsingsFolderPath = os.path.join(unpackedRootFolderPath, "parsings")

embeddingsFilePath = os.path.join(unpackedEmbeddingsFolderPath, "cord_19_embeddings_%s.csv" % releaseDate)
pdfParsingsFolderPath = os.path.join(unpackedParsingsFolderPath, "document_parses", "pdf_json")
pmcParsingsFolderPath = os.path.join(unpackedParsingsFolderPath, "document_parses", "pmc_json")
metadataFilePath = os.path.join(unpackedRootFolderPath, "metadata.csv")

outputFolderPath = os.path.join(mountPath, "output")
cordDocumentsOutputFilePath = os.path.join(outputFolderPath, "cordDocuments_%s.csv" % releaseDate)
