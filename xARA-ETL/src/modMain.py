from jobs.v1_1.clsGlobalSimilarityJob import clsGlobalSimilarityJob
from jobs.v1_1.clsKnowledgeProvidersJob import clsKnowledgeProvidersJob
from jobs.v1_1.clsCaseSolutionsJob import clsCaseSolutionsJob

job1 = clsGlobalSimilarityJob()
job1.execute()

job2 = clsKnowledgeProvidersJob()
job2.execute()

job3 = clsCaseSolutionsJob()
job3.execute()
