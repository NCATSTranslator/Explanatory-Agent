"""
WHAT: A simple class that represents a compound, its ID, and its synonyms
WHY: Need an object to represent a compound for the pubchem api
ASSUMES: N/A
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""


class clsCompound:
    """
    See header
    """

    def __init__(self, id):
        """
        Constructor
        :param id: Compound ID per eUtils api as an integer
        """
        self.id = id
        self.synonyms = []
