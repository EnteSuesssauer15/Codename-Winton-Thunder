# views/query.py
import flet as ft
import flet_datatable2 as fdt


def DeviceView(page: ft.Page, db_manager):
    # Diese Menge merkt sich die IDs der aktuell markierten Zeilen. IDs sind
    # stabiler als Gerätenamen, weil mehrere Geräte gleich heißen können.
    selected_titles = set()
    loading_ring = ft.ProgressRing(value=None, visible=False)


    # --- Building / Searching to create and display in the table ---
    def build_rows(search_query=None):
        # Ohne Suchbegriff werden alle Datensätze geladen. Mit Suchbegriff
        # delegieren wir die Filterung an die Datenbankschicht.
        if search_query:
            columns, records = db_manager.search_inventory(search_query)
        else:
            columns, records = db_manager.fetch_query(
                """SELECT inventory.InventarNr, inventory.Device, inventory.Type_Id,
                          inventory.Assignee_Id, employees.Name, employees.Surname
                   FROM inventory
                   JOIN employees ON employees.employeeId = inventory.Assignee_Id"""
            )

        def make_row(id, device, type, employee_id, employee_name, employee_surname):
            # Aus einem Datenbank-Datensatz wird eine sichtbare Tabellenzeile.
            def handle_select_change(e: ft.Event[fdt.DataRow2]):
                # Beim Anklicken einer Checkbox wird die ID in die Auswahl
                # aufgenommen oder wieder daraus entfernt.
                e.control.selected = not e.control.selected
                if e.control.selected:
                    selected_titles.add(id)
                else:
                    selected_titles.discard(id)
                e.control.update()

                delete_button.disabled = not bool(selected_titles)
                # Der Zustand des Löschbuttons hängt von der Auswahl ab.
                page.update()

            return fdt.DataRow2(
                on_select_change=handle_select_change,
                selected=id in selected_titles,
                cells=[
                    ft.DataCell(content=ft.Text(str(id))),
                    ft.DataCell(content=ft.Text(device)),
                    ft.DataCell(content=ft.Text(type)),
                    ft.DataCell(content=ft.Text(str(employee_id))),
                    ft.DataCell(content=ft.Text(employee_name)),
                    ft.DataCell(content=ft.Text(employee_surname)),
                ],
            )

        return [make_row(*record) for record in records]


    def run_query(e):
        # Die Suche wird durch Enter oder das Lupen-Icon gestartet.
        loading_ring.visible = True
        page.update()
        query = query_field.value
        try:
            table.rows = build_rows(query if query else None)
        except Exception as ex:
            # Bei einer ungültigen Abfrage bleibt die Tabelle leer, statt die
            # gesamte Benutzeroberfläche abstürzen zu lassen.
            table.rows = []
        table.update()
        loading_ring.visible = False
        page.update()
        
    def delete_selected():
        # Jede markierte ID wird einzeln aus der Datenbank gelöscht.
        if not selected_titles:
            return

        for id in list(selected_titles):
            db_manager.device_delete(id)
            selected_titles.discard(id)

        refresh_table()

    def refresh_table(e=None):
        # Diese Funktion wird auch von main.py aufgerufen, wenn die Tabellen-
        # Seite geöffnet wird oder ein neuer Datensatz gespeichert wurde.
        table.visible = True
        table.rows = build_rows()
        page.update()

    def handle_select_all(e):
        # Der Kopf der Tabelle kann alle vorhandenen IDs auf einmal auswählen
        # oder die Auswahl komplett leeren.
        _, records = db_manager.fetch_query("SELECT InventarNr FROM inventory")
        if e.data == "true":
            selected_titles.update(record[0] for record in records)
        else:
            selected_titles.clear()
        refresh_table()
    # --- Building / Searching to create and display in the table ---

    # Der Button ist anfangs deaktiviert, weil noch keine Zeile ausgewählt ist.
    delete_button = ft.Button(
        "delete selected",
        icon=ft.CupertinoIcons.TRASH,
        on_click=delete_selected,
        disabled=True,
    )

    table = fdt.DataTable2(
        visible=False,
        expand=True,
        show_checkbox_column=True,
        fixed_top_rows=1,
        empty=ft.Text("Inventory Empty"),
        columns=[
            fdt.DataColumn2(label=ft.Text("InventarNr"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Device"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Type"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("EmployeeId"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Employee Name"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Employee Surname"), size=fdt.DataColumnSize.L),
        ],
        rows=build_rows(),
        on_select_all=handle_select_all,
    )


    # --- Dialog zum Anlegen eines neuen Geräts ---

    device_field = ft.TextField(label="Device Name")

    # Definition der Dropdown Menüs, sodass diese nicht nur innerhalb der Funktion verfügbar sind
    select_type_drpdwn = ft.Dropdown(width=300, options=[], editable=True)
    select_employee_drpdwn = ft.Dropdown(width=300, options=[], editable=True)

    def refresh_dropdown_options():

        # 

        _, type_rows = db_manager.types()
        select_type_drpdwn.options = [
            ft.dropdown.Option(key=str(row[0]), text=str(row[0])) for row in type_rows
        ]

        _, employee_rows = db_manager.employees()
        select_employee_drpdwn.options = [
            ft.dropdown.Option(key=str(row[0]), text=str(row[0]) + " | " + str(row[1]) + " " + str(row[2])) for row in employee_rows
        ]

    def close_dialog(e):
        # Der Dialog wird geschlossen, ohne die Datenbank zu verändern.
        page.pop_dialog()
        page.update()

    def save_entry(e):
        # Werte lesen; Dropdowns liefern None, wenn nichts gewählt wurde.
        # "or ''" macht daraus einen leeren String, damit .strip() sicher funktioniert.
        device = (device_field.value or "").strip()
        device_type = (select_type_drpdwn.value or "").strip()
        employee = (select_employee_drpdwn.value or "").strip()

        # Alte Fehlermeldungen zurücksetzen
        device_field.error = None
        select_type_drpdwn.error_text = None
        select_employee_drpdwn.error_text = None

        # Validierung: alle Felder prüfen, damit mehrere Fehler gleichzeitig angezeigt werden
        has_error = False

        if not device:
            device_field.error = "Device is required"
            has_error = True

        if not device_type:
            select_type_drpdwn.error_text = "Type is required"
            has_error = True

        if not employee:
            select_employee_drpdwn.error_text = "Employee is required"
            has_error = True



        # Zuweisung des Kürzels aus den Typen für die InventarNr
        # Sodass dort CMPXXXXX steht statt ComputerXXXXX
        _, type_rows = db_manager.types()
        type_short = None

        for row in type_rows:
            type_id = str(row[0])
            short_code = str(row[1])

            if type_id == device_type:
                type_short = short_code
                break

        if type_short is None:
            select_type_drpdwn.error_text = "Select a valid type"
            has_error = True
            page.update()
            return

        if has_error:
            page.update()
            return

        device_id = type_short + str(db_manager.get_next_highest_id(type_short))

        db_manager.device_create(device_id, device, device_type, int(employee))

        page.pop_dialog()
        refresh_table()
        page.update()

    add_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Device"),
        content=ft.Column(
            [device_field, select_type_drpdwn, select_employee_drpdwn],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Save", on_click=save_entry),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_add_dialog(e):
        refresh_dropdown_options()
        
        # Vor jedem Öffnen werden die Felder zurückgesetzt, damit kein alter
        # Inhalt aus einem vorherigen Dialog stehen bleibt.
        page.show_dialog(add_dialog)

    add_device_btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        content=ft.Text("Add Device"),
        width=150,
        on_click=open_add_dialog,
    )

    # Der FAB (Floating Action Button) ist das Plus-Symbol zum Anlegen.

    # Das Suchfeld reagiert auf Enter; das Lupen-Icon ruft denselben Handler auf.
    query_field = ft.TextField(
        label="Enter InventoryNr, Device Name, Type, Employee Name, Employee Surname",
        on_submit=run_query,
        expand=True,
    )

    # Hier werden Suchfeld, Löschbutton und Tabelle zu einer gemeinsamen View
    # zusammengesetzt. `expand=True` lässt die Tabelle den Platz ausfüllen.
    container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    [
                        query_field,
                        ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_query),
                        add_device_btn,
                    ],
                    expand=True,
                ),
                ft.Row([
                    delete_button
                ]),
                ft.Container(content=table, expand=True),
            ],
            spacing=20,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )

    return container, refresh_table