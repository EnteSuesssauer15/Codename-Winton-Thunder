# views/query.py
import flet as ft
import flet_datatable2 as fdt


def TableView(page: ft.Page, db_manager):
    selected_titles = set()
    loading_ring = ft.ProgressRing(value=None, visible=False)

    def build_rows():
        _, records = db_manager.fetch_query("SELECT ID, Device, Type, Location FROM inventory")

        def make_row(id, device, type, location):
            def handle_select_change(e: ft.Event[fdt.DataRow2]):
                e.control.selected = not e.control.selected
                if e.control.selected:
                    selected_titles.add(id)
                else:
                    selected_titles.discard(id)
                e.control.update()

                if selected_titles:
                    delete_button.disabled = False
                else:
                    delete_button.disabled = True

                page.update()

            return fdt.DataRow2(
                on_select_change=handle_select_change,
                selected=id in selected_titles,
                cells=[
                    ft.DataCell(content=ft.Text(str(id))),
                    ft.DataCell(content=ft.Text(device)),
                    ft.DataCell(content=ft.Text(type)),
                    ft.DataCell(content=ft.Text(location))
                ],
            )

        return [make_row(id, device, type, location) for id, device, type, location in records]

    def delete_selected():
        if not selected_titles:
            return

        for id in list(selected_titles):
            db_manager.device_delete(id)
            selected_titles.discard(id)

        refresh_table()

    delete_button = ft.Button(
        "delete selected",
        icon=ft.CupertinoIcons.TRASH,
        on_click=delete_selected,
        disabled=True,
    )

    def refresh_table(e=None):
        table.visible = True
        print(selected_titles)
        table.rows = build_rows()
        table.update()

    def handle_select_all(e):
        _, records = db_manager.fetch_query("SELECT ID, Device, Type, Location FROM inventory")
        if e.data == "true":
            selected_titles.update(id for id, _, _, _ in records)
        else:
            selected_titles.clear()
        refresh_table()



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

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([
                    ft.Button("Refresh list", icon=ft.Icons.REFRESH, on_click=refresh_table),
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