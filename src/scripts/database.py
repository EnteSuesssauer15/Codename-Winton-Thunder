# database.py
# Enthält die Klasse DatabaseManager. Sie bündelt alle Zugriffe auf die
# SQLite-Datenbank, damit die Views (Seiten) kein SQL selbst schreiben müssen,
# sondern nur Methoden wie `device_create()` oder `employees()` aufrufen.
#
# Die Datenbank besteht aus vier Tabellen:
# - employees:   Mitarbeiter (ID, Name, Nachname, Abteilung)
# - devicetypes: Gerätetypen (Typname und Kürzel, z. B. "Computer" / "CMP")
# - inventory:   Geräte (Inventarnummer, Name, Typ, zugewiesener Mitarbeiter)
# - settings:    Einstellungen als Paare aus Option und Wert
#
# Hinweis: Werte werden nie direkt in den SQL-Text geschrieben (z. B. mit
# `.format()`), sondern über Platzhalter (`?`) übergeben. SQLite setzt die Werte
# dann selbst sicher ein. So funktionieren auch Werte mit Hochkomma wie "O'Brien",
# und niemand kann über ein Eingabefeld eigene SQL-Befehle einschleusen
# (SQL-Injection).
import os
import pysqlite3 as sql3


class DatabaseManager:
    # Wird beim Erstellen eines DatabaseManager-Objekts aufgerufen.
    # Die Verbindung zur Datenbank wird hier noch nicht geöffnet, sondern erst
    # beim ersten Zugriff (siehe z. B. `execute()`).
    def __init__(self, db_name="database.db"):

        # Pfad zur Datenbankdatei
        self.db_name = db_name
        # Die geöffnete Verbindung zur Datenbank (None = noch nicht verbunden)
        self.connection = None
        # Der Cursor führt SQL-Befehle aus und liefert die Ergebnisse
        self.cursor = None

    def exists(self):
        # Prüft, ob die Datenbankdatei (standardmäßig "database.db") vorhanden ist.
        # Gibt True oder False zurück.
        return os.path.exists(self.db_name)

    # Schließt die Verbindung zur Datenbank, wenn sie geöffnet ist.
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    # Erzeugt die Datenbankdatei und legt alle Tabellen an.
    # Wird nur aufgerufen, wenn die Datei noch nicht existiert.
    def initialize_database(self):
        try:
            if not self.exists():
                # `connect` legt die Datei automatisch an, wenn sie fehlt.
                connection = sql3.connect(self.db_name)
                cursor = connection.cursor()
                print("Database created and Successfully Connected to SQLite")

                # Tabelle für Mitarbeiter. AUTOINCREMENT vergibt die ID
                # automatisch fortlaufend (1, 2, 3, ...).
                cursor.execute("""CREATE TABLE IF NOT EXISTS employees (
                    employeeId INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TXT NOT NULL,
                    Surname TXT NOT NULL,
                    Department TXT NOT NULL
                );""")
                # `commit()` speichert die Änderung dauerhaft in der Datei.
                connection.commit()

                # Tabelle für Gerätetypen. Der Typname ist gleichzeitig die ID.
                # Das Kürzel (Short) wird später vor die Inventarnummer gesetzt.
                cursor.execute("""CREATE TABLE IF NOT EXISTS devicetypes (
                    TypeId TXT PRIMARY KEY,
                    Short TXT NOT NULL
                );""")
                connection.commit()

                # Drei Standardtypen, damit man direkt Geräte anlegen kann.
                cursor.execute("""INSERT INTO devicetypes (TypeId, Short) VALUES 
                    ('Monitor', 'MON'),
                    ('Computer', 'CMP'),
                    ('Peripherie', 'PER');""")
                connection.commit()

                # Tabelle für Geräte. Die beiden FOREIGN KEYs sorgen dafür, dass
                # jedes Gerät auf einen existierenden Typ und Mitarbeiter verweist.
                cursor.execute("""CREATE TABLE IF NOT EXISTS inventory (
                    InventarNr TEXT PRIMARY KEY,
                    Device TEXT NOT NULL,
                    Type_Id TEXT NOT NULL,
                    Assignee_Id INTEGER NOT NULL,
                    FOREIGN KEY (Type_Id) REFERENCES devicetypes(TypeId),
                    FOREIGN KEY (Assignee_Id) REFERENCES employees(employeeId)
                );""")
                connection.commit()

                # Tabelle für Einstellungen als einfache Schlüssel-Wert-Paare.
                cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                    option TEXT PRIMARY KEY,
                    value TEXT
                );""")
                connection.commit()
                print("Database initialized")
        except Exception as e:
            print("Couldnt create Database:\n\n")
            print(e)


    # Führt einen beliebigen SQL-Befehl aus, ohne ein Ergebnis zurückzugeben.
    # Geeignet für INSERT, UPDATE, DELETE oder PRAGMA.
    # command = SQL-Text, darin steht für jeden Wert ein `?` als Platzhalter
    # params  = Tupel mit den Werten für die Platzhalter, in derselben Reihenfolge.
    #           Ohne Platzhalter kann `params` weggelassen werden,
    #           z. B. execute("PRAGMA foreign_keys = ON;").
    def execute(self, command, params=()):
        # Falls noch keine Verbindung besteht, wird sie jetzt geöffnet.
        # Dieses Muster wiederholt sich in mehreren Methoden dieser Klasse.
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute(command, params)
        self.connection.commit()


    # Speichert eine Einstellung (z. B. setting="theme", value="dark").
    def settings_set(self, setting, value):
        # INSERT OR REPLACE legt eine Option an oder ersetzt ihren alten Wert.
        # Die beiden `?` werden der Reihe nach mit `setting` und `value` gefüllt.
        self.execute("INSERT OR REPLACE INTO settings (option, value) VALUES (?, ?)", (setting, value))


    # Liest den gespeicherten Wert einer Einstellung aus.
    def settings_get(self, setting):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        # SELECT liest genau den Wert der angeforderten Option.
        # Auch bei nur einem Wert muss ein Tupel übergeben werden. Das Komma in
        # `(setting,)` ist wichtig, ohne es wäre es kein Tupel.
        self.cursor.execute("SELECT value FROM settings WHERE option = ?", (setting,))
        # `fetchone()` liefert die erste gefundene Zeile als Tupel, z. B. ("dark",),
        # oder None, wenn nichts gefunden wurde.
        result = self.cursor.fetchone()
        # Gibt es keinen Eintrag, liefert die Funktion `None` zurück.
        return result[0] if result else None


    # Legt ein neues Gerät an.
    # id       = Inventarnummer, z. B. "CMP00001"
    # device   = Gerätename
    # type     = Typname aus der Tabelle devicetypes, z. B. "Computer"
    # location = ID des Mitarbeiters, dem das Gerät zugewiesen wird
    def device_create(self, id, device, type, location):
        self.execute("INSERT INTO inventory (InventarNr, Device, Type_Id, Assignee_Id) VALUES (?, ?, ?, ?)", (id, device, type, location))

    # Löscht ein Gerät anhand seiner Inventarnummer.
    def device_delete(self, id):
        self.execute("DELETE FROM inventory WHERE InventarNr = ?", (id,))

    # Legt einen neuen Mitarbeiter an. Die ID wird von der Datenbank
    # automatisch vergeben (AUTOINCREMENT) und muss nicht übergeben werden.
    def employee_create(self, Name, Surname, Department):
        self.execute("INSERT INTO employees (Name, Surname, Department) VALUES (?, ?, ?)", (Name, Surname, Department))

    # Löscht einen Mitarbeiter anhand seiner ID.
    def employee_delete(self, id):
        # Ist dem Mitarbeiter noch ein Gerät zugewiesen, verhindert die
        # Fremdschlüssel-Prüfung das Löschen und es entsteht ein Fehler.
        # Dieser Fehler wird nicht weitergeworfen, sondern zurückgegeben, damit
        # die View eine Meldung anzeigen kann. Ohne Fehler wird None zurückgegeben.
        try:
            self.execute("DELETE FROM employees WHERE EmployeeId = ?", (id,))
        except Exception as e:
            return e

    # Liest alle Mitarbeiter (ID, Name, Nachname) aus.
    # Rückgabe: (Liste der Spaltennamen, Liste aller Zeilen)
    def employees(self):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("""SELECT employeeId, Name, Surname FROM employees """)
        # `cursor.description` enthält Infos zu jeder Spalte des Ergebnisses.
        # Das erste Element (desc[0]) ist jeweils der Spaltenname.
        column_names = [desc[0] for desc in self.cursor.description]
        # `fetchall()` liefert alle Ergebniszeilen als Liste von Tupeln.
        rows = self.cursor.fetchall()
        return column_names, rows

    # Legt einen neuen Gerätetyp an, z. B. Type="Drucker", Short="DRU".
    def type_create(self, Type, Short):
        self.execute("INSERT INTO devicetypes (TypeId, Short) VALUES (?, ?)", (Type, Short))

    # Löscht einen Gerätetyp anhand seiner ID (des Typnamens).
    def type_delete(self, id):
        # Wird der Typ noch von einem Gerät verwendet, entsteht ein Fehler.
        # Wie bei `employee_delete()` wird der Fehler zurückgegeben statt geworfen.
        try:
            self.execute("DELETE FROM devicetypes WHERE TypeId = ?", (id,))
        except Exception as e:
            return e


    # Liest alle Gerätetypen (Typname und Kürzel) aus.
    # Rückgabe: (Liste der Spaltennamen, Liste aller Zeilen)
    def types(self):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        self.cursor.execute("""SELECT * FROM devicetypes """)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows

    # Führt eine beliebige SELECT-Abfrage aus und gibt sowohl die Spaltennamen
    # als auch alle gefundenen Zeilen zurück.
    def fetch_query(self, query):
        # `check_same_thread=False` erlaubt, die Verbindung auch aus anderen
        # Threads zu nutzen. Flet führt Event-Handler teilweise in eigenen Threads aus.
        if not self.connection:
            self.connection = sql3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.connection.cursor()
        self.cursor.execute(query)
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return column_names, rows


    # Die folgenden drei Suchfunktionen wurden mit Unterstützung von KI erstellt.
    # Sie funktionieren alle nach demselben Prinzip:
    # - Die Reihenfolge der Suchbegriffe spielt keine Rolle.
    # - Groß- und Kleinschreibung wird ignoriert.
    # - Leerzeichen werden ignoriert.
    # - Eine Zeile wird nur angezeigt, wenn ALLE Suchbegriffe darin vorkommen.
    # Beispiel: "max cmp" findet das Gerät "CMP00001", das "Max Mustermann" zugewiesen ist.

    # Durchsucht die Geräte. Gesucht werden kann nach Inventarnummer, Gerätename,
    # Typ, Mitarbeiter-ID sowie Vor- und Nachname des Mitarbeiters.
    def search_inventory(self, query):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()

        # Teilt die Eingabe an Leerzeichen auf und legt alle Suchbegriffe in einer
        # Liste ab, in Kleinbuchstaben und ohne Leerzeichen.
        # `casefold()` ist eine gründlichere Variante von `lower()`.
        search_terms = ["".join(term.casefold().split()) for term in query.split()]

        # Liest die gesamte inventory-Tabelle aus. Über JOIN werden zu jedem Gerät
        # Name und Nachname des zugewiesenen Mitarbeiters aus `employees` ergänzt.
        self.cursor.execute("""SELECT inventory.InventarNr, inventory.Device, inventory.Type_Id, inventory.Assignee_Id, employees.Name, employees.Surname FROM inventory
               JOIN employees ON employees.employeeId = inventory.Assignee_Id""")
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        matching_rows = []

        for row in rows:
            # Fügt alle Spaltenwerte der Zeile zu einem einzigen Text zusammen,
            # in Kleinbuchstaben und ohne Leerzeichen.
            # Beispiel: ("CMP00001", "Laptop", ...) wird zu "cmp00001laptop..."
            row_text = "".join("".join(str(value).casefold().split()) for value in row)

            # Wenn alle Suchbegriffe in diesem Text vorkommen, wird die Zeile
            # zu den Treffern hinzugefügt.
            if all(term in row_text for term in search_terms):
                matching_rows.append(row)

        # Gibt die Spaltennamen und nur die passenden Gerätezeilen zurück.
        return column_names, matching_rows

    # Durchsucht die Gerätetypen. Gesucht werden kann nach Typname oder Kürzel.
    def search_type(self, query):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()

        # Teilt die Eingabe an Leerzeichen auf und legt alle Suchbegriffe in einer
        # Liste ab, in Kleinbuchstaben und ohne Leerzeichen.
        search_terms = ["".join(term.casefold().split()) for term in query.split()]

        # Liest die gesamte devicetypes-Tabelle aus.
        self.cursor.execute("""SELECT TypeId, Short FROM devicetypes""")
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        matching_rows = []

        for row in rows:
            # Fügt alle Spaltenwerte der Zeile zu einem einzigen Text zusammen,
            # in Kleinbuchstaben und ohne Leerzeichen.
            row_text = "".join("".join(str(value).casefold().split()) for value in row)

            # Wenn alle Suchbegriffe in diesem Text vorkommen, wird die Zeile
            # zu den Treffern hinzugefügt.
            if all(term in row_text for term in search_terms):
                matching_rows.append(row)

        # Gibt die Spaltennamen und nur die passenden Typzeilen zurück.
        return column_names, matching_rows

    # Durchsucht die Mitarbeiter. Gesucht werden kann nach ID, Name, Nachname
    # oder Abteilung.
    def search_employee(self, query):
        if not self.connection:
            self.connection = sql3.connect(self.db_name)
            self.cursor = self.connection.cursor()

        # Teilt die Eingabe an Leerzeichen auf und legt alle Suchbegriffe in einer
        # Liste ab, in Kleinbuchstaben und ohne Leerzeichen.
        search_terms = ["".join(term.casefold().split()) for term in query.split()]

        # Liest die gesamte employees-Tabelle aus.
        self.cursor.execute("""SELECT employeeId, Name, Surname, Department FROM employees""")
        column_names = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        matching_rows = []

        for row in rows:
            # Fügt alle Spaltenwerte der Zeile zu einem einzigen Text zusammen,
            # in Kleinbuchstaben und ohne Leerzeichen.
            row_text = "".join("".join(str(value).casefold().split()) for value in row)

            # Wenn alle Suchbegriffe in diesem Text vorkommen, wird die Zeile
            # zu den Treffern hinzugefügt.
            if all(term in row_text for term in search_terms):
                matching_rows.append(row)

        # Gibt die Spaltennamen und nur die passenden Mitarbeiterzeilen zurück.
        return column_names, matching_rows

    # Mit Unterstützung von KI erstellt.
    # Ermittelt die nächste freie Nummer für eine Inventarnummer mit dem
    # angegebenen Kürzel (prefix). Gibt die Nummer als fünfstelligen Text zurück.
    # Beispiel: Gibt es schon "CMP00041" und "CMP00042", liefert
    # get_next_highest_id("CMP") den Text "00043".
    def get_next_highest_id(self, prefix):
        # Sucht die höchste Inventarnummer, die mit dem Kürzel beginnt.
        # `LIKE 'CMP%'` bedeutet: beginnt mit "CMP", danach beliebige Zeichen.
        # Das `?` ist ein Platzhalter, den SQLite sicher mit dem Wert aus dem
        # Tupel dahinter füllt.
        self.cursor.execute(
            "SELECT MAX(InventarNr) FROM inventory WHERE InventarNr LIKE ?",
            (f"{prefix}%",)
        )
        result = self.cursor.fetchone()

        # Existiert noch kein Eintrag mit diesem Kürzel, wird mit 1 begonnen.
        if result is None or result[0] is None:
            next_number = 1
        else:
            # result[0] ist beispielsweise "CMP00042".
            highest_string = result[0]

            # Schneidet die letzten 5 Zeichen aus, sodass nur noch "00042" übrig bleibt.
            numeric_part = highest_string[-5:]

            # Wandelt den Text in eine Ganzzahl (int) um und addiert 1.
            next_number = int(numeric_part) + 1

        # Gibt die nächste Nummer zurück. `:05d` füllt links mit Nullen auf
        # fünf Stellen auf, z. B. 43 wird zu "00043".
        return f"{next_number:05d}"
