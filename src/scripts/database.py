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
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Device TEXT NOT NULL,
                Type TEXT NOT NULL,
                Location TEXT NOT NULL
            );""")
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
    def device_create(self, device, type, location):
        """Set a device in the inventory table."""
        # Die Werte kommen aus dem Formular in table.py und werden als neuer
        # Datensatz in `inventory` gespeichert.
        self.execute("INSERT OR REPLACE INTO inventory (device, type, location) VALUES ('{}', '{}', '{}')".format(device, type, location))

    def device_delete(self, id):
        """Delete a device from the inventory table."""
        # Geloescht wird ueber die eindeutige ID, nicht ueber den Geraetenamen.
        self.execute("DELETE FROM inventory WHERE ID = {}".format(id))

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


    # acts as check to prevent double entries when checking for updates
    def check(self, title):
        """Return True if an update with this title is already in the database."""
        # `check` beantwortet nur die Frage, ob ein Geraet bereits existiert.
        # Die Methode wird derzeit von keiner View verwendet.
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