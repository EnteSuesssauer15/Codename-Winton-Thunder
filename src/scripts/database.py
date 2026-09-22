import os
import pysqlite3 as sql3


class DatabaseManager:
    """Kleine Hilfsklasse fuer alle Zugriffe auf die lokale SQLite-Datenbank."""

    def __init__(self, db_name="database.db"):
        # Der Dateiname wird von main.py uebergeben. Verbindung und Cursor
        # werden erst geoeffnet, wenn eine Abfrage wirklich gebraucht wird.
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    # startup check wether database exists or not, returns True if exists, False if not
    def exists(self):
        # Eine SQLite-Datenbank ist in diesem Projekt einfach eine Datei.
        # Diese Pruefung sagt noch nichts darueber aus, ob die Tabellen korrekt
        # sind; sie prueft nur, ob die Datei vorhanden ist.
        return os.path.exists(self.db_name)


    # startup method to create a missing database and the required tables inside 
    def initialize_database(self):
        if not self.exists():
            # `connect` erstellt die Datei, falls sie noch nicht existiert.
            # Ueber die Verbindung werden danach SQL-Befehle ausgefuehrt.
            connection = sql3.connect(self.db_name)
            cursor = connection.cursor()
            print("Database created and Successfully Connected to SQLite")

            # `inventory` speichert jedes Geraet. ID wird automatisch vergeben;
            # die drei Textfelder duerfen nicht leer sein (NOT NULL).
            cursor.execute("""CREATE TABLE IF NOT EXISTS inventory (
                InventarNr TEXT PRIMARY KEY,
                Device TEXT NOT NULL,
                Type TEXT NOT NULL,
                Location TEXT NOT NULL
            );""")
            connection.commit()


            # eigene datenbank für auswählbare optionen im menü
            # legt den wert für die inventarnummer fest
            cursor.execute("""CREATE TABLE IF NOT EXISTS devicetypes (
                ID TEXT PRIMARY KEY,
                Device TEXT NOT NULL,
                Key TEXT NOT NULL
            );""")
            connection.commit()

            cursor.execute("""INSERT INTO devicetypes (Device, Key) VALUES 
                ('Monitor', 'MON'),
                ('Computer', 'CMP'),
                ('Päripherie', 'DV'),
                ('Lizenz', 'LZ');""")
            connection.commit()

            # In `settings` koennen spaeter Optionen wie der Dark Mode liegen.
            # `option` ist der Schluessel und darf daher nur einmal vorkommen.
            cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                option TEXT PRIMARY KEY,
                value TEXT
            );""")
            connection.commit()
            connection.close()
            print("Database initialized and updates table created.")
        else:
            # Die vorhandene Datei wird nicht ueberschrieben. So bleiben die
            # bereits gespeicherten Geraete beim Neustart erhalten.
            print("Database already exists.")


    # used for full database control, like creating tables, inserting data, etc.
    def execute(self, command):
        # Diese Methode ist fuer Schreibbefehle gedacht, zum Beispiel INSERT
        # oder DELETE. Eine Verbindung wird nur einmal pro Manager aufgebaut.
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute(command)
        self.connection.commit()
        # `commit` bestaetigt die Aenderung dauerhaft in der Datei.
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
        self.execute("INSERT OR REPLACE INTO inventory (InventarNr, Device, Type, Location) VALUES ('{}', '{}', '{}', '{}')".format(id, device, type, location))

    def device_delete(self, id):
        """Delete a device from the inventory table."""
        # Geloescht wird ueber die eindeutige ID, nicht ueber den Geraetenamen.
        self.execute("DELETE FROM inventory WHERE InventarNr = '{}'".format(id))

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
        self.cursor.execute("""SELECT id, device, type, location FROM inventory WHERE id || device || type || location LIKE '%{}%'""".format(query))
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows

    def types(self):
        """Run a SELECT query and return (column_names, rows)."""
        # Die Suche verbindet ID, Geraet, Typ und Ort zu einem Suchbereich.
        # Dadurch findet ein Begriff Treffer in jeder sichtbaren Spalte.
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("""SELECT Device, Key FROM devicetypes """)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows

    def get_next_highest_id(self, prefix="CMP"):       
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
