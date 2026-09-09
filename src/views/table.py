# views/query.py
import flet as ft
import flet_datatable2 as fdt


def TableView(page: ft.Page, db_manager):
    selected_titles = set()
    loading_ring = ft.ProgressRing(value=None, visible=False)

    def build_rows(search_query=None):
        if search_query:
            columns, records = db_manager.search(search_query)
        else:
            columns, records = db_manager.fetch_query(
                "SELECT ID, Device, Type, Location FROM inventory"
            )

        def make_row(id, device, type_, location):
            def handle_select_change(e: ft.Event[fdt.DataRow2]):
                e.control.selected = not e.control.selected
                if e.control.selected:
                    selected_titles.add(id)
                else:
                    selected_titles.discard(id)
                e.control.update()

                delete_button.disabled = not bool(selected_titles)
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
        query = query_field.value
        try:
            table.rows = build_rows(query if query else None)
        except Exception as ex:
            table.rows = []
        table.update()
        page.update()
        
    def delete_selected():
        if not selected_titles:
            return

        for id in list(selected_titles):
            db_manager.device_delete(id)
            selected_titles.discard(id)

        refresh_table()

    def refresh_table(e=None):
        table.visible = True
        table.rows = build_rows()
        table.update()

    def handle_select_all(e):
        _, records = db_manager.fetch_query("SELECT ID, Device, Type, Location FROM inventory")
        if e.data == "true":
            selected_titles.update(id for id, _, _, _ in records)
        else:
            selected_titles.clear()
        refresh_table()

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

    device_field = ft.TextField(label="Device")
    type_field = ft.TextField(label="Type")
    location_field = ft.TextField(label="Location")

    def close_dialog(e):
        page.pop_dialog()
        page.update()

    def save_entry(e):
        device = device_field.value.strip()
        type = type_field.value.strip()
        location = location_field.value.strip()

        if not device:
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

    query_field = ft.TextField(
        label="Enter your SQL query",
        on_submit=run_query,
        expand=True,
    )

    def open_add_dialog(e):
        device_field.value = ""
        type_field.value = ""
        location_field.value = "None"
        page.show_dialog(add_dialog)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=open_add_dialog,
    )
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