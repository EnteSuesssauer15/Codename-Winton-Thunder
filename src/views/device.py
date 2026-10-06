# device.py
# Seite "Devices": zeigt alle Geräte in einer Tabelle an. Hier kann man
# Geräte suchen, neue Geräte anlegen und markierte Geräte löschen.
#
# type.py und employee.py sind nach demselben Muster aufgebaut. Wer diese Datei
# verstanden hat, findet sich dort schnell zurecht.
import flet as ft
import flet_datatable2 as fdt


# Erstellt die komplette Geräte-Seite.
# Rückgabe: (Container mit der Seite, Funktion zum Neuladen der Tabelle)
# Beides wird in main.py verwendet.
#
# Hinweis: Alle Funktionen in dieser Funktion sind "innere Funktionen". Sie
# können auf Variablen wie `table` oder `selected_titles` zugreifen, auch wenn
# diese erst weiter unten definiert werden, weil sie erst später (z. B. bei
# einem Klick) aufgerufen werden.
def DeviceView(page: ft.Page, db_manager):
    # Diese Menge (set) merkt sich die IDs der aktuell markierten Zeilen.
    # IDs sind besser geeignet als Gerätenamen, weil mehrere Geräte gleich
    # heißen können. Ein set enthält jeden Wert höchstens einmal.
    selected_titles = set()

    # Erstellt die Tabellenzeilen aus den Datenbankeinträgen.
    # Rückgabe: Liste von Tabellenzeilen (DataRow2), eine pro Gerät.
    def build_rows(search_query=None):
        # Ohne Suchbegriff werden alle Datensätze geladen. Mit Suchbegriff
        # übernimmt die Datenbankklasse das Filtern.
        if search_query:
            # Die Suchfunktion liefert zwei Werte zurück, die direkt in
            # `columns` (Spaltennamen) und `records` (Zeilen) gespeichert werden.
            columns, records = db_manager.search_inventory(search_query)
        else:
            # Kein Suchbegriff: Es werden alle Geräte geladen.
            # Über JOIN kommen Name und Nachname des zugewiesenen Mitarbeiters dazu.
            columns, records = db_manager.fetch_query("""SELECT inventory.InventarNr, inventory.Device, inventory.Type_Id, inventory.Assignee_Id, employees.Name, employees.Surname FROM inventory
                   JOIN employees ON employees.employeeId = inventory.Assignee_Id""")

        # Erstellt aus einem Datensatz eine sichtbare Tabellenzeile.
        # Wird hier nur definiert und erst am Ende von `build_rows` für jeden
        # Datensatz aufgerufen.
        def make_row(id, device, type, employee_id, employee_name, employee_surname):
            # Wird aufgerufen, wenn die Checkbox dieser Zeile angeklickt wird.
            def handle_select_change(e: ft.Event[fdt.DataRow2]):
                # Beim Anklicken einer Checkbox wird die ID in die Auswahl
                # aufgenommen oder wieder daraus entfernt.
                e.control.selected = not e.control.selected
                if e.control.selected:
                    selected_titles.add(id)
                else:
                    selected_titles.discard(id)
                e.control.update()

                # Der Löschbutton ist nur aktiv, wenn mindestens eine Zeile markiert ist.
                device_delete_button.disabled = not bool(selected_titles)

                page.update()

            # Hier wird die Tabellenzeile erstellt.
            # Jeder Wert braucht seine eigene DataCell, damit er in einer eigenen
            # Spalte steht. Die Anzahl der Zellen muss genau der Anzahl der
            # Spalten in `table` entsprechen, sonst gibt es einen Fehler.
            # Jeder Aufruf von make_row erstellt genau eine Zeile der Tabelle.
            return fdt.DataRow2(
                on_select_change=handle_select_change,
                # Zeile bleibt markiert, wenn ihre ID schon ausgewählt war.
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

        # Ruft make_row für jeden Datensatz auf. Das `*` entpackt das Tupel, sodass
        # jede Spalte als eigener Parameter übergeben wird.
        # Beispiel: make_row(*("CMP00001", "Laptop", ...)) entspricht make_row("CMP00001", "Laptop", ...)
        return [make_row(*record) for record in records]


    # Wird beim Klick auf die Lupe oder beim Drücken von Enter im Suchfeld ausgeführt.
    def run_query(e):
        page.update()
        query = query_field.value
        try:
            # Ist das Suchfeld leer, wird None übergeben und alle Geräte werden geladen.
            table.rows = build_rows(query if query else None)
        except Exception as ex:
            # Bei einer ungültigen Abfrage bleibt die Tabelle leer, statt die
            # gesamte Benutzeroberfläche abstürzen zu lassen.
            table.rows = []
        table.update()
        page.update()

    # Anfang Löschfunktion (wiederholt sich in jeder Tabellen-View)

    # Wird beim Klick auf "delete selected" ausgeführt.
    def delete_selected():
        # Ist nichts markiert, gibt es nichts zu tun.
        if not selected_titles:
            return

        # Jede markierte ID wird einzeln aus der Datenbank gelöscht.
        # `list(...)` erstellt eine Kopie, weil man ein set nicht verändern darf,
        # während man darüber läuft.
        for id in list(selected_titles):
            db_manager.device_delete(id)
            selected_titles.discard(id)

        refresh_table()

    # Liest alle Geräte neu aus der Datenbank und baut die Tabelle neu zusammen.
    # `e=None` erlaubt den Aufruf sowohl als Event-Handler als auch direkt.
    def refresh_table(e=None):
        table.visible = True
        table.rows = build_rows()
        page.update()

    # Wird ausgeführt, wenn die Checkbox im Tabellenkopf angeklickt wird.
    def handle_select_all(e):
        # Über den Tabellenkopf können alle vorhandenen IDs auf einmal ausgewählt
        # oder die Auswahl komplett geleert werden.
        _, records = db_manager.fetch_query("SELECT InventarNr FROM inventory")
        # `e.data` ist True, wenn der Haken gesetzt wurde.
        if e.data == True:
            selected_titles.update(record[0] for record in records)
            device_delete_button.disabled = False
        else:
            selected_titles.clear()
            device_delete_button.disabled = True
        refresh_table()

    # Ende Löschfunktion

    # Button zum Löschen der markierten Geräte. Ist zu Beginn deaktiviert,
    # weil noch nichts markiert ist.
    device_delete_button = ft.Button(
        "delete selected",
        icon=ft.CupertinoIcons.TRASH,
        on_click=delete_selected,
        disabled=True,
    )

    # Definition des Tabellenobjekts
    table = fdt.DataTable2(
        # Unsichtbar, bis die Seite zum ersten Mal geöffnet wird (siehe refresh_table).
        visible=False,
        expand=True,
        # Zeigt vor jeder Zeile eine Checkbox zum Markieren an.
        show_checkbox_column=True,
        # Die Kopfzeile bleibt beim Scrollen oben stehen.
        fixed_top_rows=1,
        # Text, der angezeigt wird, wenn die Tabelle keine Zeilen hat.
        empty=ft.Text("Inventory Empty"),
        columns=[
            # Hier kann der angezeigte Name der jeweiligen Spalte verändert werden.
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


    # Dialog zum Anlegen eines neuen Geräts

    # Eingabefeld für den Gerätenamen
    device_field = ft.TextField(label="Device Name")

    # Die Dropdown-Menüs werden hier außerhalb der Funktionen definiert, damit
    # mehrere Funktionen (Befüllen, Speichern, Zurücksetzen) darauf zugreifen können.
    # `editable=True` erlaubt, im Dropdown zu tippen, um die Liste zu filtern.
    select_type_drpdwn = ft.Dropdown(width=300, options=[], label="Type", editable=True)
    select_employee_drpdwn = ft.Dropdown(width=300, options=[], label="Employee", editable=True)

    def refresh_dropdown_options():

        # Holt die neuesten Daten aus der Datenbank und schreibt diese in die
        # beiden Dropdown-Menüs. Wird bei jedem Öffnen des Pop-ups ausgeführt,
        # damit neu angelegte Typen oder Mitarbeiter direkt auswählbar sind.

        # Typen: `key` ist der Wert, der intern gespeichert wird,
        # `text` ist das, was der Benutzer sieht.
        _, type_rows = db_manager.types()
        select_type_drpdwn.options = [
            ft.dropdown.Option(key=str(row[0]), text=str(row[0])) for row in type_rows
        ]

        # Mitarbeiter: intern wird die ID gespeichert, angezeigt wird
        # z. B. "3 | Max Mustermann".
        _, employee_rows = db_manager.employees()
        select_employee_drpdwn.options = [
            ft.dropdown.Option(key=str(row[0]), text=str(row[0]) + " | " + str(row[1]) + " " + str(row[2])) for row in employee_rows
        ]

    # Schließt das Pop-up-Fenster beim Klick auf "Cancel".
    def close_dialog(e):
        page.pop_dialog()
        page.update()

    # Speichert den neuen Eintrag beim Klick auf "Save".
    def save_entry(e):
        # Werte lesen. Felder liefern None, wenn nichts eingegeben bzw. gewählt wurde.
        # "or ''" macht daraus einen leeren String, damit .strip() sicher funktioniert.
        # .strip() entfernt Leerzeichen am Anfang und Ende.
        device = (device_field.value or "").strip()
        device_type = (select_type_drpdwn.value or "").strip()
        employee = (select_employee_drpdwn.value or "").strip()

        # Alte Fehlermeldungen zurücksetzen
        device_field.error = None
        select_type_drpdwn.error_text = None
        select_employee_drpdwn.error_text = None

        # Validierung: Alle Felder werden geprüft, damit keines leer bleibt.
        # `has_error` merkt sich, ob mindestens ein Fehler gefunden wurde. So
        # werden alle Fehler gleichzeitig angezeigt und nicht nur der erste.
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



        # Sucht das Kürzel des gewählten Typs heraus, damit die Inventarnummer
        # die Form "CMPxxxxx" bekommt.
        _, type_rows = db_manager.types()
        type_short = None

        for row in type_rows:
            type_id = str(row[0])
            short_code = str(row[1])

            if type_id == device_type:
                type_short = short_code
                # `break` beendet die Schleife, sobald der Typ gefunden wurde.
                break
        # Prüft, ob der eingegebene Typ auch existiert. Das ist nötig, weil man
        # im Dropdown auch freien Text eingeben kann.
        if type_short is None:
            select_type_drpdwn.error_text = "Select a valid type"
            has_error = True
            page.update()
            return

        # Gab es einen Fehler, werden die Fehlermeldungen angezeigt und es wird
        # nicht gespeichert.
        if has_error:
            page.update()
            return

        # Holt die nächsthöhere Nummer für dieses Kürzel aus der Datenbank und
        # setzt das Kürzel davor, z. B. "CMP" + "00043" = "CMP00043".
        device_id = type_short + str(db_manager.get_next_highest_id(type_short))

        # Speichert das Gerät, indem ein neuer Datenbankeintrag aus den
        # angegebenen Daten geschrieben wird.
        db_manager.device_create(device_id, device, device_type, int(employee))

        # Pop-up schließen und Tabelle neu laden, damit das neue Gerät sichtbar wird.
        page.pop_dialog()
        refresh_table()
        page.update()

    # Das Pop-up-Fenster zum Anlegen eines Geräts.
    # `modal=True` bedeutet: Man kann nicht daneben klicken, um es zu schließen.
    add_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Device"),
        content=ft.Column(
            # Diese Eingabefelder werden untereinander im Pop-up angezeigt.
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

    # Öffnet das Pop-up zum Anlegen eines Geräts.
    def open_add_dialog(e):
        refresh_dropdown_options()

        # Vor jedem Öffnen werden die Felder zurückgesetzt, damit kein alter
        # Inhalt aus einem vorherigen Dialog stehen bleibt.
        device_field.value = ""
        select_type_drpdwn.value = ""
        select_employee_drpdwn.value = ""

        page.show_dialog(add_dialog)

    # Der Button zum Hinzufügen von Geräten
    add_device_btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        content=ft.Text("Add Device"),
        width=150,
        on_click=open_add_dialog,
    )

    # Das Suchfeld. `on_submit` wird beim Drücken von Enter ausgelöst.
    query_field = ft.TextField(
        label="Enter InventoryNr, Device Name, Type, Employee Name, Employee Surname",
        on_submit=run_query,
        expand=True,
    )

    # Hier werden Suchfeld, Buttons und Tabelle zu einer gemeinsamen View
    # zusammengesetzt. `expand=True` lässt die Tabelle den freien Platz ausfüllen.
    container = ft.Container(
        content=ft.Column(
            controls=[
                # Obere Zeile: Suchfeld, Lupen-Button und "Add Device"-Button
                ft.Row(
                    [
                        query_field, ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_query), add_device_btn,
                    ],
                    expand=True,
                ),
                # Zweite Zeile: Löschbutton
                ft.Row([
                    device_delete_button
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

    return container, refresh_table
