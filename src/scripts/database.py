import os
import pysqlite3 as sql3


class DatabaseManager:
    def __init__(self, db_name="database.db"):

        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def exists(self):
        # Prüfen ob eine "database.db" Datei vorhanden ist
        return os.path.exists(self.db_name)


    # Funktion um die Datenbank zu generieren und einzurichten
    def initialize_database(self):
        try:
            if not self.exists():
                connection = sql3.connect(self.db_name)
                cursor = connection.cursor()
                print("Database created and Successfully Connected to SQLite")

                cursor.execute("""CREATE TABLE IF NOT EXISTS employees (
                    employeeId INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TXT NOT NULL,
                    Surname TXT NOT NULL,
                    Department TXT NOT NULL
                );""")
                connection.commit()

                cursor.execute("""CREATE TABLE IF NOT EXISTS devicetypes (
                    TypeId TXT PRIMARY KEY,
                    Short TXT NOT NULL
                );""")
                connection.commit()

                # ! Entfernen
                cursor.execute("""INSERT INTO devicetypes (TypeId, Short) VALUES 
                    ('Monitor', 'MON'),
                    ('Computer', 'CMP'),
                    ('Päripherie', 'DV'),
                    ('Lizenz', 'LZ');""")
                connection.commit()

                cursor.execute("""CREATE TABLE IF NOT EXISTS inventory (
                    InventarNr TEXT PRIMARY KEY,
                    Device TEXT NOT NULL,
                    Type_Id TEXT NOT NULL,
                    Assignee_Id INTEGER NOT NULL,
                    FOREIGN KEY (Type_Id) REFERENCES devicetypes(TypeId),
                    FOREIGN KEY (Assignee_Id) REFERENCES employees(employeeId)
                );""")
                connection.commit()

                cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                    option TEXT PRIMARY KEY,
                    value TEXT
                );""")
                connection.commit()

                connection.close()
                print("Database initialized")
        except Exception as e:
            print("Couldnt create Database:\n\n")
            print(e)


    # Für komplette Datenbank kontrolle ohne Rückgabewert
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
        # INSERT OR REPLACE legt eine Option an oder ersetzt ihren alten Wert.
        self.execute("INSERT OR REPLACE INTO settings (option, value) VALUES ('{}', '{}')".format(setting, value))


    # retrieving values of settings from the database settings table
    def settings_get(self, setting):
        """Get a setting from the settings table."""
        # SELECT liest genau den Wert der angeforderten Option.
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT value FROM settings WHERE option = '{}'".format(setting))
        result = self.cursor.fetchone()
        # Gibt es keinen Eintrag, liefert die Methode None zurueck.
        return result[0] if result else None


    # stores the found updates with its title and description in the database updates table
    def device_create(self, id, device, type, location):
        """Set a device in the inventory table."""
        # Die Werte kommen aus dem Formular in table.py und werden als neuer
        # Datensatz in `inventory` gespeichert.
        self.execute("PRAGMA foreign_keys = ON;")
        self.execute("INSERT INTO inventory (InventarNr, Device, Type_Id, Assignee_Id) VALUES ('{}', '{}', '{}', '{}')".format(id, device, type, location))

    def device_delete(self, id):
        """Delete a device from the inventory table."""
        # Geloescht wird ueber die eindeutige ID, nicht ueber den Geraetenamen.
        self.execute("DELETE FROM inventory WHERE InventarNr = '{}'".format(id))

    def employee_create(self, Name, Surname, Department):
        self.execute("PRAGMA foreign_keys = ON;")
        self.execute("INSERT INTO employees (Name, Surname, Department) VALUES ('{}', '{}', '{}')".format(Name, Surname, Department))

    def employee_delete(self, id):
        self.execute("DELETE FROM employees WHERE EmployeeId = '{}'".format(id,))

    def employees(self):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("""SELECT employeeId, Name, Surname FROM employees """)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows

    def type_create(self, Type, Short):
        self.execute("PRAGMA foreign_keys = ON;")
        self.execute("INSERT INTO devicetypes (TypeId, Short) VALUES ('{}', '{}')".format(Type, Short))

    def type_delete(self, id):
        self.execute("DELETE FROM devicetypes WHERE TypeId = '{}'".format(id,))

    def types(self):
        """Run a SELECT query and return (column_names, rows)."""
        # Die Suche verbindet ID, Geraet, Typ und Ort zu einem Suchbereich.
        # Dadurch findet ein Begriff Treffer in jeder sichtbaren Spalte.
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("""SELECT * FROM devicetypes """)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows

    # used to build tables which returns the column names and rows of the database updates table
    def fetch_query(self, query):
        """Run a SELECT query and return (column_names, rows)."""
        # Diese Methode fuehrt eine SELECT-Abfrage aus und gibt sowohl die
        # Spaltennamen als auch alle gefundenen Zeilen zurueck.
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
        # Die Suche verbindet ID, Geraet, Typ und Ort zu einem Suchbereich.
        # Dadurch findet ein Begriff Treffer in jeder sichtbaren Spalte.
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("""SELECT InventarNr, Device, Type, Location FROM inventory WHERE InventarNr || Device || Type || Location LIKE '%{}%'""".format(query))
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows


    # Unterstützt durch KI
    def get_next_highest_id(self, prefix):       
        # Nächste nummer für die InventarNr
        self.cursor.execute(
            "SELECT MAX(InventarNr) FROM inventory WHERE InventarNr LIKE ?", 
            (f"{prefix}%",)
        )
        result = self.cursor.fetchone()
        
        # If no items exist with this prefix yet, start at 1
        if result is None or result[0] is None:
            next_number = 1
        else:
            # result[0] is e.g., "CMP00042"
            highest_string = result[0]
            
            # 2. Cut out just the last 5 digits using string slicing [-5:]
            numeric_part = highest_string[-5:]  # Results in "00042"
            
            # 3. Convert to integer and add 1
            next_number = int(numeric_part) + 1
            
        # 4. Return the prefix combined with the newly padded 5-digit number
        return f"{next_number:05d}"
