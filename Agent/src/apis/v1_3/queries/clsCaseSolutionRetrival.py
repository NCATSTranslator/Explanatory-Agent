"""
1) Retrieve all rows from xARA_CaseSolutions that have the same Case_IDs of the CaseProblems passed in to the object.
2) Assign priority to each CaseSolution row based on the "Priority" column for the KP in xARA_KP_Info. If the KP is not present for the CaseSolution, set priority to 0.
3) Sort CaseSolutions in descending priority.
4) The CaseSolution first in the list from step 3 should be held aside, including its priority.
5) For all CaseSolutions excluding the one from step 4, generate a random number between 0 and 1 and assign that to all CaseSolution priorities.
6) Sort the CaseSolution list based on priorities from step 5.(exclude first 4)
7) Insert the CaseSolution from step 4 in the ordered list from step 6 in one of two ways:
7a) If the CaseSolution from step 4 is the highest priority, insert it at the front of the list.
7b) If it is not, insert it second in the list.
8) Return the reordered list of CaseSolutions.

WHO: YR 2021-09-08
"""
import random
from modDatabase import db
import logging


class clsCaseSolutionRetrival:
    """
    See header
    """
   
    """
    Retrieve all rows from xARA_CaseSolutions that have the same Case_IDs of the CaseProblems passed in to the object.
    Assign priority to each CaseSolution row based on the "Priority" column for the KP in xARA_KP_Info. 
    If the KP is not present for the CaseSolution, set priority to 0.
    """
    sqlFetchSolutionCases = \
        """
        select
            A."CASE_ID",
            A."SOLUTION_FIRST_KP_NAME",
        case
            when "xARA_KP_Info"."Priority" IS NULL THEN 0
            else "xARA_KP_Info"."Priority" END AS "Priority" 
        from( 
            select 
                "CASE_ID", 
                "SOLUTION_FIRST_KP_NAME" 
            from "xARA_CaseSolutions" 
            where "CASE_ID" IN :caseIds
            AND "ORIGIN" = 'fromKP'
        )
        A LEFT OUTER JOIN "xARA_KP_Info"
        ON A."SOLUTION_FIRST_KP_NAME" = "xARA_KP_Info"."KP_Name"
        """


    timeoutSeconds = 60

    def __init__(self):
        self.app = None
    
        self.logs = None

    def retrieveRows_xARA_CaseSolutions(self, rows_xARA_CaseSolutions_priority, priority_index=-1):
        """
        :param similarCases_Ids: list of caseId's eg: ['Q000001', 'Q000037', 'Q000039', 'Q000040']
        """
        # logging.debug(f"Retrieved {len(rows_xARA_CaseSolutions_priority)} case solutions")
        
        """Sort CaseSolutions in descending priority."""
        # sorted_rows_xARA_CaseSolutions_priority = sorted(rows_xARA_CaseSolutions_priority, key=lambda x: (x[priority_index], x[0]), reverse=True)

        new_sort = sorted(rows_xARA_CaseSolutions_priority, key=lambda x: x[0])
        new_sort.sort(key=lambda x: x[priority_index], reverse=True)
        sorted_rows_xARA_CaseSolutions_priority = new_sort

        # TODO: reenable below code once testing concluded. Needs to be refactored to return the full rows and not just the Case Problem IDs
        return sorted_rows_xARA_CaseSolutions_priority
    
        n = 1
        first_n_rows=sorted_rows_xARA_CaseSolutions_priority[0:n]
        remaining_after_n_rows = sorted_rows_xARA_CaseSolutions_priority[n:]

        """
        For all CaseSolutions excluding the one from 4, 
        generate a random number between 0 and 1 and assign that to all CaseSolution priorities.
        """
        for i in range(0, len(remaining_after_n_rows)):
            # converting to list for replacing priority with random number
            l = list(remaining_after_n_rows[i])
            l[2] = random.random()
            remaining_after_n_rows[i] = tuple(l)
        
        # Sort the CaseSolution list based on priorities from 5.(exclude first 4)
        sorted_remaining_after_n_rows = sorted(remaining_after_n_rows, key=lambda x: x[priority_index], reverse=True)

        if(first_n_rows[0][priority_index] >= sorted_remaining_after_n_rows[0][priority_index]):
            reordered_list = first_n_rows + sorted_remaining_after_n_rows
        else: 
            reordered_list = sorted_remaining_after_n_rows
            reordered_list.insert(1, first_n_rows[0]) 

        # return caseIds from the generated list
        prioritized_case_ids = [x[0] for x in reordered_list]

        # remove duplicate case IDs
        seen = set()
        seen_add = seen.add
        deduped_prioritized_case_ids = [x for x in prioritized_case_ids if not (x in seen or seen_add(x))]

        return deduped_prioritized_case_ids

        """
        sample output: 
        ['Q000037', 'Q000040', 'Q000039', 'Q000116', 'Q000043',
        'Q000037', 'Q000001', 'Q000001', 'Q000040', 'Q000116', 'Q000001', 
        'Q000001', 'Q000037', 'Q000045', 'Q000049', 'Q000045', 'Q000045',
        'Q000043', 'Q000049', 'Q000046', 'Q000136', 'Q000039', 'Q000046',
        'Q000043', 'Q000001', 'Q000001', 'Q000116', 'Q000043', 'Q000037', 
        'Q000040', 'Q000136', 'Q000039', 'Q000040', 'Q000039', 'Q000039', 
        'Q000136', 'Q000037', 'Q000049']
        """
       

   
    
    





