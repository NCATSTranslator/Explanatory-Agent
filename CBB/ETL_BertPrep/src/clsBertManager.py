"""
WHAT: A class which will:
        * Download bert pretraining data .zip file
        * Unpacks bert pretraining data .zip file
        * Loads document text into memory as a list (the replaced text)
        * Create bert input file (a new sentence each line, documents separated by a blank line)
WHY: Need an object which manages the entire data flow in the program
ASSUMES: 1 instance only, no need for more instances, but there's no static class in python
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-28
"""

import modConfig
import logging
from clsDatabase import clsDatabase
import os
import nltk
from tqdm import tqdm
import zipfile
import tarfile
import requests
import shutil
import numpy as np
import json


class clsBertManager:
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """
        self.df = None  # a dataframe of every document with replaced text

    @staticmethod
    def printAndLog(msg):
        """
        Helper function to print and logging.info
        :param msg: Any message
        :return: None
        """
        print(msg)
        logging.info(msg)

    @staticmethod
    def readFileAsString(fileName):
        """
        Read a text file as a string
        :param fileName: The file name
        :return: The string of the text file
        """
        with open(fileName, "r") as file:
            return file.read()

    def checkHealth(self):
        """
        Connect to MySQL is up and running.  This in-lieu of format integration tests.
        Also check to see if web service hosting the files is up.
        :return: None
        """
        self.printAndLog("Checking MySQL connectivity")
        db = clsDatabase()
        db.connect()
        db.disconnect()

        self.printAndLog("Checking file host url")
        response = requests.get(modConfig.downloadBaseUrl)
        assert response.status_code in [200, 403, 404]  # 403/404 is OK here, at least we know its up (sort of)

        self.printAndLog("Health check OK!")

    def downloadPretraining(self):
        """
        Downloads the bert dataset .zip file in 1KB increments via stream for progress bar monitoring
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

    def unpackPretraining(self):
        """
        Unpacks the pretrained dataset file (.tar.gz or .zip) which was downloaded because we cannot access a compressed file
        :return: None
        """
        self.printAndLog("Initiating unpacking of file %s" % modConfig.downloadFileName)
        if os.path.exists(modConfig.unpackedFolderPath):
            self.printAndLog("File %s already unpacked" % modConfig.downloadFileName)
            return

        self.printAndLog("Unpacking %s" % modConfig.downloadFilePath)
        if modConfig.downloadFilePath.endswith(".zip"):
            with zipfile.ZipFile(modConfig.downloadFilePath, "r") as zipRef:
                zipRef.extractall(modConfig.unpackedFolderPath)
        elif modConfig.downloadFilePath.endswith(".tar.gz"):
            tar = tarfile.open(modConfig.downloadFilePath, "r:gz")
            tar.extractall(modConfig.unpackedFolderPath)
            tar.close()
        else:
            raise AttributeError("File extension must be .zip or .tar.gz for unpacking")

    def addBackwardsWordsToVocabFile(self):
        """
        Create a copy of the provided vocab text file, and add the backwards words to the end
        :return: None
        """
        self.printAndLog("Modifying vocab file")
        if os.path.exists(modConfig.vocabModifiedFilePath):
            self.printAndLog("Vocab file %s already modified" % modConfig.vocabModifiedFilePath)
            return

        shutil.copy(src=modConfig.vocabOriginalFilePath, dst=modConfig.vocabModifiedFilePath)
        with open(modConfig.vocabModifiedFilePath, 'a', newline='\n') as file:
            file.write("".join(list(reversed("chemical"))) + '\n')
            file.write("".join(list(reversed("disease"))) + '\n')
            file.write("".join(list(reversed("protein"))) + '\n')

    def addVocabRowsToBertConfigFile(self):
        """
        Create a copy of the provided bert_config text file, and add the backwards words to the end
        :return: None
        """
        self.printAndLog("Modifying Bert Config file")
        if os.path.exists(modConfig.bertConfigModifiedFilePath):
            self.printAndLog("Bert Config file %s already modified" % modConfig.bertConfigModifiedFilePath)
            return

        with open(modConfig.bertConfigOriginalFilePath, 'r') as file:
            bertConfig = json.load(file)
        bertConfig['vocab_size'] += 3
        with open(modConfig.bertConfigModifiedFilePath, 'w') as file:
            json.dump(bertConfig, file)

    def loadDocumentTextWithReplacedWords(self):
        """
        Read document text with replaced backwards biological words
        :return: None
        """
        self.printAndLog("Loading document text with backwards biological words")
        db = clsDatabase()
        db.connect()
        self.df = db.execute(sql=self.readFileAsString("sql/fetchDocumentsWithReplacedWords.sql"), expectingReturn=True)
        self.df.set_index(['id'], inplace=True)
        db.disconnect()

    def createBertInputFile(self):
        """
        Create Bert input file
        :return: None
        """
        self.printAndLog("Cleaning documents directory")
        if os.path.exists(modConfig.documentsFolderPath):
            shutil.rmtree(modConfig.documentsFolderPath)
        os.mkdir(modConfig.documentsFolderPath)

        self.printAndLog("Breaking dataframe into chunks")
        chunkDfs = np.array_split(self.df, modConfig.documentsFileCount)
        zfillSize = len(str(modConfig.documentsFileCount))

        self.printAndLog("Writing documents to files")
        for chunkNumber, chunkDf in enumerate(tqdm(chunkDfs, desc="Writing documents", unit="file")):
            documentsFileName = os.path.join(modConfig.documentsFolderPath, str(chunkNumber).zfill(zfillSize) + ".txt")
            documentsFileObject = open(documentsFileName, "w+", encoding="utf-8", newline="\n")
            documentNumber = 0
            for index, row in chunkDf.iterrows():
                sentences = nltk.tokenize.sent_tokenize(row['text'])
                for sentenceNumber, sentenceText in enumerate(sentences):
                    documentsFileObject.writelines(sentenceText + "\n")
                if documentNumber != (len(chunkDf) - 1):
                    documentsFileObject.write("\n")
                documentNumber += 1
            documentsFileObject.close()

    def execute(self):
        """
        Execute all methods as a group of functions
        :return: None
        """
        self.checkHealth()
        self.downloadPretraining()
        self.unpackPretraining()
        self.addBackwardsWordsToVocabFile()
        self.addVocabRowsToBertConfigFile()
        self.loadDocumentTextWithReplacedWords()
        self.createBertInputFile()
