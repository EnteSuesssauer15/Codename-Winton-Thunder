import os
import pysqlite3 as sql3


class DatabaseManager:

    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def exists(self):
        # Check if the database file exists
        return os.path.exists(self.db_name)
    
    def create_database(self):
        # Creates the database file and establishes a connection
        connection = sql3.connect(self.db_name)
        cursor = connection.cursor()
        print("Database created and Successfully Connected to SQLite")
        print("created")
        return connection, cursor
    
    def initialize_database(self):
        # Placeholder for creating the basic tables or schema if the database doesn't exist
        if not self.exists():
            connection, cursor = self.create_database()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            );""")
            connection.commit()
            connection.close()
            print("Database initialized and users table created.")
        else:
            print("Database already exists.")

    def execute(self, command):
        # future running queries will be done through this method
        if not self.connection:
            self.connect()
        self.cursor.execute(command)
        self.connection.commit()
        print("Command executed successfully.")
