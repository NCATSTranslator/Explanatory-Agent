"""
WHAT: A class which represents the predicates supported by this api the logic involved with the clsAgentView
WHY: Need a class to handle data specific logic outside of clsAgentView to separate concerns
ASSUMES: N/A
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-12-14
"""

from apis.v1_0.views.clsQueryView import clsQueryView


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

    @staticmethod
    def return_accepted():
        return_predicates = {}
        for view in clsQueryView.registered_query_views:
            for subject, object_predicates in view.predicates().items():
                if subject not in return_predicates:
                    return_predicates[subject] = {}
                for obj, predicates in object_predicates.items():
                    if obj not in return_predicates[subject]:
                        return_predicates[subject][obj] = set()
                    return_predicates[subject][obj] |= set(predicates)

        # convert all finalized sets to sorted lists for consistency.
        for subject, object_predicates in return_predicates.items():
            for obj in object_predicates.keys():
                return_predicates[subject][obj] = sorted(list(return_predicates[subject][obj]))

            # return_predicates.update(view.predicates())

        return return_predicates
