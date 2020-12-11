"""
WHAT: A simple class that represents a disease and its name
WHY: Need an object to represent a disease
ASSUMES: N/A
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""


class clsDisease:
    """
    See header
    """

    def __init__(self, name):
        """
        Constructor
        :param name: A disease name as a string
        """
        self.name = name