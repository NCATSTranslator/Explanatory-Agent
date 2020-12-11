"""
WHAT: A class which represents a single document with its metadata and methods.
A document represents the original text and the methods to replace certain text with backwards keywords as masked flags.
This class is meant to be single-threaded since it all shares a reference to the case insensitive dictionary.
This class knows how to read and combined all of its own metadata to prepare for export to MySQL.
WHY: Need an object which encapsulates a single document.
ASSUMES: Single-threaded, all sharing a reference to caseInsensitiveDictionaryOfBiologicalWords
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-01
"""

import nltk


class clsDocument:
    """
    See header
    """

    def __init__(self, id, originalText, caseInsensitiveDictionaryOfBiologicalWords):
        """
        Constructor
        The unique id was created because:
        ReleaseDate gives traceability into which release of the cord-19 dataset
        RowId gives the row number in the metadata.csv file
        CordUid gives the supposedly unique identifier of the document, however there are duplicates due to multiple submissions of the same document
        DocumentType gives either 'pdf' or 'pmc' from the metadata.csv, sometimes there is both listed
        DocumentDuplicationCount gives how many times this occurs through string splitting the file path on ";", giving multiple documents
        :param id: The artificially created unique document id (ReleaseDate + RowId + CordUid + DocumentType + DocumentDuplicateCount)
        :param originalText: The original text string body on which to perform replacement
        :param caseInsensitiveDictionaryOfBiologicalWords: A dictionary which is super-setted by clsCaseInsensitiveDictionary; required for lambda method in multipleReplaceAlgorithm
        """
        self.id = id
        self.originalText = originalText
        self.caseInsensitiveDictionaryOfBiologicalWords = caseInsensitiveDictionaryOfBiologicalWords

        self.replacedText = None

    def replaceBiologicalWordsWithBackwardsWords(self):
        """
        If a protein, chemical, or disease is identified, then replace it with that backwards identifier.
        For example, if a protein from the document originalText is found in the proteinWords set, then replace it with "nietorp".
        For example, if a chemical from the document originalText is found in the chemicalWords set, then replace it with "lacimehc".
        For example, if a disease from the document originalText is found in the diseaseWords set, then replace it with "esaesid".
        :return: None
        """

        pattern = r'''(?x)          # set flag to allow verbose regexps
                (?:[A-Z]\.)+        # abbreviations, e.g. U.S.A.
              | \w+(?:-\w+)*        # words with optional internal hyphens
              | \$?\d+(?:\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
              | \.\.\.              # ellipsis
              | [][.,;"'?():_`-]    # these are separate tokens; includes ], [
            '''

        tokenWords = nltk.tokenize.regexp_tokenize(self.originalText.strip(), pattern, gaps=False)
        tokenGaps = nltk.tokenize.regexp_tokenize(self.originalText.strip(), pattern, gaps=True, discard_empty=False)[1:]  # ignore first blank string

        # replace words
        replacedTokenWords = [None] * len(tokenWords)
        for i, tokenWord in enumerate(tokenWords):
            # if the token is a short word, ignore it
            if len(tokenWord) < 3:
                replacedTokenWords[i] = tokenWord
                continue

            replacedTokenWord = self.caseInsensitiveDictionaryOfBiologicalWords.get(tokenWord)
            if not replacedTokenWord and tokenWord.endswith("."):
                replacedTokenWord = self.caseInsensitiveDictionaryOfBiologicalWords.get(tokenWord[:-1])
                if replacedTokenWord:
                    replacedTokenWord += "."
            if replacedTokenWord:
                replacedTokenWords[i] = replacedTokenWord
            else:
                replacedTokenWords[i] = tokenWord

        # rebuild text
        totalTokenLength = len(tokenWords) + len(tokenGaps)
        wordCounter = 0
        gapCounter = 0
        allTokens = [None] * totalTokenLength
        for i in range(totalTokenLength):
            if i % 2 == 0:
                allTokens[i] = replacedTokenWords[wordCounter]  # use tokenWords to check original
                wordCounter += 1
            elif i % 2 == 1:
                allTokens[i] = tokenGaps[gapCounter]
                gapCounter += 1
        self.replacedText = "".join(allTokens)

    def freeMemory(self):
        """
        Release unused memory we don't need those anymore, garbage collection makes the code slow.
        The code is still holding onto these instances so it doesn't know to release these properties.
        We are preserving only the id and replacedText properties.
        This document class knows nothing of the other document classes.
        :return: None
        """
        self.originalText = None

    def execute(self):
        """
        Execute all computation for this document as a group of functions
        :return: None
        """
        self.replaceBiologicalWordsWithBackwardsWords()
        self.freeMemory()


