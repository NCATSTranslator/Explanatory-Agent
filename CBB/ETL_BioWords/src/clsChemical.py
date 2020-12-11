"""
WHAT: A simple class that represents a chemical and its name
WHY: Need an object to represent a chemical
ASSUMES: N/A
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""


class clsChemical:
    """
    See header
    """

    def __init__(self, name):
        """
        Constructor
        :param name: A chemical name as a string
        """
        self.name = name