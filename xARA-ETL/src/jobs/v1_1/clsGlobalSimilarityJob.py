import pandas as pd
import os
from tqdm import tqdm
import modConfig
from clsDatabase import clsDatabase
from utils.modMiscUtils import printAndLog


class clsGlobalSimilarityJob:

    def __init__(self):
        pass

    def execute(self):

        printAndLog("Starting Global Similarity job")

        filePathGlobalSimilarity = os.path.join(modConfig.mountPath, "v1_1", "GlobalSimilarity.csv")
        printAndLog(f"Reading {filePathGlobalSimilarity}")

        dfGlobalSimilarityRaw = pd.read_csv(filePathGlobalSimilarity, header=0)

        printAndLog("Expanding data")
        data = []
        for index, row in tqdm(dfGlobalSimilarityRaw.iterrows(), unit="rows", total=len(dfGlobalSimilarityRaw), desc="Expanding data"):

            for column in dfGlobalSimilarityRaw.columns:
                if not column.startswith("Q"): continue
                data.append([
                    row['Subject_category'],
                    row['Object_category'],
                    row['Predicate'],
                    column,
                    row[column]
                ])

        printAndLog("Creating output DataFrame")
        dfGlobalSimilarity = pd.DataFrame(
            data=data,
            columns=["Subject", "Object", "Predicate", "CaseId", "CaseValue"]
        )
        numRowsWithDuplicates = len(dfGlobalSimilarity)

        printAndLog("Dropping duplicate rows")
        dfGlobalSimilarity.drop_duplicates(
            subset=["Subject", "Object", "Predicate", "CaseId"],
            keep="first",
            inplace=True
        )
        numRowsWithoutDuplicates = len(dfGlobalSimilarity)
        numDuplicates = numRowsWithDuplicates - numRowsWithoutDuplicates

        printAndLog(f"Number of rows with duplicates: " + str(numRowsWithDuplicates))
        printAndLog(f"Number of rows without duplicates: " + str(numRowsWithoutDuplicates))
        printAndLog(f"Number of duplicate rows: " + str(numDuplicates))

        printAndLog("Adding Id column")
        dfGlobalSimilarity["Id"] = list(range(1, (len(dfGlobalSimilarity) + 1)))

        printAndLog("Connecting to postgres host: " + modConfig.dbHost)
        db = clsDatabase()
        db.connect()

        printAndLog("Uploading table v1_1_GlobalSimilarity")
        db.uploadTableViaStringIO(
            df=dfGlobalSimilarity,
            tableName="v1_1_GlobalSimilarity",
            clearTable=True,
        )

        printAndLog("Disconnecting from postgres")
        db.disconnect()

        printAndLog("Done!")


if __name__ == '__main__':
    job = clsGlobalSimilarityJob()
    job.execute()
