# views/query.py
import flet as ft
import flet_datatable2 as fdt


def TableView(page: ft.Page, db_manager):
    # Diese Menge merkt sich die IDs der aktuell markierten Zeilen. IDs sind
    # stabiler als Geraetenamen, weil mehrere Geraete gleich heissen koennen.
    selected_titles = set()
    loading_ring = ft.ProgressRing(value=None, visible=False)


    # --- Building / Searching to create and display in the table ---
    def build_rows(search_query=None):
        # Ohne Suchbegriff werden alle Datensaetze geladen. Mit Suchbegriff
        # delegieren wir die Filterung an die Datenbankschicht.
        if search_query:
            columns, records = db_manager.search(search_query)
        else:
            columns, records = db_manager.fetch_query(
                "SELECT ID, Device, Type, Location FROM inventory"
            )

        def make_row(id, device, type_, location):
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
                # Der Zustand des Loeschbuttons haengt von der Auswahl ab.
                page.update()

            return fdt.DataRow2(
                on_select_change=handle_select_change,
                selected=id in selected_titles,
                cells=[
                    ft.DataCell(content=ft.Text(str(id))),
                    ft.DataCell(content=ft.Text(device)),
                    ft.DataCell(content=ft.Text(type_)),
                    ft.DataCell(content=ft.Text(location)),
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
            # Bei einer ungueltigen Abfrage bleibt die Tabelle leer, statt die
            # gesamte Benutzeroberflaeche abstuerzen zu lassen.
            table.rows = []
        table.update()
        loading_ring.visible = False
        page.update()
        
    def delete_selected():
        # Jede markierte ID wird einzeln aus der Datenbank geloescht.
        if not selected_titles:
            return

        for id in list(selected_titles):
            db_manager.device_delete(id)
            selected_titles.discard(id)

        refresh_table()

    def refresh_table(e=None):
        # Diese Funktion wird auch von main.py aufgerufen, wenn die Tabellen-
        # Seite geoeffnet wird oder ein neuer Datensatz gespeichert wurde.
        table.visible = True
        table.rows = build_rows()
        table.update()

    def handle_select_all(e):
        # Der Kopf der Tabelle kann alle vorhandenen IDs auf einmal auswaehlen
        # oder die Auswahl komplett leeren.
        _, records = db_manager.fetch_query("SELECT ID, Device, Type, Location FROM inventory")
        if e.data == "true":
            selected_titles.update(id for id, _, _, _ in records)
        else:
            selected_titles.clear()
        refresh_table()
    # --- Building / Searching to create and display in the table ---

    # Der Button ist anfangs deaktiviert, weil noch keine Zeile ausgewaehlt ist.
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
            fdt.DataColumn2(label=ft.Text("ID"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Device"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Type"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Location"), size=fdt.DataColumnSize.L),
        ],
        rows=build_rows(),
        on_select_all=handle_select_all,
    )


    # --- Dialog zum Anlegen eines neuen Geraets ---

    device_field = ft.TextField(label="Device")
    type_field = ft.TextField(label="Type")
    location_field = ft.TextField(label="Location")

    def close_dialog(e):
        # Der Dialog wird geschlossen, ohne die Datenbank zu veraendern.
        page.pop_dialog()
        page.update()

    def save_entry(e):
        # Werte aus den Eingabefeldern lesen und fuehrende/trailing Leerzeichen
        # entfernen, bevor sie in der Datenbank gespeichert werden.
        device = device_field.value.strip()
        type = type_field.value.strip()
        location = location_field.value.strip()

        if not device:
            # `error_text` zeigt die Fehlermeldung direkt unter dem Feld an.
            device_field.error_text = "Device is required"
            page.update()
            return

        if not type:
            type_field.error_text = "Type is required"
            page.update()
            return

        if not location:
            location_field.error_text = "Location is required"
            page.update()
            return

        # Erst wenn alle drei Werte vorhanden sind, wird der Datensatz angelegt.
        db_manager.device_create(device, type, location)

        device_field.value = ""
        type_field.value = ""
        location_field.value = ""

        page.pop_dialog()
        refresh_table()
        page.update()

    add_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Device"),
        content=ft.Column(
            [device_field, type_field, location_field],
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
        # Vor jedem Oeffnen werden die Felder zurueckgesetzt, damit kein alter
        # Inhalt aus einem vorherigen Dialog stehen bleibt.
        device_field.value = ""
        type_field.value = ""
        location_field.value = "None"
        page.show_dialog(add_dialog)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=open_add_dialog,
    )

    # Der FAB (Floating Action Button) ist das Plus-Symbol zum Anlegen.

    # Das Suchfeld reagiert auf Enter; das Lupen-Icon ruft denselben Handler auf.
    query_field = ft.TextField(
        label="Enter your Search Term",
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
                        query_field,
                        ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_query),
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