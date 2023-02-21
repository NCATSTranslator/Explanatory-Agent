"""
WHAT: Central source for Knowledge Type checks and labels
WHY: Checking the knowledge_type predicate property is used across multiple classes. Defining everything in one class will ensure nothing is missed if a value changes in the future.
ASSUMES: None
FUTURE IMPROVEMENTS:
WHO: TZ 2023-01-16
"""
from typing import List
import warnings


class clsKnowledgeType:
    LOOKUP: str = 'lookup'
    INFERRED: str = 'inferred'
    CREATIVE_MODE: str = 'inferred'
    LOOKUP_THRESHOLD_COLUMN: str = 'REGULAR_GLOBAL_QUERY_THRESHOLD'
    LOOKUP_MAX_CASES: int = 1
    LOOKUP_ORIGINS: List[str] = ['fromKP']
    INFERRED_THRESHOLD_COLUMN: str = 'CREATIVE_GLOBAL_QUERY_THRESHOLD'
    INFERRED_MAX_CASES: int = 2
    INFERRED_ORIGINS: List[str] = ['derived']

    @staticmethod
    def origins(knowledge_type: str) -> List[str]:
        """
        If the query is "creative" then always include both origin types, otherwise include fromKP only
        :param knowledge_type: Knowledge type to check
        :return: List of origins to use in clsBiolinkSimilarity
        """
        if knowledge_type == clsKnowledgeType.LOOKUP:
            return clsKnowledgeType.LOOKUP_ORIGINS
        elif knowledge_type == clsKnowledgeType.INFERRED:
            return clsKnowledgeType.INFERRED_ORIGINS
        else:
            warnings.warn(f"Unknown knowledge type: '{knowledge_type}'! Returning as lookup.")
            return clsKnowledgeType.LOOKUP_ORIGINS

    @staticmethod
    def config_query(knowledge_type: str) -> str:
        if knowledge_type == clsKnowledgeType.LOOKUP:
            threshold_column = clsKnowledgeType.LOOKUP_THRESHOLD_COLUMN
        elif knowledge_type == clsKnowledgeType.INFERRED:
            threshold_column = clsKnowledgeType.INFERRED_THRESHOLD_COLUMN
        else:
            warnings.warn(f"Unknown knowledge type: '{knowledge_type}'! Returning as lookup.")
            threshold_column = clsKnowledgeType.LOOKUP_THRESHOLD_COLUMN

        return f'SELECT "{threshold_column}", "GLOBAL_PRECISION", "MAX_REUSE", "SECOND_HIGHEST_MAX_REUSE" FROM public."xARA_Config";'

    @staticmethod
    def max_cases(knowledge_type: str) -> int:
        if knowledge_type == clsKnowledgeType.LOOKUP:
            return clsKnowledgeType.LOOKUP_MAX_CASES
        elif knowledge_type == clsKnowledgeType.INFERRED:
            return clsKnowledgeType.INFERRED_MAX_CASES
        else:
            warnings.warn(f"Unknown knowledge type: '{knowledge_type}'! Returning as lookup.")
            return clsKnowledgeType.LOOKUP_MAX_CASES
