"""
WHAT: A class which will:
    * Download the CORD-19 dataset .tar.gz file
    * Unpack the CORD-19 dataset .tar.gz file
    * Load the CORD-19 metadata file
    * Creates a unique index to handle duplicate files
    * Load the user stop words text file
    * Load document objects
    * Process document objects
    * Unload document objects
    * Exports results to disk
    * Upload results to MySQL (via csv file upload)
WHY: Need an object which manages the entire data flow in the program
ASSUMES: 1 instance only, no need for more instances, but there's no static class in python
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""

import pandas as pd
import modConfig
from tqdm import tqdm
from clsDocument import clsDocument
from clsDatabase import clsDatabase
import modDispatcher
import logging
import os
import requests
import tarfile
import urllib.parse


class clsDocumentManager:
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """
        self.dfMetadata = None  # a DataFrame of the metadata.csv file
        self.uniqueMetadata = None  # a dictionary of the unique metadata to be loaded into document objects
        self.documents = None  # a list of document objects
        self.dfDocuments = None  # document object data unloaded into a DataFrame
        self.standardStopWords = None  # a list of standard stop words from nltk package
        self.userStopWords = None  # a list of user supplied stop words from userStopWords.txt
        self.combinedStopWords = None  # the combined set of stop words

    @staticmethod
    def printAndLog(msg):
        """
        Helper function to print and logging.info
        :param msg: Any message
        :return: None
        """
        print(msg)
        logging.info(msg)

    def checkHealth(self):
        """
        Connect to MySQL and webservices to verify they are up and running.  This in-lieu of format integration tests.
        :return: None
        """
        self.printAndLog("Checking MySQL connectivity")
        db = clsDatabase()
        db.connect()

        self.printAndLog("Disconnecting from MySQL")
        db.disconnect()

        self.printAndLog("Checking file host url")
        parsedUrl = urllib.parse.urlsplit(modConfig.downloadUrl)
        response = requests.get(parsedUrl.scheme + "://" + parsedUrl.netloc)
        response.raise_for_status()

        self.printAndLog("Health check OK!")

    def downloadDocuments(self):
        """
        Downloads the CORD-19 dataset .tar.gz file in 1KB increments via stream for progress bar monitoring
        :return: None
        """
        self.printAndLog("Initiating download of file %s" % modConfig.downloadFileName)
        if os.path.exists(modConfig.downloadFilePath):
            self.printAndLog("File %s already downloaded" % modConfig.downloadFileName)
            return

        self.printAndLog("Downloading %s" % modConfig.downloadFileName)
        response = requests.get(modConfig.downloadUrl, stream=True)
        response.raise_for_status()
        totalSizeInBytes = int(response.headers.get('content-length', 0))
        blockSize = 1024  # 1 KB
        progressBar = tqdm(total=totalSizeInBytes, unit='iB', unit_scale=True, desc="Downloading %s" % modConfig.downloadFileName)
        with open(modConfig.downloadFilePath, 'wb') as file:
            for data in response.iter_content(blockSize):
                progressBar.update(len(data))
                file.write(data)
        progressBar.close()
        if totalSizeInBytes != 0 and progressBar.n != totalSizeInBytes:
            raise RuntimeError("Something failed with the download")

    def unpackDocuments(self):
        """
        Unpacks the CORD-19 dataset .tar.gz file which was downloaded because we cannot access a compressed file
        :return: None
        """
        self.printAndLog("Initiating unpacking of file %s" % modConfig.downloadFileName)
        if os.path.exists(modConfig.unpackedRootFolderPath):
            self.printAndLog("File %s already unpacked" % modConfig.downloadFileName)
            return

        self.printAndLog("Unpacking %s" % modConfig.downloadFilePath)
        tar = tarfile.open(modConfig.downloadFilePath, "r:gz")
        tar.extractall(path=modConfig.unpackedFolderPath)
        tar.close()

        self.printAndLog("Unpacking %s" % modConfig.packedEmbeddingsFilePath)
        tar = tarfile.open(modConfig.packedEmbeddingsFilePath, "r:gz")
        tar.extractall(path=modConfig.unpackedEmbeddingsFolderPath)
        tar.close()

        self.printAndLog("Unpacking %s" % modConfig.packedParsingsFilePath)
        tar = tarfile.open(modConfig.packedParsingsFilePath, "r:gz")
        tar.extractall(path=modConfig.unpackedParsingsFolderPath)
        tar.close()

    def loadMetadataFile(self):
        """
        Reads the CORD-19 metadata file which describes the all of the .json files that were unpacked
        :return: None
        """
        self.printAndLog("Reading metadata file")
        self.dfMetadata = pd.read_csv(modConfig.metadataFilePath, dtype=object)[["cord_uid", "title", "abstract", "pdf_json_files", "pmc_json_files"]]

    def buildUniqueMetadata(self):
        """
        Creates unique metadata from the metadata file provided by the CORD-19 project.
        The metadata file provided by the CORD study is not unique per document.
        This method creates a unique key of ReleaseDate + RowId + CordUid + DocumentType + DocumentDuplicateCount
        See clsDocument constructor for more details.
        :return: None
        """
        self.printAndLog("Building unique metadata")
        uniqueMetadata = {}
        for index, row in tqdm(self.dfMetadata.iterrows(), total=len(self.dfMetadata), desc="Making unique metadata"):

            if pd.notnull(row["pdf_json_files"]):
                pdfJsonFiles = row["pdf_json_files"].split(";")
                for i, pdfJsonFile in enumerate(pdfJsonFiles):
                    id = modConfig.releaseDate + "_" + str(index).zfill(7) + "_" + row["cord_uid"] + "_pdf_" + str(i).zfill(2)
                    uniqueMetadata[id] = {"title": row["title"], "abstract": row["abstract"], "filePath": pdfJsonFile.strip(), "fileType": "pdf"}

            if pd.notnull(row["pmc_json_files"]):
                pmcJsonFiles = row["pmc_json_files"].split(";")
                for i, pmcJsonFile in enumerate(pmcJsonFiles):
                    id = modConfig.releaseDate + "_" + str(index).zfill(7) + "_" + row["cord_uid"] + "_pmc_" + str(i).zfill(2)
                    uniqueMetadata[id] = {"title": row["title"], "abstract": row["abstract"], "filePath": pmcJsonFile.strip(), "fileType": "pmc"}
        self.uniqueMetadata = uniqueMetadata

    def loadDocuments(self):
        """
        Loads each unique metadata value into a document object model because we need OOP design simplifies maintenance
        :return: None
        """
        self.printAndLog("Loading document objects")
        self.documents = [
            clsDocument(
                id=id,
                title=metadata["title"],
                abstract=metadata["abstract"],
                filePath=metadata["filePath"],
                fileType=metadata["fileType"],
            ) for id, metadata in tqdm(self.uniqueMetadata.items(), desc="Building document objects")
        ]

    def processDocuments(self):
        """
        Executes document based computation, sends a list of documents to dispatching engine in series or in parallel
        Computation is simply the "execute" function signature of clsDocument.
        :return: None
        """
        self.printAndLog("Processing document objects")
        self.documents = modDispatcher.dispatcher(objs=self.documents, mode="serial")

    def unloadDocuments(self):
        """
        Converts document objects to pandas DataFrame to prepare for uploading
        :return: None
        """
        self.printAndLog("Unloading document objects")
        self.dfDocuments = pd.DataFrame(data=[[document.id, document.combinedText] for document in self.documents], columns=['id', 'text'])
        self.documents = None  # release memory

    def exportResults(self):
        """
        Export results for debugging purposes
        :return: None
        """
        self.printAndLog("Exporting results for debugging purposes")
        self.dfDocuments.to_csv(modConfig.cordDocumentsOutputFilePath, index=False, line_terminator="\n")

    def uploadResults(self):
        """
        Uploads all document output text to MySQL
        :return: None
        """
        db = clsDatabase()
        db.connect()
        db.uploadTableViaDataFrame(df=self.dfDocuments, tableName="cord_documents", clearTable=True)
        db.disconnect()

    def execute(self):
        """
        Execute all methods as a group of functions
        :return: None
        """
        self.checkHealth()
        self.downloadDocuments()
        self.unpackDocuments()
        self.loadMetadataFile()
        self.buildUniqueMetadata()
        self.loadDocuments()
        self.processDocuments()
        self.unloadDocuments()
        self.exportResults()
        self.uploadResults()
