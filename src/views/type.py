# views/query.py
import flet as ft
import flet_datatable2 as fdt


def TypeView(page: ft.Page, db_manager):
    selected_titles = set()

    # --- Baut die Tabelle aus den Datenbankdaten zusammen ---
    def build_rows(search_query=None):
        # Ohne Suchbegriff werden alle Datensätze geladen. Mit Suchbegriff
        # delegieren wir die Filterung an die Datenbankschicht.
        if search_query:
            columns, records = db_manager.search(search_query)
        else:
            columns, records = db_manager.fetch_query(
                "SELECT TypeId, Short FROM devicetypes"
            )

        def make_row(id, name):
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

                type_delete_button.disabled = not bool(selected_titles)
                # Der Zustand des Löschbuttons hängt von der Auswahl ab.
                page.update()

            return fdt.DataRow2(
                on_select_change=handle_select_change,
                selected=id in selected_titles,
                cells=[
                    ft.DataCell(content=ft.Text(id)),
                    ft.DataCell(content=ft.Text(name)),
                ],
            )

        return [make_row(*record) for record in records]

    # Die Suche wird durch Enter oder das Lupen-Icon gestartet.
    def run_query(e):
        query = type_search_bar.value
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
            db_manager.type_delete(id)
            selected_titles.discard(id)

        refresh_types()

    def refresh_types(e=None):
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
        refresh_types()
    # --- Building / Searching to create and display in the table ---

    # Der Button ist anfangs deaktiviert, weil noch keine Zeile ausgewählt ist.
    type_delete_button = ft.Button(
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
        empty=ft.Text("No Types"),
        columns=[
            fdt.DataColumn2(label=ft.Text("Devicetype"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Short"), size=fdt.DataColumnSize.L),
        ],
        rows=build_rows(),
        on_select_all=handle_select_all,
    )


    # --- Dialog zum Anlegen eines neuen Geraets ---

    add_type_dialog_devicetype = ft.TextField(label="Device Type")
    add_type_dialog_short = ft.TextField(label="Short", tooltip="Shorts will be visible at the beginning of every InventoryNr")

    def close_dialog(e):
        # Der Dialog wird geschlossen, ohne die Datenbank zu veraendern.
        page.pop_dialog()
        page.update()

    def save_entry(e):
        # Werte lesen; Dropdowns liefern None, wenn nichts gewählt wurde.
        # "or ''" macht daraus einen leeren String, damit .strip() sicher funktioniert.
        type = (add_type_dialog_devicetype.value or "").strip()
        short = (add_type_dialog_short.value or "").strip()

        # Alte Fehlermeldungen zuruecksetzen
        add_type_dialog_devicetype.error = None
        add_type_dialog_short.error = None

        # Validierung: alle Felder pruefen, damit mehrere Fehler gleichzeitig angezeigt werden
        has_error = False

        if not type:
            add_type_dialog_devicetype.error = "Type is required"
            has_error = True

        if not short:
            add_type_dialog_short.error = "Short is required"
            has_error = True

        if has_error:
            page.update()
            return

        # Erst wenn alle drei Werte vorhanden sind, wird der Datensatz angelegt.
        db_manager.type_create(type, short)

        page.pop_dialog()
        refresh_types()
        page.update()

    add_type_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New type"),
        content=ft.Column(
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

    def open_add_dialog(e):
        
        # Vor jedem Öffnen werden die Felder zurückgesetzt, damit kein alter
        # Inhalt aus einem vorherigen Dialog stehen bleibt.
        add_type_dialog_devicetype.value = ""
        add_type_dialog_short.value = ""

        # Aufrufen des menüs
        page.show_dialog(add_type_dialog)


    # Der Knopf, welcher das Menü zur Mitarbeitererstellung öffnet
    add_type_btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        content=ft.Text("Add type"),
        width=150,
        on_click=open_add_dialog,
    )

    # Das Suchfeld reagiert auf Enter; das Lupen-Icon ruft denselben Handler auf.
    type_search_bar = ft.TextField(
        label="Enter Type or Short",
        on_submit=run_query,
        expand=True,
    )

    # Hier werden Suchfeld, Loeschbutton und Tabelle zu einer gemeinsamen View
    # zusammengesetzt. `expand=True` laesst die Tabelle den Platz ausfuellen.
    container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    [
                        type_search_bar,
                        ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_query),
                        add_type_btn,
                    ],
                    expand=True,
                ),
                ft.Row([
                    type_delete_button
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

    return container, refresh_types