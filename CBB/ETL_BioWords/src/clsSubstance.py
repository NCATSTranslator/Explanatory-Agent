"""
WHAT: A simple class that represents a substance, its ID, and its synonyms
WHY: Need an object to represent a substance for the pubchem api
ASSUMES: N/A
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""


class clsSubstance:
    """
    See header
    """

    def __init__(self, id):
        """
        Constructor
        :param id: Substance ID per eUtils api as an integer
        """
        self.id = id
        self.synonyms = []
