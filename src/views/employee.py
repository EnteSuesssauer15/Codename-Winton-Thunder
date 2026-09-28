# views/query.py
import flet as ft
import flet_datatable2 as fdt


def EmployeeView(page: ft.Page, db_manager):
    selected_titles = set()

    # --- Baut die Tabelle aus den Datenbankdaten zusammen ---
    def build_rows(search_query=None):
        # Ohne Suchbegriff werden alle Datensätze geladen. Mit Suchbegriff
        # delegieren wir die Filterung an die Datenbankschicht.
        if search_query:
            columns, records = db_manager.search(search_query)
        else:
            columns, records = db_manager.fetch_query(
                "SELECT employeeId, Name, Surname, Department FROM employees"
            )

        def make_row(employeeId, Name, Surname, Department):
            # Aus einem Datenbank-Datensatz wird eine sichtbare Tabellenzeile.
            def handle_select_change(e: ft.Event[fdt.DataRow2]):
                # Beim Anklicken einer Checkbox wird die ID in die Auswahl
                # aufgenommen oder wieder daraus entfernt.
                e.control.selected = not e.control.selected
                if e.control.selected:
                    selected_titles.add(employeeId)
                else:
                    selected_titles.discard(employeeId)
                e.control.update()

                employee_delete_button.disabled = not bool(selected_titles)
                # Der Zustand des Löschbuttons hängt von der Auswahl ab.
                page.update()

            return fdt.DataRow2(
                on_select_change=handle_select_change,
                selected=employeeId in selected_titles,
                cells=[
                    ft.DataCell(content=ft.Text(str(employeeId))),
                    ft.DataCell(content=ft.Text(Name)),
                    ft.DataCell(content=ft.Text(Surname)),
                    ft.DataCell(content=ft.Text(Department)),
                ],
            )

        return [make_row(*record) for record in records]

    # Die Suche wird durch Enter oder das Lupen-Icon gestartet.
    def run_query(e):
        query = employee_search_bar.value
        # Bei einer ungültigen Abfrage bleibt die Tabelle leer, statt die
        # gesamte Benutzeroberfläche abstürzen zu lassen.
        try:
            table.rows = build_rows(query if query else None)
        except Exception as ex:
            table.rows = []
        table.update()
        
    def delete_selected():
        # Jede markierte ID wird einzeln aus der Datenbank gelöscht.
        if not selected_titles:
            return

        for id in list(selected_titles):
            db_manager.employee_delete(id)
            selected_titles.discard(id)
            print(selected_titles)
            print(id)

        refresh_employees()

    def refresh_employees(e=None):
        # Diese Funktion wird auch von main.py aufgerufen, wenn die Tabellen-
        # Seite geöffnet wird oder ein neuer Datensatz gespeichert wurde.
        table.visible = True
        table.rows = build_rows()
        page.update()

    def handle_select_all(e):
        # Der Kopf der Tabelle kann alle vorhandenen IDs auf einmal auswählen
        # oder die Auswahl komplett leeren.
        _, records = db_manager.fetch_query("SELECT InventarNr, Device, Type, Location FROM inventory")
        if e.data == "true":
            selected_titles.update(id for id, _, _, _ in records)
        else:
            selected_titles.clear()
        refresh_employees()
    # --- Building / Searching to create and display in the table ---

    # Der Button ist anfangs deaktiviert, weil noch keine Zeile ausgewählt ist.
    employee_delete_button = ft.Button(
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
        empty=ft.Text("No Employees"),
        columns=[
            fdt.DataColumn2(label=ft.Text("EmployeeId"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Name"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Surname"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Department"), size=fdt.DataColumnSize.L),
        ],
        rows=build_rows(),
        on_select_all=handle_select_all,
    )


    # --- Dialog zum Anlegen eines neuen Geräts ---

    add_employee_dialog_name = ft.TextField(label="Name")
    add_employee_dialog_surname = ft.TextField(label="Surname")
    add_employee_dialog_department = ft.TextField(label="Department")

    def close_dialog(e):
        # Der Dialog wird geschlossen, ohne die Datenbank zu verändern.
        page.pop_dialog()
        page.update()

    def save_entry(e):
        # Werte aus den Eingabefeldern lesen und führende/trailing Leerzeichen
        # entfernen, bevor sie in der Datenbank gespeichert werden.
        name = (add_employee_dialog_name.value or "").strip()
        surname = (add_employee_dialog_surname.value or "").strip()
        department = (add_employee_dialog_department.value or "").strip()

        add_employee_dialog_name.error = None
        add_employee_dialog_surname.error = None
        add_employee_dialog_department.error = None

        has_error = False

        if not name:
            # `error_text` zeigt die Fehlermeldung direkt unter dem Feld an.
            add_employee_dialog_name.error = "Name is required"
            has_error = True

        if not surname:
            add_employee_dialog_surname.error = "Surname is required"
            has_error = True

        if not department:
            add_employee_dialog_department.error = "Department is required"
            has_error = True
            
        if has_error:
            page.update()
            return

        # Erst wenn alle drei Werte vorhanden sind, wird der Datensatz angelegt.
        db_manager.employee_create(name, surname, department)

        page.pop_dialog()
        refresh_employees()
        page.update()

    add_employee_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Employee"),
        content=ft.Column(
            [add_employee_dialog_name, add_employee_dialog_surname, add_employee_dialog_department],
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
        
        # Vor jedem Öffnen werden die Felder zurückgesetzt, damit kein alter
        # Inhalt aus einem vorherigen Dialog stehen bleibt.
        add_employee_dialog_name.value = ""
        add_employee_dialog_surname.value = ""
        add_employee_dialog_department.value = ""

        # Aufrufen des menüs
        page.show_dialog(add_employee_dialog)


    # Der Knopf, welcher das Menü zur Mitarbeitererstellung öffnet
    add_employee_btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        content=ft.Text("Add Employee"),
        width=150,
        on_click=open_add_dialog,
    )

    # Das Suchfeld reagiert auf Enter; das Lupen-Icon ruft denselben Handler auf.
    employee_search_bar = ft.TextField(
        label="Enter Employee Name, Surname or Department",
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
                        employee_search_bar,
                        ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_query),
                        add_employee_btn,
                    ],
                    expand=True,
                ),
                ft.Row([
                    employee_delete_button
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

    return container, refresh_employees