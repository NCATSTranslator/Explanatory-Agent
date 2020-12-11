"""
WHAT: A class which will:
    * Fetch the biological words from MySQL (proteins, chemicals, and diseases)
    * Fetch document originalText from MySQL
    * Build case-insensitive dictionary of biological words and their backwards bio-type
    * Load documents objects
    * Process document objects
    * Upload results to MySQL
WHY: Need an object which manages the entire data flow in the program
ASSUMES: 1 instance only, no need for more instances, but there's no static class in python
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""

from clsDatabase import clsDatabase
from clsDocument import clsDocument
from clsCaseInsensitiveDictionary import clsCaseInsensitiveDictionary
from tqdm import tqdm
import logging
import pandas as pd
import modConfig


class clsDocumentManager:
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """
        self.dfBiologicalWords = None  # a pandas DataFrame of the biological words
        self.dfDocuments = None  # a pandas DataFrame of the document originalText with id, and later as replacedText with id
        self.documents = None  # a list of document objects
        self.caseInsensitiveDictionaryOfBiologicalWords = None  # a case-insensitive dictionary of biological words, and their word type backwards

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
        Connect to MySQL and webservices to verify they are up and running.  This in-lieu of format integration tests.
        Also check to see if files for I/O exist.
        :return: None
        """
        self.printAndLog("Checking MySQL connectivity")
        db = clsDatabase()
        db.connect()

        self.printAndLog("Disconnecting from MySQL")
        db.disconnect()

        self.printAndLog("Health check OK!")

    def fetchDocuments(self):
        """
        Connect to MySQL and retrieve the document originalText into a DataFrame
        :return:
        """
        self.printAndLog("Reading documents")
        db = clsDatabase()
        db.connect()
        self.dfDocuments = db.execute(sql=self.readFileAsString("sql/fetchDocuments.sql"), expectingReturn=True)
        db.disconnect()

    def fetchBiologicalWords(self):
        """
        Connect to MySQL and retrieve the protein, chemical, and disease words
        :return: None
        """
        self.printAndLog("Reading biological words")
        db = clsDatabase()
        db.connect()
        self.dfBiologicalWords = db.execute(sql=self.readFileAsString("sql/fetchBiologicalWords.sql"), expectingReturn=True)
        db.disconnect()

    def buildCaseInsensitiveDictionaryOfBiologicalWords(self):
        """
        Building a dictionary where the key-value pairs represent a word and its type (protein, chemical, or disease).
        This dictionary is super-setted by clsCaseInsensitiveDictionary in order to support the multipleReplace algorithm in clsDocument
        :return: None
        """
        self.printAndLog("Building case insensitive dictionary of biological words")
        self.caseInsensitiveDictionaryOfBiologicalWords = clsCaseInsensitiveDictionary(self.dfBiologicalWords.set_index('name').to_dict()['type_reversed'])
        self.dfBiologicalWords = None  # free memory

    def loadDocuments(self):
        """
        Load document objects from rows in the DataFrame
        """
        self.printAndLog("Loading document objects")
        self.documents = [
            clsDocument(
                id=row['id'],
                originalText=row['text'],
                caseInsensitiveDictionaryOfBiologicalWords=self.caseInsensitiveDictionaryOfBiologicalWords  # pass by reference
            ) for index, row in tqdm(self.dfDocuments.iterrows(), total=len(self.dfDocuments), desc="Building document objects", unit="document")
        ]
        self.dfDocuments = None  # free memory

    def processDocuments(self):
        """
        Executes document based computation, sends a list of documents to dispatching engine in series or in parallel
        :return: None
        """
        self.printAndLog("Processing document objects")
        for document in tqdm(self.documents, desc="Processing document objects", unit="document"):
            document.execute()
        self.caseInsensitiveDictionaryOfBiologicalWords = None  # free memory

    def unloadDocuments(self):
        """
        Converts document objects to pandas DataFrame to prepare for uploading
        :return: None
        """
        self.printAndLog("Unloading document objects")
        self.dfDocuments = pd.DataFrame(data=[[document.id, document.replacedText] for document in self.documents], columns=['id', 'text'])

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
        db.uploadTableViaDataFrame(df=self.dfDocuments, tableName="cord_documents_replaced", clearTable=True)
        db.disconnect()

    def execute(self):
        """
        Execute all methods as a group of functions
        :return: None
        """
        self.checkHealth()

        self.fetchDocuments()
        self.fetchBiologicalWords()

        self.buildCaseInsensitiveDictionaryOfBiologicalWords()
        self.loadDocuments()
        self.processDocuments()
        self.unloadDocuments()

        self.exportResults()
        self.uploadResults()

