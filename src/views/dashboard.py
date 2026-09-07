# pages/home.py
import flet as ft
import flet_datatable2 as fdt
import os
import sys
import ctypes

def DashboardView(page: ft.Page, db_manager):
    selected_titles = set()

    def build_rows():
        _, records = db_manager.fetch_query("SELECT title, description FROM updates")

        def make_row(title, description):
            def handle_select_change(e: ft.Event[fdt.DataRow2]):
                e.control.selected = not e.control.selected
                if e.control.selected:
                    selected_titles.add(title)
                else:
                    selected_titles.discard(title)
                e.control.update()

            return fdt.DataRow2(
                on_select_change=handle_select_change,
                selected=title in selected_titles,
                cells=[
                    ft.DataCell(content=ft.Text(title)),
                    ft.DataCell(content=ft.Text(description)),
                ],
            )

        return [make_row(title, desc) for title, desc in records]

    def handle_select_all(e):
        _, records = db_manager.fetch_query("SELECT title, description FROM updates")
        if e.data == "true":
            selected_titles.update(title for title, _ in records)
        else:
            selected_titles.clear()
        table.rows = build_rows()
        table.update()

    def handle_install_selected(e):
        from scripts.updater import install_update_by_title
        for title in list(selected_titles):
            updater.install_update_by_title(title)

    def refresh_table(e=None):
        table.rows = build_rows()
        table.update()

    def search_for_updates(e):
        updater_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "scripts", "updater.py")
        )
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            f'"{updater_path}" check_updates',
            None,
            0,  # SW_HIDE
        )
        # updater.py writes results to the DB in a separate elevated process,
        # so this call returns immediately — the table won't reflect new
        # rows until you refresh (see note below).

    table = fdt.DataTable2(
        expand=True,
        show_checkbox_column=True,
        fixed_top_rows=1,
        empty=ft.Text("No updates found. Click 'Search for updates' to check."),
        columns=[
            fdt.DataColumn2(label=ft.Text("Title"), size=fdt.DataColumnSize.L),
            fdt.DataColumn2(label=ft.Text("Description"), size=fdt.DataColumnSize.L),
        ],
        rows=build_rows(),
        on_select_all=handle_select_all,
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Dashboard Page", size=28, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Button("Search for updates", on_click=search_for_updates),
                        ft.Button("Refresh list", on_click=refresh_table),
                        ft.Button("Install selected", on_click=handle_install_selected),
                    ]
                ),
                table,
            ],
            expand=True,
        ),
        padding=20,
        expand=True,
    )