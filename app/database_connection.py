import logging
import mysql.connector

class DatabaseConnection:
    def __init__(self, conf):
        self.conf = conf

    def connect(self):
        """Connect to the database"""
        try:
            self.cnx = mysql.connector.connect(user=self.conf["user"],
                                               password=self.conf["password"],
                                               host=self.conf["host"],
                                               database=self.conf["database"],
                                               port=3306)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.info(
                    "Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.info("Database does not exist")
            else:
                logging.info(err)

    def execute_select(self, query):
        """Execute a select query"""
        cursor = self.cnx.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_transaction(self, queries_tup):
        """
        Execute an array of queries with parameters

        args:
            queries_tup: array of tuples with format [(query, params)]
        """
        # print(queries_tup)
        cursor = self.cnx.cursor(dictionary=True)
        for query, params in queries_tup:
            cursor.execute(query, params)
        self.cnx.commit()
        cursor.close()

    def disconnect(self):
        """Disconnect from database"""
        self.cnx.close()