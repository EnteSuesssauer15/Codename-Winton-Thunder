# pages/home.py
import flet as ft
import flet_datatable2 as fdt
import os
import sys
import threading
from win32com.shell import shell, shellcon
import win32event
import win32process


def run_elevated_and_wait(exe_path, params):
    proc_info = shell.ShellExecuteEx(
        nShow=0,                     # 0 = hidden window
        fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
        lpVerb="runas",               # triggers UAC + elevation
        lpFile=exe_path,
        lpParameters=params,
    )
    handle = proc_info["hProcess"]
    win32event.WaitForSingleObject(handle, win32event.INFINITE)
    win32process.GetExitCodeProcess(handle)


def DashboardView(page: ft.Page, db_manager):
    selected_titles = set()
    loading_ring = ft.ProgressRing(value=None, visible=False)

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
                cells=[ft.DataCell(content=ft.Text(title)), ft.DataCell(content=ft.Text(description))],
            )

        return [make_row(title, desc) for title, desc in records]

    def refresh_table(e=None):
        table.rows = build_rows()
        table.update()

    def get_updater_path():
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "updater.py"))

    def search_for_updates(e):
        def worker():
            loading_ring.visible = True
            page.update()
            try:
                #run_elevated_and_wait(sys.executable, f'"{get_updater_path()}" check_updates')
                run_elevated_and_wait(sys.executable, f'"{get_updater_path()}" find_winget_updates')
            except Exception as e:
                print("Error occurred while checking updates:", e)
            finally:
                loading_ring.visible = False
                refresh_table()
                page.update()
        threading.Thread(target=worker, daemon=True).start()

    def handle_install_selected(e):
        def worker():
            loading_ring.visible = True
            page.update()
            try:
                for title in list(selected_titles):
                        run_elevated_and_wait(sys.executable, f'"{get_updater_path()}" install "{title}"')
            except Exception as e:
                print("Error occurred while installing updates:", e)
            finally:
                loading_ring.visible = False
                selected_titles.clear()
                refresh_table()
                page.update()
        threading.Thread(target=worker, daemon=True).start()

    def handle_select_all(e):
        _, records = db_manager.fetch_query("SELECT title, description FROM updates")
        if e.data == "true":
            selected_titles.update(title for title, _ in records)
        else:
            selected_titles.clear()
        refresh_table()

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
                ft.Row([
                    ft.Button("Search for updates", icon=ft.Icons.REFRESH, on_click=search_for_updates),
                    #ft.Button("Refresh list", on_click=refresh_table),
                    ft.Button("Install selected", icon=ft.Icons.DOWNLOAD, on_click=handle_install_selected),
                ]),
                table, loading_ring
            ],
            expand=True,
        ),
        padding=20,
        expand=True,
    )