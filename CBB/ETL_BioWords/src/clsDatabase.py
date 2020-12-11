"""
WHAT: A class which which manages the interface with MySQL
WHY: Need to read and write data to MySQL
ASSUMES: MySQL is running per the connection parameters
FUTURE IMPROVEMENTS: Add table upload functions, and DDL creation as required
WHO: SL 2020-08-13
"""

import mysql.connector as mysql
import pandas as pd
from tqdm import tqdm
import modConfig
import logging
import os


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
        Connect to MySQL
        :return: None
        """
        self.connection = mysql.connect(host='host.docker.internal' if modConfig.isDocker else 'localhost', port=12345, database='cord-bert', user='root', password='corddatabase', autocommit=False, option_files="my.cnf")

    def disconnect(self):
        """
        Disconnect from MySQL
        :return: None
        """
        if self.connection is not None:
            self.connection.close()

    def reconnect(self):
        """
        Reconnect to MySQL
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
        Uploads a pandas DataFrame to a given MySQL table via insert statements
        :param df: A pandas DataFrame with column names which match the target table column names
        :param tableName: A MySQL table name
        :param clearTable: Boolean whether to clear the table before uploading
        :return: None
        """
        sql = "insert into `%s`\n(`" % tableName + "`,`".join(df.columns) + "`)\nvalues\n(" + ",".join(["%s"]*len(df.columns)) + ")"
        cursor = self.connection.cursor()
        if clearTable:
            cursor.execute("delete from `%s`" % tableName)
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

    def uploadTableViaCsvFile(self, fileName, tableName, columnNames=None, clearTable=False):
        """
        Uploads a pandas DataFrame to a given MySQL table via local csv file.
        NOTE Server must have local_infile turned on
            set @@global.local_infile = 1
        NOTE Client must have local_infile enabled in its .cnf file
            [client]
            allow_local_infile=ON
        :param fileName: A comma separated text file with equivalent of pd.to_csv( , index=False, line_terminator='\n')
        :param tableName: A MySQL table name
        :param clearTable: Boolean whether to clear the table before uploading
        :return: None
        """
        sql = \
            """
            LOAD DATA LOCAL INFILE '%s' INTO TABLE `%s`
            FIELDS TERMINATED BY ',' 
            ENCLOSED BY '"' 
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            """ % (fileName.replace(os.sep, '/'), tableName)  # os.sep is to handle windows file paths

        if columnNames is not None:
            sql += "\n(`" + "`,`".join(columnNames) + "`)"
        sql += ";"

        cursor = self.connection.cursor()
        if clearTable:
            cursor.execute("delete from `%s`" % tableName)
        cursor.execute(sql)
        cursor.close()
        self.connection.commit()


if __name__ == '__main__':

    print("Connecting to database")
    db = clsDatabase()
    db.connect()

    print("Querying database")
    df = db.execute(sql="select current_timestamp", expectingReturn=True)
    print(df)

    print("Disconnecting from database")
    db.disconnect()

    print("Done")
