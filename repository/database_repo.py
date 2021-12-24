import sqlite3

class DatabaseRepository:

    def __init__(self,):
        self.path = "data/database.db"


    def select(self, sql_statement, args = (), row_type = sqlite3.Row):
        
        connection = sqlite3.connect(self.path)

        if row_type is not None:
            connection.row_factory = row_type
            
        cursor = connection.cursor()
        cursor.execute(sql_statement, args)
        data = cursor.fetchall()
        connection.close()

        return data


    def general_statement(self, sql_statement, args = None):
        """
        Used for `insert` and `update`

        Args:
            sql_statement (string): The SQL statement
            args (tuple, optional): Statement's arguments. Defaults to None.
        """
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        cursor.execute(sql_statement, args)
        connection.commit()
        connection.close()  


    def delete(self, sql_statement, args = None):
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        cursor.execute(sql_statement, args)
        connection.commit()
        connection.close()  

        return cursor.rowcount