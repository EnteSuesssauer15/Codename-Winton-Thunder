# employee.py
# Seite "Employees": zeigt alle Mitarbeiter in einer Tabelle an. Hier kann man
# Mitarbeiter suchen, neue Mitarbeiter anlegen und markierte Mitarbeiter löschen.
#
# Der Aufbau entspricht device.py. Die dortigen Kommentare erklären einige
# Stellen noch etwas ausführlicher.
import flet as ft
import flet_datatable2 as fdt


# Erstellt die komplette Mitarbeiter-Seite.
# Rückgabe: (Container mit der Seite, Funktion zum Neuladen der Tabelle)
def EmployeeView(page: ft.Page, db_manager):
    # Diese Menge (set) merkt sich die IDs der aktuell markierten Zeilen.
    # IDs sind besser geeignet als Namen, weil mehrere Mitarbeiter gleich
    # heißen können.
    selected_titles = set()

    # Erstellt die Tabellenzeilen aus den Datenbankeinträgen.
    def build_rows(search_query=None):
        # Ohne Suchbegriff werden alle Datensätze geladen. Mit Suchbegriff
        # übernimmt die Datenbankklasse das Filtern.
        if search_query:
            # Die Suchfunktion liefert zwei Werte zurück, die direkt in
            # `columns` (Spaltennamen) und `records` (Zeilen) gespeichert werden.
            columns, records = db_manager.search_employee(search_query)
        else:
            # Kein Suchbegriff: Es werden alle Mitarbeiter geladen.
            columns, records = db_manager.fetch_query(
                "SELECT employeeId, Name, Surname, Department FROM employees"
            )

        # Erstellt aus einem Datensatz eine sichtbare Tabellenzeile.
        # Wird hier nur definiert und erst am Ende von `build_rows` aufgerufen.
        def make_row(employeeId, Name, Surname, Department):
            # Wird aufgerufen, wenn die Checkbox dieser Zeile angeklickt wird.
            def handle_select_change(e: ft.Event[fdt.DataRow2]):
                # Beim Anklicken einer Checkbox wird die ID in die Auswahl
                # aufgenommen oder wieder daraus entfernt.
                e.control.selected = not e.control.selected
                if e.control.selected:
                    selected_titles.add(employeeId)
                else:
                    selected_titles.discard(employeeId)
                e.control.update()

                # Der Löschbutton ist nur aktiv, wenn mindestens eine Zeile markiert ist.
                employee_delete_button.disabled = not bool(selected_titles)

                page.update()

            # Hier wird die Tabellenzeile erstellt.
            # Jeder Wert braucht seine eigene DataCell, damit er in einer eigenen
            # Spalte steht. Die Anzahl der Zellen muss genau der Anzahl der
            # Spalten in `table` entsprechen.
            # Jeder Aufruf von make_row erstellt genau eine Zeile der Tabelle.
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

        # Ruft make_row für jeden Datensatz auf. Das `*` entpackt das Tupel, sodass
        # jede Spalte als eigener Parameter übergeben wird.
        return [make_row(*record) for record in records]

    # Wird beim Klick auf die Lupe oder beim Drücken von Enter im Suchfeld ausgeführt.
    def run_query(e):
        query = employee_search_bar.value
        try:
            # Ist das Suchfeld leer, wird None übergeben und alle Mitarbeiter werden geladen.
            table.rows = build_rows(query if query else None)
        except Exception as ex:
            # Bei einer ungültigen Abfrage bleibt die Tabelle leer, statt die
            # gesamte Benutzeroberfläche abstürzen zu lassen.
            table.rows = []
        table.update()

    # Anfang Löschfunktion (wiederholt sich in jeder Tabellen-View)

    # Wird beim Klick auf "delete selected" ausgeführt.
    def delete_selected():
        # Ist nichts markiert, gibt es nichts zu tun.
        if not selected_titles:
            return

        # Merkt sich einen eventuell aufgetretenen Fehler, um ihn danach anzuzeigen.
        error = None

        # Jede markierte ID wird einzeln aus der Datenbank gelöscht.
        # `employee_delete` gibt einen Fehler zurück, wenn dem Mitarbeiter noch
        # Geräte zugewiesen sind. Dann bleibt die Zeile markiert.
        for id in list(selected_titles):
            delete_error = db_manager.employee_delete(id)
            if delete_error is not None:
                error = delete_error
            else:
                selected_titles.discard(id)
                employee_delete_button.disabled = True

        refresh_employees()

        # Konnte mindestens ein Mitarbeiter nicht gelöscht werden, wird ein
        # Hinweisfenster mit der Fehlermeldung angezeigt.
        if error is not None:
            page.show_dialog(
                ft.AlertDialog(
                    title=ft.Text("Cannot delete Employee"),
                    content=ft.Column([
                        ft.Text(size=16, value="This Employee is still assigned to one or more devices"),
                        ft.Text(size=10, value=str(error)),
                        ],
                        tight=True,),
                    # `lambda e: ...` ist eine kurze, namenlose Funktion, die beim
                    # Klick auf "OK" das Hinweisfenster schließt.
                    actions=[ft.TextButton("OK", on_click=lambda e: page.pop_dialog())]
                )
            )

    # Liest alle Mitarbeiter neu aus der Datenbank und baut die Tabelle neu zusammen.
    def refresh_employees(e=None):
        table.visible = True
        table.rows = build_rows()
        page.update()

    # Wird ausgeführt, wenn die Checkbox im Tabellenkopf angeklickt wird.
    def handle_select_all(e):
        # Über den Tabellenkopf können alle vorhandenen IDs auf einmal ausgewählt
        # oder die Auswahl komplett geleert werden.
        _, records = db_manager.fetch_query("SELECT employeeId, Name, Surname, Department FROM employees")
        # `e.data` ist True, wenn der Haken gesetzt wurde.
        if e.data == True:
            # Aus jeder Zeile wird nur die ID (erste Spalte) übernommen.
            # `_` steht für Werte, die nicht gebraucht werden.
            selected_titles.update(id for id, _, _, _ in records)
            employee_delete_button.disabled = False
        else:
            selected_titles.clear()
            employee_delete_button.disabled = True
        refresh_employees()

    # Ende Löschfunktion

    # Button zum Löschen der markierten Mitarbeiter. Ist zu Beginn deaktiviert.
    employee_delete_button = ft.Button(
        "delete selected",
        icon=ft.CupertinoIcons.TRASH,
        on_click=delete_selected,
        disabled=True,
    )

    # Definition des Tabellenobjekts
    table = fdt.DataTable2(
        # Unsichtbar, bis die Seite zum ersten Mal geöffnet wird.
        visible=False,
        expand=True,
        show_checkbox_column=True,
        fixed_top_rows=1,
        empty=ft.Text("No Employees"),
        columns=[
            # Hier kann der angezeigte Name der jeweiligen Spalte verändert werden.
            fdt.DataColumn2(label=ft.Text("EmployeeId"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Name"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Surname"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Department"), size=fdt.DataColumnSize.L),
        ],
        rows=build_rows(),
        on_select_all=handle_select_all,
    )


    # Dialog zum Anlegen eines neuen Mitarbeiters

    # Eingabefelder für Name, Nachname und Abteilung
    add_employee_dialog_name = ft.TextField(label="Name")
    add_employee_dialog_surname = ft.TextField(label="Surname")
    add_employee_dialog_department = ft.TextField(label="Department")

    # Schließt das Pop-up-Fenster beim Klick auf "Cancel".
    def close_dialog(e):
        page.pop_dialog()
        page.update()

    # Speichert den neuen Eintrag beim Klick auf "Save".
    def save_entry(e):
        # Werte lesen. Ein Feld kann None liefern, wenn es noch nie befüllt wurde.
        # "or ''" macht daraus einen leeren String, damit .strip() sicher funktioniert.
        # .strip() entfernt Leerzeichen am Anfang und Ende.
        name = (add_employee_dialog_name.value or "").strip()
        surname = (add_employee_dialog_surname.value or "").strip()
        department = (add_employee_dialog_department.value or "").strip()

        # Alte Fehlermeldungen zurücksetzen
        add_employee_dialog_name.error = None
        add_employee_dialog_surname.error = None
        add_employee_dialog_department.error = None

        # Validierung: Alle Felder werden geprüft, damit keines leer bleibt.
        # `has_error` merkt sich, ob mindestens ein Fehler gefunden wurde.
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

        # Gab es einen Fehler, werden die Meldungen angezeigt und nichts gespeichert.
        if has_error:
            page.update()
            return

        # Erst wenn alle drei Werte vorhanden sind, wird der Datensatz angelegt.
        db_manager.employee_create(name, surname, department)

        # Pop-up schließen und Tabelle neu laden, damit der neue Mitarbeiter sichtbar wird.
        page.pop_dialog()
        refresh_employees()
        page.update()

    # Das Pop-up-Fenster zum Anlegen eines Mitarbeiters.
    # `modal=True` bedeutet: Man kann nicht daneben klicken, um es zu schließen.
    add_employee_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Employee"),
        content=ft.Column(
            # Diese Eingabefelder werden untereinander im Pop-up angezeigt.
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

    # Öffnet das Pop-up zum Anlegen eines Mitarbeiters.
    def open_add_dialog(e):
        # Vor jedem Öffnen werden die Felder zurückgesetzt, damit kein alter
        # Inhalt aus einem vorherigen Dialog stehen bleibt.
        add_employee_dialog_name.value = ""
        add_employee_dialog_surname.value = ""
        add_employee_dialog_department.value = ""

        page.show_dialog(add_employee_dialog)


    # Der Button zum Hinzufügen von Mitarbeitern
    add_employee_btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        content=ft.Text("Add Employee"),
        width=150,
        on_click=open_add_dialog,
    )

    # Das Suchfeld. `on_submit` wird beim Drücken von Enter ausgelöst.
    employee_search_bar = ft.TextField(
        label="Enter Employee Name, Surname or Department",
        on_submit=run_query,
        expand=True,
    )

    # Hier werden Suchfeld, Buttons und Tabelle zu einer gemeinsamen View
    # zusammengesetzt. `expand=True` lässt die Tabelle den freien Platz ausfüllen.
    container = ft.Container(
        content=ft.Column(
            controls=[
                # Obere Zeile: Suchfeld, Lupen-Button und "Add Employee"-Button
                ft.Row(
                    [
                        employee_search_bar, ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_query), add_employee_btn,
                    ],
                    expand=True,
                ),
                # Zweite Zeile: Löschbutton
                ft.Row([
                    employee_delete_button
                ]),
                # Darunter die Tabelle
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
