"""
WHAT: A class which represents a single protein and its name, along with several methods to extract chemicals:
    * Search eUtils-search for all assay IDs for this protein
    * Search pubchem for all substance IDs for the assay IDs
    * Search pubchem for all substance synonyms for the substance IDs
    * Search pubchem for all compound IDs for the assay IDs
    * Search pubchem for all compound synonyms for the compound IDs
    * Create a set of chemicals based on the unique set of compound synonyms and substance synonyms
WHY: Need an object which encapsulates a protein and can search for its related chemicals.
ASSUMES: Internet connectivity to eUtils and pubchem apis, and caching to disk.
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""

from clsAssay import clsAssay
from clsSubstance import clsSubstance
from clsCompound import clsCompound
from clsChemical import clsChemical
import requests
import xmltodict
import json
import modConfig
from collections import OrderedDict
import logging
import time


class clsProtein:
    """
    See header
    """

    def __init__(self, name):
        """
        Constructor
        :param name: A protein name as a string
        """
        self.name = name
        self.assays = None
        self.substances = None
        self.compounds = None
        self.chemicals = None

    def getAssays(self):
        """
        Search eUtils-search api for protein name and return the assay IDs to create assay objects
        :return: None
        """
        for requestTryCount in range(modConfig.maxRequestTryCount):
            try:
                response = requests.get(
                    url=modConfig.eUtilsSearchUrl,
                    params={
                        "api_key": modConfig.eUtilsApiKey,
                        "db": modConfig.eUtilsAssayDatabase,
                        "term": '"%s [Homo sapiens]"[Protein Target Name]' % self.name
                    }
                )
                response.raise_for_status()
                break
            except Exception:
                if requestTryCount == (modConfig.maxRequestTryCount - 1):
                    raise
                else:
                    time.sleep(modConfig.requestTryDelaySeconds)

        data = xmltodict.parse(response.text)
        assayCount = int(data['eSearchResult']['Count'])
        if assayCount == 0: return
        assayIds = data['eSearchResult']['IdList']['Id']
        self.assays = OrderedDict((int(assayId), clsAssay(id=int(assayId))) for assayId in sorted(assayIds) if int(assayId) > 0)

    def getSubstances(self):
        """
        Search pubchem api for assay IDs and return the substance IDs to create substance objects
        :return: None
        """
        for requestTryCount in range(modConfig.maxRequestTryCount):
            try:
                response = requests.post(
                    url=modConfig.pcUrl + modConfig.pcAssayDatabase + "/aid/sids/json",
                    data={"aid": ",".join(map(str, sorted(list(self.assays.keys()))))},
                    params={"sids_type": "active"}
                )
                if response.status_code == 404:
                    msg = "Ignoring a 404"
                    print(msg)
                    logging.warning(msg)
                    return
                elif response.status_code != 200:
                    response.raise_for_status()
                break
            except Exception:
                if requestTryCount == (modConfig.maxRequestTryCount - 1):
                    raise
                else:
                    time.sleep(modConfig.requestTryDelaySeconds)

        data = json.loads(response.text)
        self.substances = OrderedDict()
        for assayResult in data['InformationList']['Information']:
            if 'SID' not in assayResult: continue
            for substanceId in assayResult['SID']:
                if substanceId not in self.substances:
                    self.substances[substanceId] = clsSubstance(id=substanceId)

    def getSubstancesSynonyms(self):
        """
        Search pubchem api for substance IDs and return the synonyms to assign to the substance objects
        :return: None
        """
        for requestTryCount in range(modConfig.maxRequestTryCount):
            try:
                response = requests.post(
                    url=modConfig.pcUrl + modConfig.pcSubstanceDatabase + "/sid/synonyms/json",
                    data={"sid": ",".join(map(str, sorted(list(self.substances.keys()))))}
                )
                response.raise_for_status()
                break
            except Exception:
                if requestTryCount == (modConfig.maxRequestTryCount - 1):
                    raise
                else:
                    time.sleep(modConfig.requestTryDelaySeconds)

        data = json.loads(response.text)
        for substanceResult in data['InformationList']['Information']:
            if 'SID' not in substanceResult or 'Synonym' not in substanceResult: continue
            if substanceResult['SID'] not in self.substances: raise AttributeError
            self.substances[substanceResult['SID']].synonyms += substanceResult['Synonym']

    def getCompounds(self):
        """
        Search pubchem api for assay IDs and return the compound IDs to create compound objects
        :return: None
        """
        for requestTryCount in range(modConfig.maxRequestTryCount):
            try:
                response = requests.post(
                    url=modConfig.pcUrl + modConfig.pcAssayDatabase + "/aid/cids/json",
                    data={"aid": ",".join(map(str, sorted(list(self.assays.keys()))))},
                    params={"cids_type": "active"}
                )
                if response.status_code == 404:
                    msg = "Ignoring a 404"
                    print(msg)
                    logging.warning(msg)
                    return
                elif response.status_code != 200:
                    response.raise_for_status()
                break
            except Exception:
                if requestTryCount == (modConfig.maxRequestTryCount - 1):
                    raise
                else:
                    time.sleep(modConfig.requestTryDelaySeconds)

        data = json.loads(response.text)
        self.compounds = OrderedDict()
        for assayResult in data['InformationList']['Information']:
            if 'CID' not in assayResult: continue
            for compoundId in assayResult['CID']:
                if compoundId not in self.compounds:
                    self.compounds[compoundId] = clsCompound(id=compoundId)

    def getCompoundsSynonyms(self):
        """
        Search pubchem api for compound IDs and return the synonyms to assign to the compound objects
        :return: None
        """
        for requestTryCount in range(modConfig.maxRequestTryCount):
            try:
                response = requests.post(
                    url=modConfig.pcUrl + modConfig.pcCompoundDatabase + "/cid/synonyms/json",
                    data={"cid": ",".join(map(str, sorted(list(self.compounds.keys()))))}
                )
                response.raise_for_status()
                break
            except Exception:
                if requestTryCount == (modConfig.maxRequestTryCount - 1):
                    raise
                else:
                    time.sleep(modConfig.requestTryDelaySeconds)

        data = json.loads(response.text)
        for compoundResult in data['InformationList']['Information']:
            if 'CID' not in compoundResult or 'Synonym' not in compoundResult: continue
            if compoundResult['CID'] not in self.compounds: raise AttributeError
            self.compounds[compoundResult['CID']].synonyms += compoundResult['Synonym']

    def getChemicals(self):
        """
        Create chemical objects from the unique set of compound and substance synonyms
        :return: None
        """
        chemicalNames = []
        for compoundId, compound in self.compounds.items():
            chemicalNames += compound.synonyms
        for substanceId, substance in self.substances.items():
            chemicalNames += substance.synonyms
        self.chemicals = OrderedDict((chemicalName, clsChemical(name=chemicalName)) for chemicalName in sorted(list(set(chemicalNames))))

    def freeMemory(self):
        """
        Release unused memory we don't need those anymore, garbage collection makes the code slow.
        The code is still holding onto these instances so it doesn't know to release these properties.
        We are preserving only the name and the list of chemicals because we have to combine them later.
        This protein class knows nothing of the other protein classes.
        :return: None
        """
        self.assays = None
        self.substances = None
        self.compounds = None

    def execute(self):
        """
        Execute all methods of the object as a group of functions
        :return: None
        """
        self.getAssays()
        if not self.assays: return

        self.getSubstances()
        if self.substances:
            self.getSubstancesSynonyms()

        self.getCompounds()
        if self.compounds:
            self.getCompoundsSynonyms()

        if self.substances or self.compounds:
            self.getChemicals()

        self.freeMemory()
