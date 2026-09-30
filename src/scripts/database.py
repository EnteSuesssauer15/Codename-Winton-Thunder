import os
import pysqlite3 as sql3


class DatabaseManager:
    def __init__(self, db_name="database.db"):

        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.execute("PRAGMA foreign_keys = ON;")

    def exists(self):
        #? Prüfen ob eine "database.db" Datei vorhanden ist
        return os.path.exists(self.db_name)


    #? Funktion um die Datenbank zu generieren und einzurichten
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

                cursor.execute("""INSERT INTO devicetypes (TypeId, Short) VALUES 
                    ('Monitor', 'MON'),
                    ('Computer', 'CMP'),
                    ('Peripherie', 'PER');""")
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


    #? Für komplette Datenbank kontrolle ohne Rückgabewert
    def execute(self, command):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute(command)
        self.connection.commit()
        print("Command executed successfully.")


    #? Um Einstellungen zu speichern
    def settings_set(self, setting, value):
        #? INSERT OR REPLACE legt eine Option an oder ersetzt ihren alten Wert.
        self.execute("INSERT OR REPLACE INTO settings (option, value) VALUES ('{}', '{}')".format(setting, value))


    #? Um Einstellungswerte zu erhalten
    def settings_get(self, setting):
        #? SELECT liest genau den Wert der angeforderten Option.
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT value FROM settings WHERE option = '{}'".format(setting))
        result = self.cursor.fetchone()
        #? Gibt es keinen Eintrag, liefert die Funktion `None`` zurück.
        return result[0] if result else None


    #? Erstellt neue Geräte anhand der 4 mitgegebenen Werte
    def device_create(self, id, device, type, location):
        #? Schaltet die Prüfung für Fremdschlüssel ein
        self.execute("INSERT INTO inventory (InventarNr, Device, Type_Id, Assignee_Id) VALUES ('{}', '{}', '{}', '{}')".format(id, device, type, location))

    #? Löscht geräte anhand ihrer InventarNr
    def device_delete(self, id):
        self.execute("DELETE FROM inventory WHERE InventarNr = '{}'".format(id))

    #? Erstellt neue Mitarbeiter anhand der 3 mitgegebenen Werte
    def employee_create(self, Name, Surname, Department):
        #? Schaltet die Prüfung für Fremdschlüssel ein
        self.execute("INSERT INTO employees (Name, Surname, Department) VALUES ('{}', '{}', '{}')".format(Name, Surname, Department))

    #? Löscht Mitarbeiter anhand ihrer ID
    def employee_delete(self, id):
        #? erzeugt einen fehler und gibt den zurück wenn der wert noch zugewiesen ist
        try:
            self.execute("DELETE FROM employees WHERE EmployeeId = '{}'".format(id,))
        except Exception as e:
            return e
        
    #? Listet alle Mitarbeiter auf
    def employees(self):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("""SELECT employeeId, Name, Surname FROM employees """)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows

    #? Erstellt neue Typen anhand der 2 mitgegebenen Werte
    def type_create(self, Type, Short):
        #? Schaltet die Prüfung für Fremdschlüssel ein 
        self.execute("INSERT INTO devicetypes (TypeId, Short) VALUES ('{}', '{}')".format(Type, Short))

    #? Löscht Typen anhand der ID
    def type_delete(self, id):
        #? erzeugt einen fehler und gibt den zurück wenn der wert noch zugewiesen ist
        try:
            self.execute("DELETE FROM devicetypes WHERE TypeId = '{}'".format(id,))
        except Exception as e:
            return e
            

    #? Listet alle Typen
    def types(self):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("""SELECT * FROM devicetypes """)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows
    
    #? Diese Methode führt eine SELECT-Abfrage aus und gibt sowohl die Spaltennamen als auch alle gefundenen Zeilen zurück.
    def fetch_query(self, query):
        
        if not self.connection:
            self.connection = sql3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.connection.cursor()
        self.cursor.execute(query)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows
    
    #? Durchsucht die Inventar Tabelle in der entweder InventarNr, Gerät, Typ, MitarbeiterID, Name oder Nachname Gesucht wird
    #? Der suchbegriff wird durch den Parameter query mitgegeben und als "search_pattern" gespeichert
    def search_inventory(self, query):

        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        #? Fügt % an anfang und ende, sodass es als wildcard verwendet wird
        search_pattern = f"%{query}%"
        self.cursor.execute("""SELECT inventory.InventarNr, inventory.Device, inventory.Type_Id, inventory.Assignee_Id, employees.Name, employees.Surname FROM inventory
               JOIN employees ON employees.employeeId = inventory.Assignee_Id WHERE inventory.InventarNr || inventory.Device || inventory.Type_Id || inventory.Assignee_Id || employees.Name || employees.Surname LIKE ?""",(search_pattern,),)
        #? Für jede Spalte die gelistet wird gibts einen array eintrag
        column_names = [desc[0] for desc in self.cursor.description]
        #? "rows" steht hier für jede Reihe die gelistet wird
        rows = self.cursor.fetchall()
        #? beide Werte werden zurückgegeben als wert für denjenigen der sie Funktion aufgerufen hat.
        return column_names, rows
    
    #? Durchsucht die Type Tabelle in der entweder Typen oder Kürzel gesucht werden können
    def search_type(self, query):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        #? Fügt % an anfang und ende, sodass es als wildcard verwendet wird
        search_pattern = f"%{query}%"
        self.cursor.execute("""SELECT TypeId, Short FROM devicetypes WHERE TypeId || Short LIKE ?""",(search_pattern,),)
        #? Für jede Spalte die gelistet wird gibts einen array eintrag
        column_names = [desc[0] for desc in self.cursor.description]
        #? "rows" steht hier für jede Reihe die gelistet wird
        rows = self.cursor.fetchall()
        #? beide Werte werden zurückgegeben als wert für denjenigen der sie Funktion aufgerufen hat.
        return column_names, rows

    #? Durchsucht die Type Tabelle in der entweder ID, Name, Nachname oder Abteilung gesucht werden können
    def search_employee(self, query):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        #? Fügt % an anfang und ende, sodass es als wildcard verwendet wird
        search_pattern = f"%{query}%"
        self.cursor.execute("""SELECT employeeId, Name, Surname, Department FROM employees WHERE employeeId || Name || Surname || Department LIKE ?""",(search_pattern,),)
        #? Für jede Spalte die gelistet wird gibts einen array eintrag
        column_names = [desc[0] for desc in self.cursor.description]
        #? "rows" steht hier für jede Reihe die gelistet wird
        rows = self.cursor.fetchall()
        #? beide Werte werden zurückgegeben als wert für denjenigen der sie Funktion aufgerufen hat.
        return column_names, rows

    #! Unterstützt durch KI
    #? Nächste nummer für die InventarNr  
    def get_next_highest_id(self, prefix):       
        self.cursor.execute(
            "SELECT MAX(InventarNr) FROM inventory WHERE InventarNr LIKE ?", 
            (f"{prefix}%",)
        )
        result = self.cursor.fetchone()
        
        #? Wenn kein Eintrag existiert mit dem Prefix, starte mit 1
        if result is None or result[0] is None:
            next_number = 1
        else:
            #? result[0] ist beispielsweise "CMP00042"
            highest_string = result[0]
            
            #? Schneite die Letzten 5 Ziffern aus, sodass man nur noch "00042" hat
            numeric_part = highest_string[-5:]
            
            #? wandelt das in eine integer um und addiert diese um 1
            next_number = int(numeric_part) + 1
            
        #? Gibt die nächste Nummer zurück
        return f"{next_number:05d}"
