# views/query.py
import flet as ft
import flet_datatable2 as fdt


def EmployeeView(page: ft.Page, db_manager):
    #* Diese Menge merkt sich die IDs der aktuell markierten Zeilen. IDs sind
    #* stabiler als Gerätenamen, weil mehrere Geräte gleich heißen können.
    selected_titles = set()

    #? Anfang Erstellung der Tabelle aus den Datenbankeinträgen
    def build_rows(search_query=None):
        #? Ohne Suchbegriff werden alle Datensätze geladen. Mit Suchbegriff delegieren wir die Filterung an die Datenbankschicht.
        if search_query:
            #? Festlegung der lokalen Variablen die von der aufgerufenen Funktion befüllt werden
            columns, records = db_manager.search_employee(search_query)
        else:
            #? Hier werden alle Reihen ausgegeben, da nicht gesucht wird.
            #? Die Variablen müssen ebenfalls deklariert werden und werden ebenfalls befüllt von der Funktion
            columns, records = db_manager.fetch_query(
                "SELECT employeeId, Name, Surname, Department FROM employees"
            )

        #! Wird erst am ende der Funktion aufgerufen
        def make_row(employeeId, Name, Surname, Department):
            def handle_select_change(e: ft.Event[fdt.DataRow2]):
                #? Beim Anklicken einer Checkbox wird die ID in die Auswahl
                #? aufgenommen oder wieder daraus entfernt.
                e.control.selected = not e.control.selected
                if e.control.selected:
                    selected_titles.add(employeeId)
                else:
                    selected_titles.discard(employeeId)
                e.control.update()

                #? Der Zustand des Löschbuttons hängt von der Auswahl ab.
                employee_delete_button.disabled = not bool(selected_titles)

                page.update()

            #? Hier wird erst die Datenbank erstellt
            #* Jeder Parameter braucht seine eigene DataCell in der Tabelle von Flet um jeden Wert eingeben zu können, es darf nie eine Spalte leer bleiben
            #* Jeder durchlauf von dieser make_row Funktion erstellt hiermit eine einzige Reihe in der gesamten Tabelle
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

        #? Hier wird die Funktion make_row aufgerufen welche pro Spalte ihren eigenen Paremeter mitgegeben bekommt und pro Eintrag die Reihen erstellt
        return [make_row(*record) for record in records]

    def run_query(e):
        query = employee_search_bar.value
        try:
            table.rows = build_rows(query if query else None)
        except Exception as ex:
            #? Bei einer ungültigen Abfrage bleibt die Tabelle leer, statt die gesamte Benutzeroberfläche abstürzen zu lassen.
            table.rows = []
        table.update()

    # ? Anfang Löschfunktion (wiederholend pro Seite)
        
    def delete_selected():
        #? Jede markierte ID wird einzeln aus der Datenbank gelöscht.
        if not selected_titles:
            return

        error = None

        for id in list(selected_titles):
            delete_error = db_manager.employee_delete(id)
            if delete_error is not None:
                error = delete_error
            else:
                selected_titles.discard(id)
                employee_delete_button.disabled = True

        refresh_employees()

        if error is not None:
            page.show_dialog(
                ft.AlertDialog(
                    title=ft.Text("Cannot delete Employee"),
                    content=ft.Column([
                        ft.Text(size=16, value="This Employee is still assigned to one or more devices"),
                        ft.Text(size=10, value=str(error)),
                        ],
                        tight=True,),
                    actions=[ft.TextButton("OK", on_click=lambda e: page.pop_dialog())]
                )
            )

    #? Baut die Tabelle neu zusammen
    def refresh_employees(e=None):
        table.visible = True
        table.rows = build_rows()
        page.update()

    def handle_select_all(e):
        #? Der Kopf der Tabelle kann alle vorhandenen IDs auf einmal auswählen oder die Auswahl komplett leeren.
        _, records = db_manager.fetch_query("SELECT employeeId, Name, Surname, Department FROM employees")
        if e.data == True:
            selected_titles.update(id for id, _, _, _ in records)
            employee_delete_button.disabled = False
        else:
            selected_titles.clear()
            employee_delete_button.disabled = True
        refresh_employees()

    # ? Ende Löschfunktion (wiederholend pro Seite)

    employee_delete_button = ft.Button(
        "delete selected",
        icon=ft.CupertinoIcons.TRASH,
        on_click=delete_selected,
        disabled=True,
    )

    #? Definition des Tabellenobjekts
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


    #? Dialog zum Anlegen eines neuen Mitarbeiters

    add_employee_dialog_name = ft.TextField(label="Name")
    add_employee_dialog_surname = ft.TextField(label="Surname")
    add_employee_dialog_department = ft.TextField(label="Department")

    #? Schließt das Popup Fenster auf "Cancel"
    def close_dialog(e):
        page.pop_dialog()
        page.update()

    #? Speichert den neuen Eintrag auf "Save"
    def save_entry(e):
        #? Werte lesen; Dropdowns liefern None, wenn nichts gewählt wurde.
        #? "or ''" macht daraus einen leeren String, damit .strip() sicher funktioniert.
        name = (add_employee_dialog_name.value or "").strip()
        surname = (add_employee_dialog_surname.value or "").strip()
        department = (add_employee_dialog_department.value or "").strip()

        #? Alte Fehlermeldungen zurücksetzen
        add_employee_dialog_name.error = None
        add_employee_dialog_surname.error = None
        add_employee_dialog_department.error = None

        #? Validierung: alle Felder prüfen, sodass keines davon leer ist
        has_error = False

        if not name:
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

        #? Erst wenn alle drei Werte vorhanden sind, wird der Datensatz angelegt.
        db_manager.employee_create(name, surname, department)

        page.pop_dialog()
        refresh_employees()
        page.update()

    #? Popupobjekt welches hier definiert wird
    add_employee_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Employee"),
        content=ft.Column(
            #? welche Objekte von Flet in diesem Dialog sein sollen
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
        #? Vor jedem Öffnen werden die Felder zurückgesetzt, damit kein alter Inhalt aus einem vorherigen Dialog stehen bleibt.
        add_employee_dialog_name.value = ""
        add_employee_dialog_surname.value = ""
        add_employee_dialog_department.value = ""

        page.show_dialog(add_employee_dialog)


    #? Der Knopf zum hinzufügen von Geräten
    add_employee_btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        content=ft.Text("Add Employee"),
        width=150,
        on_click=open_add_dialog,
    )

    #? Das Suchfeld
    employee_search_bar = ft.TextField(
        label="Enter Employee Name, Surname or Department",
        on_submit=run_query,
        expand=True,
    )

    #? Hier werden Suchfeld, Löschbutton und Tabelle zu einer gemeinsamen View
    #? zusammengesetzt. `expand=True` lässt die Tabelle den Platz ausfüllen.
    container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    [
                        employee_search_bar, ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_query), add_employee_btn,
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