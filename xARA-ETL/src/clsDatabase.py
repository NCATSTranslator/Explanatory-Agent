"""
WHAT: A class which manages the interface with Postgres
WHY: Need to read and write data to Postgres
ASSUMES: Postgres is running per the connection parameters
FUTURE IMPROVEMENTS: Add table upload functions, and DDL creation as required
WHO: SL 2021-05-05
"""

import psycopg2
import pandas as pd
from tqdm import tqdm
import modConfig
import logging
from io import StringIO


class clsDatabase:
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """
        self.connection = None

    def connect(self):
        """
        Connect to Postgres
        :return: None
        """
        self.connection = psycopg2.connect(
            host=modConfig.dbHost,
            port=modConfig.dbPort,
            database=modConfig.dbSchema,
            user=modConfig.dbUserName,
            password=modConfig.dbPassword,
        )
        self.connection.autocommit = False

    def disconnect(self):
        """
        Disconnect from Postgres
        :return: None
        """
        if self.connection is not None:
            self.connection.close()

    def reconnect(self):
        """
        Reconnect to Postgres
        :return: None
        """
        self.disconnect()
        self.connect()

    def execute(self, sql, expectingReturn=False):
        """
        Execute a sql query, and optional return results as a pandas DataFrame
        :param sql: Any sql statement
        :param expectingReturn: True meaning return a pandas DataFrame, False meaning no return
        :return: pandas DataFrame or None
        """
        if expectingReturn:
            return pd.read_sql(sql=sql, con=self.connection)
        else:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            cursor.close()

    def uploadTableViaDataFrame(self, df, tableName, clearTable=False, shouldCrashOnBadRow=True):
        """
        Uploads a pandas DataFrame to a given Postgres table via insert statements
        :param df: A pandas DataFrame with column names which match the target table column names
        :param tableName: A Postgres table name
        :param clearTable: Boolean whether to clear the table before uploading
        :return: None
        """
        sql = 'insert into "%s"\n("' % tableName + '","'.join(df.columns) + '")\nvalues\n(' + ",".join(["%s"]*len(df.columns)) + ")"
        cursor = self.connection.cursor()
        if clearTable:
            cursor.execute('delete from "%s"' % tableName)
        rowCounter = 0
        for row in tqdm(df.values.tolist(), desc="Uploading table %s" % tableName, unit="row"):
            try:
                cursor.execute(sql, row)
            except Exception as e:
                if shouldCrashOnBadRow:
                    raise
                else:
                    msg = "Row failure at row %s with error: %s" % (str(rowCounter), str(e))
                    print(msg)
                    logging.error(msg)
            rowCounter += 1

        cursor.close()
        self.connection.commit()

    def uploadTableViaStringIO(self, df, tableName, clearTable=False):
        """
        Here we are going save the dataframe in memory
        and use copy_from() to copy it to the table
        """
        # columns must be in the same order
        sqlTableColumns = \
            """
            select
                column_name
            from information_schema.columns
            where table_name = '%s'
            order by ordinal_position asc
            """
        tableColumns = list(self.execute(sql=sqlTableColumns % tableName, expectingReturn=True)['column_name'])

        # save dataframe to an in memory buffer
        buffer = StringIO()
        df[tableColumns].to_csv(buffer, header=False, index=False, sep="\t")
        buffer.seek(0)

        cursor = self.connection.cursor()
        if clearTable:
            cursor.execute('delete from "%s"' % tableName)
        cursor.copy_from(buffer, '"' + tableName + '"', sep="\t", null='')
        cursor.close()
        self.connection.commit()


if __name__ == '__main__':

    print("Connecting to database")
    db = clsDatabase()
    db.connect()

    print("Querying database")
    df = db.execute(sql="select current_timestamp;", expectingReturn=True)

    print("Disconnecting from database")
    db.disconnect()

    print("Done")
