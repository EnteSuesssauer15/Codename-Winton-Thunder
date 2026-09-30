# views/query.py
import flet as ft
import flet_datatable2 as fdt


def TypeView(page: ft.Page, db_manager):
    #* Diese Menge merkt sich die IDs der aktuell markierten Zeilen. IDs sind
    #* stabiler als Gerätenamen, weil mehrere Geräte gleich heißen können.
    selected_titles = set()

    #? Anfang Erstellung der Tabelle aus den Datenbankeinträgen
    def build_rows(search_query=None):
        #? Ohne Suchbegriff werden alle Datensätze geladen. Mit Suchbegriff delegieren wir die Filterung an die Datenbankschicht.
        if search_query:
            #? Festlegung der lokalen Variablen die von der aufgerufenen Funktion befüllt werden
            columns, records = db_manager.search_type(search_query)
        else:
            #? Hier werden alle Reihen ausgegeben, da nicht gesucht wird.
            #? Die Variablen müssen ebenfalls deklariert werden und werden ebenfalls befüllt von der Funktion
            columns, records = db_manager.fetch_query(
                "SELECT TypeId, Short FROM devicetypes"
            )
        #! Wird erst am ende der Funktion aufgerufen
        def make_row(id, name):
            # Aus einem Datenbank-Datensatz wird eine sichtbare Tabellenzeile.
            def handle_select_change(e: ft.Event[fdt.DataRow2]):
                #? Beim Anklicken einer Checkbox wird die ID in die Auswahl
                #? aufgenommen oder wieder daraus entfernt.
                e.control.selected = not e.control.selected
                if e.control.selected:
                    selected_titles.add(id)
                else:
                    selected_titles.discard(id)
                e.control.update()

                #? Der Zustand des Löschbuttons hängt von der Auswahl ab.
                type_delete_button.disabled = not bool(selected_titles)
                page.update()

            #? Hier wird erst die Datenbank erstellt
            #* Jeder Parameter braucht seine eigene DataCell in der Tabelle von Flet um jeden Wert eingeben zu können, es darf nie eine Spalte leer bleiben
            #* Jeder durchlauf von dieser make_row Funktion erstellt hiermit eine einzige Reihe in der gesamten Tabelle
            return fdt.DataRow2(
                on_select_change=handle_select_change,
                selected=id in selected_titles,
                cells=[
                    ft.DataCell(content=ft.Text(id)),
                    ft.DataCell(content=ft.Text(name)),
                ],
            )
        #? Hier wird die Funktion make_row aufgerufen welche pro Spalte ihren eigenen Paremeter mitgegeben bekommt und pro Eintrag die Reihen erstellt
        return [make_row(*record) for record in records]

    def run_query(e):
        query = type_search_bar.value
        #? Bei einer ungültigen Abfrage bleibt die Tabelle leer, statt die gesamte Benutzeroberfläche abstürzen zu lassen.
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

        for id in list(selected_titles):
            db_manager.type_delete(id)
            selected_titles.discard(id)

        type_delete_button.disabled = True

        refresh_types()

    #? Baut die Tabelle neu zusammen
    def refresh_types(e=None):
        table.visible = True
        table.rows = build_rows()
        page.update()

    def handle_select_all(e):
        #? Der Kopf der Tabelle kann alle vorhandenen IDs auf einmal auswählen oder die Auswahl komplett leeren.
        _, records = db_manager.fetch_query("SELECT TypeId, Short FROM devicetypes")
        if e.data == True:
            selected_titles.update(id for id, _, in records)
            type_delete_button.disabled = False
        else:
            selected_titles.clear()
            type_delete_button.disabled = True
        refresh_types()

    # ? Ende Löschfunktion (wiederholend pro Seite)

    type_delete_button = ft.Button(
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
        empty=ft.Text("No Types"),
        columns=[
            fdt.DataColumn2(label=ft.Text("Devicetype"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Short"), size=fdt.DataColumnSize.L),
        ],
        rows=build_rows(),
        on_select_all=handle_select_all,
    )


    #? Dialog zum Anlegen eines neuen Typen
    
    #? Definition der Dropdown Menüs, sodass diese nicht nur innerhalb der Funktion verfügbar sind
    add_type_dialog_devicetype = ft.TextField(label="Device Type")
    add_type_dialog_short = ft.TextField(label="Short", tooltip="Shorts will be visible at the beginning of every InventoryNr")

    #? Schließt das Popup Fenster auf "Cancel"
    def close_dialog(e):
        page.pop_dialog()
        page.update()

    #? Speichert den neuen Eintrag auf "Save"
    def save_entry(e):
        #? Werte lesen; Dropdowns liefern None, wenn nichts gewählt wurde.
        #? "or ''" macht daraus einen leeren String, damit .strip() sicher funktioniert.
        type = (add_type_dialog_devicetype.value or "").strip()
        short = (add_type_dialog_short.value or "").strip()

        #? Alte Fehlermeldungen zurücksetzen
        add_type_dialog_devicetype.error = None
        add_type_dialog_short.error = None

        #? Validierung: alle Felder prüfen, sodass keines davon leer ist
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

        #? Erst wenn alle drei Werte vorhanden sind, wird der Datensatz angelegt.
        db_manager.type_create(type, short)

        page.pop_dialog()
        refresh_types()
        page.update()

    #? Popupobjekt welches hier definiert wird
    add_type_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New type"),
        content=ft.Column(
            #? welche Objekte von Flet in diesem Dialog sein sollen
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
        #? Vor jedem Öffnen werden die Felder zurückgesetzt, damit kein alter Inhalt aus einem vorherigen Dialog stehen bleibt.
        add_type_dialog_devicetype.value = ""
        add_type_dialog_short.value = ""

        page.show_dialog(add_type_dialog)


    #? Der Knopf, welcher das Menü zur Typenerstellung öffnet
    add_type_btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        content=ft.Text("Add type"),
        width=150,
        on_click=open_add_dialog,
    )

    #? Das Suchfeld
    type_search_bar = ft.TextField(
        label="Enter Type or Short",
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
                        type_search_bar, ft.IconButton(icon=ft.Icons.SEARCH, on_click=run_query), add_type_btn,
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