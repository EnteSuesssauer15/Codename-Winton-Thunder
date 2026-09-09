import os
import pysqlite3 as sql3


class DatabaseManager:

    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    # startup check wether database exists or not, returns True if exists, False if not
    def exists(self):
        # Check if the database file exists
        return os.path.exists(self.db_name)


    # startup method to create a missing database and the required tables inside 
    def initialize_database(self):
        if not self.exists():
            # Creates the database file and establishes a connection
            connection = sql3.connect(self.db_name)
            cursor = connection.cursor()
            print("Database created and Successfully Connected to SQLite")
            # Placeholder for creating the basic tables or schema
            cursor.execute("""CREATE TABLE IF NOT EXISTS inventory (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Device TEXT NOT NULL,
                Type TEXT NOT NULL,
                Location TEXT NOT NULL
            );""")
            connection.commit()
            cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                option TEXT PRIMARY KEY,
                value TEXT
            );""")
            connection.commit()
            connection.close()
            print("Database initialized and updates table created.")
        else:
            print("Database already exists.")


    # used for full database control, like creating tables, inserting data, etc.
    def execute(self, command):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute(command)
        self.connection.commit()
        print("Command executed successfully.")


    # setting values to settings table in the database
    def settings_set(self, setting, value):
        """Set a setting in the settings table."""
        self.execute("INSERT OR REPLACE INTO settings (option, value) VALUES ('{}', '{}')".format(setting, value))


    # retrieving values of settings from the database settings table
    def settings_get(self, setting):
        """Get a setting from the settings table."""
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT value FROM settings WHERE option = '{}'".format(setting))
        result = self.cursor.fetchone()
        return result[0] if result else None


    # stores the found updates with its title and description in the database updates table
    def device_create(self, device, type, location):
        """Set a device in the inventory table."""
        self.execute("INSERT OR REPLACE INTO inventory (device, type, location) VALUES ('{}', '{}', '{}')".format(device, type, location))

    def device_delete(self, id):
        """Delete a device from the inventory table."""
        self.execute("DELETE FROM inventory WHERE ID = {}".format(id))

    # used to build tables which returns the column names and rows of the database updates table
    def fetch_query(self, query):
        """Run a SELECT query and return (column_names, rows)."""
        if not self.connection:
            self.connection = sql3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.connection.cursor()
        self.cursor.execute(query)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows


    # used to search for updates in the database based on a simple term
    def search(self, query):
        """Run a SELECT query and return (column_names, rows)."""
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("""SELECT id, device, type, location FROM inventory WHERE id || device || type || location LIKE '%{}%'""".format(query))
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows


    # acts as check to prevent double entries when checking for updates
    def check(self, title):
        """Return True if an update with this title is already in the database."""
        connection = sql3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT 1 FROM inventory WHERE device = ? LIMIT 1",
            (title,)
        )
        row = cursor.fetchone()
        connection.close()
        print(row)
        return row is not None