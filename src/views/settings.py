# settings.py
# Einstellungsseite. Hier kann man alle Daten als JSON-Datei sichern (Backup)
# und aus einer solchen Datei wiederherstellen (Restore). Außerdem wird der
# Pfad zur Datenbankdatei angezeigt.
#
# Diese Datei wurde hauptsächlich von KI generiert.
import json
from pathlib import Path

import flet as ft
import scripts.database as db

# Eigenes DatabaseManager-Objekt für diese Seite. Es nutzt den Standardpfad
# "database.db", also dieselbe Datei wie main.py, aber eine eigene Verbindung.
db_manager = db.DatabaseManager()


# Schreibt alle Daten aus der Datenbank in eine JSON-Datei.
# Ein Backup hat diese Form:
# {
#   "inventory": [{"InventarNr": ..., "Device": ..., "Type_Id": ..., "Assignee_Id": ...}, ...],
#   "types":     [{"TypeId": ..., "Short": ...}, ...],
#   "employees": [{"employeeId": ..., "Name": ..., "Surname": ..., "Department": ...}, ...]
# }
def make_backup(file_path):
    # Liest alle Geräte und schreibt sie als Dictionary in die Liste `inventory`.
    # Ein Dictionary speichert Werte unter einem Namen (Schlüssel), z. B. device["Device"].
    columns, rows = db_manager.fetch_query(
        "SELECT InventarNr, Device, Type_Id, Assignee_Id FROM inventory"
    )
    inventory = []
    for row in rows:
        device = {
            "InventarNr": row[0],
            "Device": row[1],
            "Type_Id": row[2],
            "Assignee_Id": row[3],
        }
        inventory.append(device)

    # Liest alle Typen und schreibt sie in die Liste `types`.
    columns, rows = db_manager.types()
    types = []
    for row in rows:
        device_type = {
            "TypeId": row[0],
            "Short": row[1],
        }
        types.append(device_type)

    # Liest alle Mitarbeiter und schreibt sie in die Liste `employees`.
    columns, rows = db_manager.fetch_query(
        "SELECT employeeId, Name, Surname, Department FROM employees"
    )
    employees = []
    for row in rows:
        employee = {
            "employeeId": row[0],
            "Name": row[1],
            "Surname": row[2],
            "Department": row[3],
        }
        employees.append(employee)

    # Ein gemeinsames Dictionary, das alle Daten enthält.
    data = {
        "inventory": inventory,
        "types": types,
        "employees": employees,
    }
    # Speichert die JSON-Datei. `indent=2` sorgt für eine gut lesbare Einrückung,
    # `ensure_ascii=False` behält Umlaute wie "ä" bei, statt sie zu kodieren.
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

# Prüft, ob jeder Eintrag einer Liste alle benötigten Felder enthält.
# Fehlt ein Feld, wird ein Fehler (ValueError) ausgelöst und die Prüfung bricht ab.
def check_backup_file(entries, needed_fields):
    for entry in entries:
        for field in needed_fields:
            if field not in entry:
                raise ValueError("Missing '" + field + "' in: " + str(entry))


# Prüft eine eingelesene Backup-Datei, bevor sie importiert wird.
# Ist etwas nicht in Ordnung, wird ein ValueError ausgelöst.
def check_backup(data):
    # Prüft, ob alle drei Bereiche (Tabellen) in der JSON-Datei existieren.
    for part in ["types", "employees", "inventory"]:
        if part not in data:
            raise ValueError("Backup file has no '" + part + "' part")

    # Prüft für jeden Bereich, ob alle Einträge die benötigten Felder besitzen.
    check_backup_file(data["types"], ["TypeId", "Short"])
    check_backup_file(data["employees"], ["employeeId", "Name", "Surname", "Department"])
    check_backup_file(data["inventory"], ["InventarNr", "Device", "Type_Id", "Assignee_Id"])

    # Sammelt alle Typnamen aus dem Backup in der Liste `known_types`.
    known_types = []
    for device_type in data["types"]:
        known_types.append(device_type["TypeId"])

    # Sammelt alle Mitarbeiter-IDs aus dem Backup in der Liste `known_employees`.
    # Die IDs werden mit str() in Text umgewandelt, damit der Vergleich unten
    # auch funktioniert, wenn eine ID mal als Zahl und mal als Text gespeichert ist.
    known_employees = []
    for employee in data["employees"]:
        known_employees.append(str(employee["employeeId"]))

    # Prüft für jedes Gerät, ob sein Typ und sein Mitarbeiter im Backup
    # vorhanden sind. Sonst würde das Gerät auf etwas verweisen, das es nicht gibt.
    for device in data["inventory"]:
        if device["Type_Id"] not in known_types:
            raise ValueError("Unknown type in: " + str(device))
        if str(device["Assignee_Id"]) not in known_employees:
            raise ValueError("Unknown employee in: " + str(device))


def delete_all_data():
    # Löscht alle Einträge in der Datenbank, bevor das Backup geladen wird.
    # Die Reihenfolge ist wichtig: Zuerst die Geräte, weil sie auf Mitarbeiter
    # und Typen verweisen. Erst danach lassen sich Mitarbeiter und Typen löschen.
    columns, rows = db_manager.fetch_query("SELECT InventarNr FROM inventory")
    for row in rows:
        db_manager.device_delete(row[0])

    columns, rows = db_manager.employees()
    for row in rows:
        db_manager.employee_delete(row[0])

    columns, rows = db_manager.types()
    for row in rows:
        db_manager.type_delete(row[0])


def insert_all_data(data):
    # Importiert die Typen. Sie kommen zuerst, weil Geräte auf sie verweisen.
    for device_type in data["types"]:
        db_manager.type_create(device_type["TypeId"], device_type["Short"])

    # Importiert die Mitarbeiter.
    # Die Datenbank vergibt neue IDs (AUTOINCREMENT), die von den IDs im Backup
    # abweichen können. Deshalb wird in `new_employee_ids` gespeichert, welche
    # alte ID zu welcher neuen ID gehört, z. B. {"1": 5, "2": 6}.
    new_employee_ids = {}
    for employee in data["employees"]:
        db_manager.employee_create(
            employee["Name"], employee["Surname"], employee["Department"]
        )
        # Die höchste ID ist die des gerade angelegten Mitarbeiters.
        columns, rows = db_manager.fetch_query("SELECT MAX(employeeId) FROM employees")
        new_id = rows[0][0]

        old_id = str(employee["employeeId"])
        new_employee_ids[old_id] = new_id

    # Importiert die Geräte. Dabei wird die alte Mitarbeiter-ID über
    # `new_employee_ids` durch die neue ID ersetzt.
    for device in data["inventory"]:
        old_id = str(device["Assignee_Id"])
        new_id = new_employee_ids[old_id]
        db_manager.device_create(
            device["InventarNr"], device["Device"], device["Type_Id"], new_id
        )

# Fasst die drei Schritte des Imports zusammen: prüfen, alles löschen, neu einfügen.
def restore_all(data):
    check_backup(data)
    delete_all_data()
    insert_all_data(data)


# Erstellt die Einstellungsseite und gibt sie als Container zurück.
def SettingsView():
    # Wird beim Klick auf "Backup and export all data" ausgeführt.
    # `async` ist nötig, weil auf das Dateiauswahlfenster mit `await` gewartet wird.
    async def handle_backup(e):
        # Das Fenster (page) wird über das Event geholt, weil SettingsView
        # keinen `page`-Parameter bekommt.
        page = e.page
        # Öffnet ein Fenster, in dem man auswählt, wo die Datei gespeichert werden soll.
        save_path = await ft.FilePicker().save_file(
            dialog_title="Save backup file",
            file_name="backup.json",
            allowed_extensions=["json"],
        )

        # Kein Pfad bedeutet: Das Fenster wurde ohne Auswahl geschlossen.
        if not save_path:
            return

        # Hängt die Endung ".json" an, falls der Benutzer sie weggelassen hat.
        if not save_path.lower().endswith(".json"):
            save_path = save_path + ".json"

        # Backup erstellen und das Ergebnis unten im Fenster (SnackBar) anzeigen.
        try:
            make_backup(save_path)
            page.show_dialog(ft.SnackBar(ft.Text("Backup completed successfully.")))
        except Exception as error:
            page.show_dialog(ft.SnackBar(ft.Text("Backup failed." + str(error))))

    # Wird beim Klick auf "Import and restore all data" ausgeführt.
    async def handle_restore(e):
        page = e.page

        # Öffnet ein Fenster zur Auswahl der Backup-Datei.
        files = await ft.FilePicker().pick_files(
            dialog_title="Select backup file",
            allow_multiple=False,
            allowed_extensions=["json"],
        )

        # Auch hier gilt: Wurde nichts ausgewählt, wird abgebrochen.
        if not files:
            return

        # Liest die Backup-Datei ein und prüft sie. Ist die Datei fehlerhaft,
        # wird eine Meldung angezeigt und abgebrochen, bevor etwas gelöscht wird.
        try:
            with open(files[0].path, "r", encoding="utf-8") as file:
                data = json.load(file)
            check_backup(data)
        except Exception as error:
            page.show_dialog(ft.SnackBar(ft.Text("Could not read backup." + str(error))))
            return

        # Klick auf "Cancel": Sicherheitsabfrage schließen, nichts passiert.
        def cancel(event):
            page.pop_dialog()

        # Klick auf "Restore": Sicherheitsabfrage schließen und Backup einspielen.
        def confirm(event):
            page.pop_dialog()
            try:
                restore_all(data)
                page.show_dialog(ft.SnackBar(ft.Text("Restore completed successfully.")))
            except Exception as error:
                page.show_dialog(ft.SnackBar(ft.Text("Restore failed. " + str(error))))

        # Zeigt eine Sicherheitsabfrage an, die darauf hinweist, dass alle
        # aktuellen Daten durch das Backup ersetzt werden.
        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Restore backup?"),
                content=ft.Text(
                    "This replaces ALL current types, employees and devices "
                    "with the backup."
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel),
                    ft.TextButton("Restore", on_click=confirm),
                ],
            )
        )

    # Platzhalter für den Button "Save Settings". Gibt bisher nur eine Meldung
    # in der Konsole aus und speichert noch nichts.
    def handle_save_settings(e):
        print("Settings saved successfully.")

    # Aufbau der Einstellungsseite: oben Backup & Restore, darunter die Einstellungen.
    return ft.Container(
        content=ft.Column([
            ft.Text("Backup & Restore", size=28, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.FloatingActionButton(
                    width=350,
                    content=ft.Text("Backup and export all data"),
                    on_click=handle_backup,
                ),
                ft.FloatingActionButton(
                    width=350,
                    content=ft.Text("Import and restore all data"),
                    on_click=handle_restore,
                ),
            ]),
            ft.Divider(),
            ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
            # Zeigt den vollständigen Pfad zur Datenbankdatei an.
            # `resolve()` macht aus dem relativen Pfad einen absoluten Pfad.
            # `selectable=True` erlaubt, den Pfad zu markieren und zu kopieren.
            ft.Container(
                content=ft.Row(tight=True, controls=[
                    ft.Text("Database Path:"),
                    ft.Text(str(Path(db_manager.db_name).resolve()), selectable=True),
                ]),
                bgcolor=ft.Colors.BLUE_GREY_900,
                border=ft.Border.all(1, ft.Colors.BLUE_ACCENT),
                border_radius=6,
                padding=10,
            ),
            ft.Button("Save Settings", on_click=handle_save_settings),
        ]),
        padding=20,
        expand=True,
    )
