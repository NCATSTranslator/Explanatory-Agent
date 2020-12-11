"""
WHAT: A class which will:
    * Read the disease.json file and load disease objects
    * Read the protein.json file and load protein objects
    * For each protein, find and load chemicals for each protein
    * Create a unique set of disease, protein, and chemical words
    * Upload unique set of words to MySQL
WHY: Need an object which manages the entire data flow in the program
ASSUMES: 1 instance only, no need for more instances, but there's no static class in python
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""

import modConfig
import json
from tqdm import tqdm
import pandas as pd
import logging
from collections import OrderedDict
from clsProtein import clsProtein
from clsChemical import clsChemical
from clsDisease import clsDisease
from clsDatabase import clsDatabase
import urllib.parse
import requests
import os


class clsWordManager:
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """
        self.diseases = None  # a dictionary of disease objects
        self.proteins = None  # a dictionary of protein objects
        self.chemicals = None  # a dictionary of chemical objects
        self.dfWords = None  # a DataFrame to be uploaded with the biological word results

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

        self.printAndLog("Checking eUtils url")
        parsedUrl = urllib.parse.urlsplit(modConfig.eUtilsSearchUrl)
        response = requests.get(parsedUrl.scheme + "://" + parsedUrl.netloc)
        response.raise_for_status()

        self.printAndLog("Checking pubchem url")
        parsedUrl = urllib.parse.urlsplit(modConfig.pcUrl)
        response = requests.get(parsedUrl.scheme + "://" + parsedUrl.netloc)
        response.raise_for_status()

        self.printAndLog("Checking for protein file")
        if not os.path.exists(modConfig.proteinFilePath):
            raise FileNotFoundError("Missing file %s" % modConfig.proteinFilePath)

        self.printAndLog("Checking for disease file")
        if not os.path.exists(modConfig.diseaseFilePath):
            raise FileNotFoundError("Missing file %s" % modConfig.diseaseFilePath)

        self.printAndLog("Health check OK!")

    def loadDieases(self):
        """
        Load diseases.json file into disease objects
        :return: None
        """
        self.printAndLog("Reading %s" % modConfig.diseaseFilePath)
        diseaseNames = []
        with open(modConfig.diseaseFilePath) as file:
            diseaseData = json.load(file)
        for diseaseKey, diseaseMetadata in diseaseData.items():
            diseaseNames.append(diseaseMetadata["mondo_name"])  # single value
            diseaseNames += diseaseMetadata["synonyms"]  # list
        diseaseNamesUnique = sorted(list(set([diseaseName.strip() for diseaseName in diseaseNames])))
        self.diseases = OrderedDict((diseaseName, clsDisease(name=diseaseName)) for diseaseName in diseaseNamesUnique)

    def loadProteins(self):
        """
        Load proteins.json file into protein objects
        :return: None
        """
        self.printAndLog("Reading %s" % modConfig.proteinFilePath)
        proteinNames = []
        with open(modConfig.proteinFilePath) as file:
            proteinData = json.load(file)
        for proteinKey, proteinMetadata in proteinData.items():
            proteinNames.append(proteinKey)
            for proteinMetadataKey, proteinMetadataValue in proteinMetadata.items():
                if proteinMetadataKey.lower().endswith("name"):  # single value
                    proteinNames.append(proteinMetadataValue)
                elif proteinMetadataKey.lower().endswith("names"):  # list
                    proteinNames += proteinMetadataValue
        proteinNamesUnique = sorted(list(set([proteinName.strip() for proteinName in proteinNames])))
        self.proteins = OrderedDict((proteinName, clsProtein(name=proteinName)) for proteinName in proteinNamesUnique)

    def loadChemicals(self):
        """
        Execute eUtils and pubchem api calls for each protein to fetch chemicals
        return: None
        """
        self.printAndLog("Loading chemicals via api calls")
        for proteinName, protein in tqdm(self.proteins.items(), unit="protein", desc="Finding chemicals for each protein"):
            protein.execute()

        self.printAndLog("Consolidating chemicals")
        chemicalNames = []
        for proteinName, protein in tqdm(self.proteins.items(), unit="protein", desc="Creating chemical list"):
            if not protein.chemicals: continue
            chemicalNames += list(protein.chemicals.keys())

        chemicalNamesUnique = sorted(list(set([chemicalName.strip() for chemicalName in chemicalNames])))
        self.chemicals = OrderedDict((chemicalName, clsChemical(name=chemicalName)) for chemicalName in chemicalNamesUnique)

    def combineWords(self):
        """
        Create a unique set of words as a pandas DataFrame.
        Converting to lowercase and stripping whitespace, and then dropping duplicates that occur in any other list.
        :return: None
        """
        self.printAndLog("Combining words")
        words = [[proteinName, "protein"] for proteinName in self.proteins.keys()] +\
                [[chemicalName, "chemical"] for chemicalName in self.chemicals.keys()] +\
                [[diseaseName, "disease"] for diseaseName in self.diseases.keys()]

        self.dfWords = pd.DataFrame(data=words, columns=["name", "type"])

        # release memory
        self.proteins = None
        self.chemicals = None
        self.diseases = None

    def exportResults(self):
        """
        Export results for debugging purposes
        :return: None
        """
        self.printAndLog("Exporting results for debugging purposes")
        self.dfWords.to_csv(modConfig.biologicalWordsOutputFilePath, index=False, line_terminator="\n")

    def uploadResults(self):
        """
        Uploads all document output text to MySQL
        :return: None
        """
        db = clsDatabase()
        db.connect()
        db.uploadTableViaDataFrame(df=self.dfWords, tableName="biological_words", clearTable=True)
        db.disconnect()

    def execute(self):
        """
        Execute all methods as a group of functions
        :return: None
        """
        self.checkHealth()
        self.loadDieases()
        self.loadProteins()
        self.loadChemicals()
        self.combineWords()
        self.exportResults()
        self.uploadResults()

