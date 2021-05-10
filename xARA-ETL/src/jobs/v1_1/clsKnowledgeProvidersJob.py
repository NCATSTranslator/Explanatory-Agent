import pandas as pd
import modConfig
from clsDatabase import clsDatabase
from utils.modMiscUtils import printAndLog
import os


class clsKnowledgeProvidersJob:

    def __init__(self):
        pass

    def execute(self):

        printAndLog("Starting Knowledge Providers job")

        filePathKnowledgeProviders = os.path.join(modConfig.mountPath, "v1_1", "KnowledgeProviders.csv")
        printAndLog(f"Reading {filePathKnowledgeProviders}")

        dfKnowledgeProviders = pd.read_csv(filePathKnowledgeProviders, header=0)
        dfKnowledgeProviders.sort_values(by=['Id'], ascending=True, inplace=True)

        printAndLog("Connecting to postgres host: " + modConfig.dbHost)
        db = clsDatabase()
        db.connect()

        db.uploadTableViaDataFrame(
            df=dfKnowledgeProviders,
            tableName="v1_1_KnowledgeProviders",
            clearTable=True,
            shouldCrashOnBadRow=True
        )

        printAndLog("Disconnecting from postgres")
        db.disconnect()

        printAndLog("Done!")


if __name__ == '__main__':
    job = clsKnowledgeProvidersJob()
    job.execute()
