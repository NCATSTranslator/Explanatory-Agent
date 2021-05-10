"""
WHAT: A class which represents the predicates supported by this api the logic involved with the clsAgentView
WHY: Need a class to handle data specific logic outside of clsAgentView to separate concerns
ASSUMES: N/A
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-12-14
"""


class clsPredicates:
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """

        # don't change these variable names, they are exposed to the client
        self.disease = {"gene": ["associated"]}
