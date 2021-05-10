import pandas as pd
import os
import modConfig
from clsDatabase import clsDatabase
from utils.modMiscUtils import printAndLog
import numpy as np


class clsCaseSolutionsJob:

    def __init__(self):
        pass

    def execute(self):

        printAndLog("Starting Case Solutions job")

        filePathCaseSolutions = os.path.join(modConfig.mountPath, "v1_1", "CaseSolutions.csv")
        printAndLog(f"Reading {filePathCaseSolutions}")

        dfCaseSolutions = pd.read_csv(filePathCaseSolutions, header=0)

        dfCaseSolutions.rename(columns={
            "SOLUTION_ID": "Id",
            "CASE_ID": "CaseId",
            "ORIGIN": "Origin",

            "SOLUTION_NO_KP": "KnowledgeProviderPathCount",
            "SOLUTION_FIRST_KP_NAME": "KnowledgeProviderPath1Name",
            "SOLUTION_SECOND_KP_NAME": "KnowledgeProviderPath2Name",

            "NODE1_PATH1_CATEGORY": "Node1Path1Category",
            "NODE1_PATH1_TYPE": "Node1Path1Type",
            "NODE1_PATH1_REFERENCE": "Node1Path1Reference",

            "NODE2_PATH1_CATEGORY": "Node2Path1Category",
            "NODE2_PATH1_TYPE": "Node2Path1Type",
            "NODE2_PATH1_REFERENCE": "Node2Path1Reference",

            "EDGE1_PATH1_PREDICATE": "Edge1Path1Predicate",
            "EDGE1_PATH1_ENDS": "Edge1Path1Ends",
            "EDGE1_PATH1_REFERENCE": "Edge1Path1Reference",

            "NODE1_PATH2_CATEGORY": "Node1Path2Category",
            "NODE1_PATH2_TYPE": "Node1Path2Type",
            "NODE1_PATH2_REFERENCE": "Node1Path2Reference",

            "NODE2_PATH2_CATEGORY": "Node2Path2Category",
            "NODE2_PATH2_TYPE": "Node2Path2Type",
            "NODE2_PATH2_REFERENCE": "Node2Path2Reference",

            "EDGE1_PATH2_PREDICATE": "Edge1Path2Predicate",
            "EDGE1_PATH2_ENDS": "Edge1Path2Ends",
            "EDGE1_PATH2_REFERENCE": "Edge1Path2Reference",
        }, inplace=True)

        dfCaseSolutions = dfCaseSolutions.replace({np.nan: None})

        printAndLog("Connecting to postgres host: " + modConfig.dbHost)
        db = clsDatabase()
        db.connect()

        printAndLog("Uploading table v1_1_CaseSolutions")
        db.uploadTableViaStringIO(
            df=dfCaseSolutions,
            tableName="v1_1_CaseSolutions",
            clearTable=True,
        )

        printAndLog("Disconnecting from postgres")
        db.disconnect()

        printAndLog("Done!")


if __name__ == '__main__':
    job = clsCaseSolutionsJob()
    job.execute()
