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

    def initialize_database(self):
        if not self.exists():
            # Creates the database file and establishes a connection
            connection = sql3.connect(self.db_name)
            cursor = connection.cursor()
            print("Database created and Successfully Connected to SQLite")
            # Placeholder for creating the basic tables or schema
            cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            );""")
            connection.commit()
            cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                setting PRIMARY KEY,
                value TEXT
            );""")
            connection.commit()
            connection.close()
            print("Database initialized and users table created.")
        else:
            print("Database already exists.")

    def execute(self, command):
        # future running queries will be done through this method
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute(command)
        self.connection.commit()
        print("Command executed successfully.")

    def settings_set(self, setting, value):
        """Set a setting in the settings table."""
        self.execute("INSERT OR REPLACE INTO settings (setting, value) VALUES ('{}', '{}')".format(setting, value))

    def settings_get(self, setting):
        """Get a setting from the settings table."""
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT value FROM settings WHERE setting = '{}'".format(setting))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def fetch_query(self, query):
        """Run a SELECT query and return (column_names, rows)."""
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute(query)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows
