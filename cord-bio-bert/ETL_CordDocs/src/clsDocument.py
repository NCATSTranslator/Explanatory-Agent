"""
WHAT: A class which represents a single document with its metadata and methods.
A document represents a single .json file in the CORD-19 document collection.
This class knows how to read and combined all of its own metadata to prepare for export to MySQL.
WHY: Need an object which encapsulates a single document.
ASSUMES: 1 instance per .json document in the input data
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""

import json
import os
import pandas as pd
import modConfig


class clsDocument:
    """
    See header
    """

    def __init__(self, id, title, abstract, filePath, fileType):
        """
        Constructor
        The unique id was created because:
        ReleaseDate gives traceability into which release of the cord-19 dataset
        RowId gives the row number in the metadata.csv file
        CordUid gives the supposedly unique identifier of the document, however there are duplicates due to multiple submissions of the same document
        DocumentType gives either 'pdf' or 'pmc' from the metadata.csv, sometimes there is both listed
        DocumentDuplicationCount gives how many times this occurs through string splitting the file path on ";", giving multiple documents
        :param id: The artificially created unique document id (ReleaseDate + RowId + CordUid + DocumentType + DocumentDuplicateCount)
        :param title: The document title from the CORD-19 metadata file (if available)
        :param abstract: The document abstract from the CORD-19 metadata file (if available)
        :param filePath: The full path to the .json document file
        :param fileType: Either "pdf" or "pmc" document type
        """
        self.id = id
        self.title = title
        self.abstract = abstract

        self.filePath = filePath
        self.fileType = fileType

        self.jsonData = None
        self.combinedText = None

        # some validation
        if self.fileType.lower() not in ["pdf", "pmc"]:
            raise AttributeError("fileType input parameter must be either 'pdf' or 'pmc'")

    @staticmethod
    def isNullOrWhiteSpace(text):
        """
        Helper function to check whether a given text is either null or whitespace
        :param text: Any string
        :return: boolean
        """
        if pd.isnull(text) or text.strip() == "":
            return True
        return False

    def loadJsonFile(self):
        """
        Read the document .json file into memory
        :return: None
        """
        with open(os.path.join(modConfig.unpackedParsingsFolderPath, self.filePath)) as file:
            self.jsonData = json.load(file)

    def applyJsonTitleIfRequired(self):
        """
        Fetch the document title from the .json file if the CORD-19 metadata file didn't provide it
        :return: None
        """
        if not self.isNullOrWhiteSpace(self.title): return
        self.title = self.jsonData["metadata"]["title"]

    def applyJsonAbstractIfRequired(self):
        """
        Fetch the document abstract from the .json file if the CORD-19 metadata file didn't provide it
        :return: None
        """
        if not self.isNullOrWhiteSpace(self.abstract): return
        if not self.fileType.lower() == "pdf": return
        abstract = ""
        for element in self.jsonData["abstract"]:
            if not self.isNullOrWhiteSpace(element["text"]):
                abstract += element["text"].strip() + " "
        self.abstract = abstract.strip()

    def buildCombinedText(self):
        """
        Combines all document text into a single string blob
        :return: None
        """
        combinedText = ""
        if not self.isNullOrWhiteSpace(self.title):
            combinedText += self.title.strip() + " "
        if not self.isNullOrWhiteSpace(self.abstract):
            combinedText += self.abstract.strip() + " "
        for element in self.jsonData["body_text"]:
            elementText = element["text"]
            if not self.isNullOrWhiteSpace(elementText):
                combinedText += elementText.strip() + " "
        self.combinedText = combinedText.strip().replace("\n", " ").replace("\r", " ")

    def freeMemory(self):
        """
        Release unused memory we don't need those anymore, garbage collection makes the code slow.
        The code is still holding onto these instances so it doesn't know to release these properties.
        We are preserving only the id, combinedText, and combinedTextLessStopWords properties.
        This document class knows nothing of the other document classes.
        :return: None
        """
        self.title = None
        self.abstract = None
        self.filePath = None
        self.fileType = None
        self.jsonData = None

    def execute(self):
        """
        Execute all computation for this document as a group of functions
        :return: None
        """
        self.loadJsonFile()
        self.buildCombinedText()
        self.freeMemory()
