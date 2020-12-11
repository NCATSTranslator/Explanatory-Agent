"""
WHAT: A simple class that represents an assay and its ID
WHY: Need an object to represent an assay for the eUtils + pubchem api
ASSUMES: N/A
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""


class clsAssay:
    """
    See header
    """

    def __init__(self, id):
        """
        Constructor
        :param id: Assay ID per eUtils api as an integer
        """
        self.id = id
