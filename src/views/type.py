# type.py
# Seite "Types": zeigt alle Gerätetypen in einer Tabelle an. Hier kann man
# Typen suchen, neue Typen anlegen und markierte Typen löschen.
# Jeder Typ hat ein Kürzel (Short), das vor jede Inventarnummer gesetzt wird,
# z. B. "CMP" für Computer -> "CMP00001".
#
# Der Aufbau entspricht device.py. Die dortigen Kommentare erklären einige
# Stellen noch etwas ausführlicher.
import flet as ft
import flet_datatable2 as fdt


# Erstellt die komplette Typen-Seite.
# Rückgabe: (Container mit der Seite, Funktion zum Neuladen der Tabelle)
def TypeView(page: ft.Page, db_manager):
    # Diese Menge (set) merkt sich die IDs der aktuell markierten Zeilen.
    # Bei Typen ist die ID der Typname, z. B. "Computer".
    selected_titles = set()

    # Erstellt die Tabellenzeilen aus den Datenbankeinträgen.
    def build_rows(search_query=None):
        # Ohne Suchbegriff werden alle Datensätze geladen. Mit Suchbegriff
        # übernimmt die Datenbankklasse das Filtern.
        if search_query:
            # Die Suchfunktion liefert zwei Werte zurück, die direkt in
            # `columns` (Spaltennamen) und `records` (Zeilen) gespeichert werden.
            columns, records = db_manager.search_type(search_query)
        else:
            # Kein Suchbegriff: Es werden alle Typen geladen.
            columns, records = db_manager.fetch_query(
                "SELECT TypeId, Short FROM devicetypes"
            )
        # Erstellt aus einem Datensatz eine sichtbare Tabellenzeile.
        # Wird hier nur definiert und erst am Ende von `build_rows` aufgerufen.
        # `id` ist der Typname, `name` das Kürzel.
        def make_row(id, name):
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
                type_delete_button.disabled = not bool(selected_titles)
                page.update()

            # Hier wird die Tabellenzeile erstellt.
            # Jeder Wert braucht seine eigene DataCell, damit er in einer eigenen
            # Spalte steht. Die Anzahl der Zellen muss genau der Anzahl der
            # Spalten in `table` entsprechen.
            # Jeder Aufruf von make_row erstellt genau eine Zeile der Tabelle.
            return fdt.DataRow2(
                on_select_change=handle_select_change,
                selected=id in selected_titles,
                cells=[
                    ft.DataCell(content=ft.Text(id)),
                    ft.DataCell(content=ft.Text(name)),
                ],
            )
        # Ruft make_row für jeden Datensatz auf. Das `*` entpackt das Tupel, sodass
        # jede Spalte als eigener Parameter übergeben wird.
        return [make_row(*record) for record in records]

    # Wird beim Klick auf die Lupe oder beim Drücken von Enter im Suchfeld ausgeführt.
    def run_query(e):
        query = type_search_bar.value
        try:
            # Ist das Suchfeld leer, wird None übergeben und alle Typen werden geladen.
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
        # `type_delete` gibt einen Fehler zurück, wenn der Typ noch von Geräten
        # verwendet wird. Dann bleibt die Zeile markiert.
        for id in list(selected_titles):
            delete_error = db_manager.type_delete(id)
            if delete_error is not None:
                error = delete_error
            else:
                selected_titles.discard(id)
                type_delete_button.disabled = True

        refresh_types()

        # Konnte mindestens ein Typ nicht gelöscht werden, wird ein
        # Hinweisfenster mit der Fehlermeldung angezeigt.
        if error is not None:
            page.show_dialog(
                ft.AlertDialog(
                    title=ft.Text("Cannot delete Type"),
                    content=ft.Column([
                        ft.Text(size=16, value="This type is still assigned to one or more devices"),
                        ft.Text(size=10, value=str(error)),
                        ],
                        tight=True,),
                    # `lambda e: ...` ist eine kurze, namenlose Funktion, die beim
                    # Klick auf "OK" das Hinweisfenster schließt.
                    actions=[ft.TextButton("OK", on_click=lambda e: page.pop_dialog())]
                )
            )

    # Liest alle Typen neu aus der Datenbank und baut die Tabelle neu zusammen.
    def refresh_types(e=None):
        table.visible = True
        table.rows = build_rows()
        page.update()

    # Wird ausgeführt, wenn die Checkbox im Tabellenkopf angeklickt wird.
    def handle_select_all(e):
        # Über den Tabellenkopf können alle vorhandenen IDs auf einmal ausgewählt
        # oder die Auswahl komplett geleert werden.
        _, records = db_manager.fetch_query("SELECT TypeId, Short FROM devicetypes")
        # `e.data` ist True, wenn der Haken gesetzt wurde.
        if e.data == True:
            # Aus jeder Zeile wird nur die ID (erste Spalte) übernommen.
            # `_` steht für Werte, die nicht gebraucht werden.
            selected_titles.update(id for id, _, in records)
            type_delete_button.disabled = False
        else:
            selected_titles.clear()
            type_delete_button.disabled = True
        refresh_types()

    # Ende Löschfunktion

    # Button zum Löschen der markierten Typen. Ist zu Beginn deaktiviert.
    type_delete_button = ft.Button(
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
        empty=ft.Text("No Types"),
        columns=[
            # Hier kann der angezeigte Name der jeweiligen Spalte verändert werden.
            fdt.DataColumn2(label=ft.Text("Devicetype"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Short"), size=fdt.DataColumnSize.L),
        ],
        rows=build_rows(),
        on_select_all=handle_select_all,
    )


    # Dialog zum Anlegen eines neuen Typs

    # Eingabefelder für Typname und Kürzel. Sie werden hier außerhalb der
    # Funktionen definiert, damit mehrere Funktionen darauf zugreifen können.
    # `tooltip` zeigt einen Hinweis an, wenn man mit der Maus darüberfährt.
    add_type_dialog_devicetype = ft.TextField(label="Device Type")
    add_type_dialog_short = ft.TextField(label="Short", tooltip="Shorts will be visible at the beginning of every InventoryNr")

    # Schließt das Pop-up-Fenster beim Klick auf "Cancel".
    def close_dialog(e):
        page.pop_dialog()
        page.update()

    # Speichert den neuen Eintrag beim Klick auf "Save".
    def save_entry(e):
        # Werte lesen. Ein Feld kann None liefern, wenn es noch nie befüllt wurde.
        # "or ''" macht daraus einen leeren String, damit .strip() sicher funktioniert.
        # .strip() entfernt Leerzeichen am Anfang und Ende.
        type = (add_type_dialog_devicetype.value or "").strip()
        short = (add_type_dialog_short.value or "").strip()

        # Alte Fehlermeldungen zurücksetzen
        add_type_dialog_devicetype.error = None
        add_type_dialog_short.error = None

        # Validierung: Alle Felder werden geprüft, damit keines leer bleibt.
        # `has_error` merkt sich, ob mindestens ein Fehler gefunden wurde.
        has_error = False

        if not type:
            add_type_dialog_devicetype.error = "Type is required"
            has_error = True

        if not short:
            add_type_dialog_short.error = "Short is required"
            has_error = True

        # Gab es einen Fehler, werden die Meldungen angezeigt und nichts gespeichert.
        if has_error:
            page.update()
            return

        # Erst wenn beide Werte vorhanden sind, wird der Datensatz angelegt.
        db_manager.type_create(type, short)

        # Pop-up schließen und Tabelle neu laden, damit der neue Typ sichtbar wird.
        page.pop_dialog()
        refresh_types()
        page.update()

    # Das Pop-up-Fenster zum Anlegen eines Typs.
    # `modal=True` bedeutet: Man kann nicht daneben klicken, um es zu schließen.
    add_type_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New type"),
        content=ft.Column(
            # Diese Eingabefelder werden untereinander im Pop-up angezeigt.
            [add_type_dialog_devicetype, add_type_dialog_short],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Save", on_click=save_entry),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Öffnet das Pop-up zum Anlegen eines Typs.
    def open_add_dialog(e):
        # Vor jedem Öffnen werden die Felder zurückgesetzt, damit kein alter
        # Inhalt aus einem vorherigen Dialog stehen bleibt.
        add_type_dialog_devicetype.value = ""
        add_type_dialog_short.value = ""

        page.show_dialog(add_type_dialog)


    # Der Button, der das Pop-up zur Typenerstellung öffnet
    add_type_btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        content=ft.Text("Add type"),
        width=150,
        on_click=open_add_dialog,
    )

    # Das Suchfeld. `on_submit` wird beim Drücken von Enter ausgelöst.
    type_search_bar = ft.TextField(
        label="Enter Type or Short",
        on_submit=run_query,
        expand=True,
    )

    # Hier werden Suchfeld, Buttons und Tabelle zu einer gemeinsamen View
    # zusammengesetzt. `expand=True` lässt die Tabelle den freien Platz ausfüllen.
    container = ft.Container(
        content=ft.Column(
            controls=[
                # Obere Zeile: Suchfeld, Lupen-Button und "Add type"-Button
                ft.Row(
                    [
                        type_search_bar, ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_query), add_type_btn,
                    ],
                    expand=True,
                ),
                # Zweite Zeile: Löschbutton
                ft.Row([
                    type_delete_button
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

    return container, refresh_types
