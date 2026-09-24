import json

import flet as ft
import scripts.database as db

db_manager = db.DatabaseManager()

# Hier gab es starke unterstützung von KI

def make_backup(file_path):
    # Liest Geräte und schreibt diese in die inventory array
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

    # Liest Typen und schreibt diese in die types array
    columns, rows = db_manager.types()
    types = []
    for row in rows:
        device_type = {
            "TypeId": row[0],
            "Short": row[1],
        }
        types.append(device_type)

    # Liest Mitarbeiter und schreibt diese in die employees array
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

    # Schreibt die 3 Arrays in die Json Datei
    data = {
        "inventory": inventory,
        "types": types,
        "employees": employees,
    }
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def check_backup_file(entries, needed_fields):
    # Prüft alle Einträge in der Json
    for entry in entries:
        for field in needed_fields:
            if field not in entry:
                raise ValueError("Missing '" + field + "' in: " + str(entry))


def check_backup(data):
    # Prüft nach den 3 "Kategorien" in der Json
    for part in ["types", "employees", "inventory"]:
        if part not in data:
            raise ValueError("Backup file has no '" + part + "' part")

    # Jeder der "Kategorien" muss jeden attribut enthalten der gefordert wird
    check_backup_file(data["types"], ["TypeId", "Short"])
    check_backup_file(data["employees"], ["employeeId", "Name", "Surname", "Department"])
    check_backup_file(data["inventory"], ["InventarNr", "Device", "Type_Id", "Assignee_Id"])

    # Liest und speichert sich die Typen aus dem backup
    known_types = []
    for device_type in data["types"]:
        known_types.append(device_type["TypeId"])

    # Liest und speichert sich die Mitarbeiter aus dem backup
    known_employees = []
    for employee in data["employees"]:
        known_employees.append(str(employee["employeeId"]))

    # Prüft ob jede abhängigkeit von allen Geräten vorhanden ist
    # Also ob jeder Typ oder jeder Mitarbeiter mit einem Gerät existiert
    for device in data["inventory"]:
        if device["Type_Id"] not in known_types:
            raise ValueError("Unknown type in: " + str(device))
        if str(device["Assignee_Id"]) not in known_employees:
            raise ValueError("Unknown employee in: " + str(device))


def delete_all_data():
    # Löscht alle einträge, bevor das Backup geladen wird
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
    # Typenimport
    for device_type in data["types"]:
        db_manager.type_create(device_type["TypeId"], device_type["Short"])

    # Mitarbeiterimport, passt automatisch die Geräte an die neue EmployeeID an die durch das AUTOINCREMENT entsteht
    new_employee_ids = {}
    for employee in data["employees"]:
        db_manager.employee_create(
            employee["Name"], employee["Surname"], employee["Department"]
        )
        columns, rows = db_manager.fetch_query("SELECT MAX(employeeId) FROM employees")
        new_id = rows[0][0]

        old_id = str(employee["employeeId"])
        new_employee_ids[old_id] = new_id

    # Geräteimport
    for device in data["inventory"]:
        old_id = str(device["Assignee_Id"])
        new_id = new_employee_ids[old_id]
        db_manager.device_create(
            device["InventarNr"], device["Device"], device["Type_Id"], new_id
        )

# Gebündelte Funktion zum vereinfachen des Imports
def restore_all(data):
    check_backup(data)
    delete_all_data()
    insert_all_data(data)

# Darstellung der Einstellungsseite
def SettingsView():
    async def handle_backup(e):
        # Öffnet die Abfrage, wo die Datei gespeichert werden soll
        save_path = await ft.FilePicker().save_file(
            dialog_title="Save backup file",
            file_name="backup.json",
            allowed_extensions=["json"],
        )

        # Kein Pfad = Fenster geschlossen
        if not save_path:
            return

        if not save_path.lower().endswith(".json"):
            save_path = save_path + ".json"

        try:
            make_backup(save_path)
            print("Backup saved to:", save_path)
        except Exception as error:
            print("Backup failed:", error)

    async def handle_restore(e):
        page = e.page

        # Dateiauswahlfenster
        files = await ft.FilePicker().pick_files(
            dialog_title="Select backup file",
            allow_multiple=False,
            allowed_extensions=["json"],
        )

        # Auch hier Fenster geschlossen
        if not files:
            return

        # Einlesen der Backupdatei
        try:
            with open(files[0].path, "r", encoding="utf-8") as file:
                data = json.load(file)
            check_backup(data)
        except Exception as error:
            print("Could not read backup:", error)
            return

        def cancel(event):
            page.pop_dialog()

        def confirm(event):
            page.pop_dialog()
            try:
                restore_all(data)
                print("Restore finished.")
            except Exception as error:
                print("Restore failed:", error)

        # Zeigt ein Popupfenster welches die änderungen bzw daten anzeigt die importiert werden
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

    def handle_save_settings(e):
        print("Settings saved successfully.")

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
            ft.Button("Save Settings", on_click=handle_save_settings),
        ]),
        padding=20,
        expand=True,
    )