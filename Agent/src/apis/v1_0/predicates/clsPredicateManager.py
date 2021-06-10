"""
WHAT: A class which generates the user response predicates from the query manager
WHY: Removes this logic from the view, and puts in a testable class
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-04-25
"""

from ..queries.clsQueryManager import clsQueryManager


class clsPredicateManager:
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """
        self.userResponsePredicates = None

    def generateUserResponsePredicates(self):
        """
        Method to tell users which predicates we support by walking the predicates of the registered queries.
        :return: None
        """

        userResponsePredicates = {}
        for registeredQueryClass in clsQueryManager.registeredQueryClasses:
            registeredQuery = registeredQueryClass(None)
            for subject, objectPredicates in registeredQuery.predicates.items():
                if subject not in userResponsePredicates:
                    userResponsePredicates[subject] = {}
                for object, predicates in objectPredicates.items():
                    if object not in userResponsePredicates[subject]:
                        userResponsePredicates[subject][object] = set()
                    userResponsePredicates[subject][object] |= set(predicates)

        # convert all finalized sets to sorted lists for consistency.
        for subject, objectPredicates in userResponsePredicates.items():
            for object in objectPredicates.keys():
                userResponsePredicates[subject][object] = sorted(list(userResponsePredicates[subject][object]))

        self.userResponsePredicates = userResponsePredicates
