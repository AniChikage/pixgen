import os
import logging
import mysql.connector



class MySQLConnector:
    def __init__(self):
        self.host = os.environ.get("mysql_host")
        self.user = os.environ.get("mysql_user")
        self.password = os.environ.get("mysql_password")
        self.database = os.environ.get("mysql_database")
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
        except mysql.connector.Error as err:
            logging.info(f"Error: {err}")

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            result = cursor.fetchall()
            return result

        except mysql.connector.Error as err:
            logging.info(f"Error: {err}")

        finally:
            if cursor:
                cursor.close()

