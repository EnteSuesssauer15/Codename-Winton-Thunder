# views/query.py
import flet as ft
import flet_datatable2 as ft_dt


def QueryView(page: ft.Page, db_manager):

    table = ft_dt.DataTable2(
        columns=[ft_dt.DataColumn2(label=ft.Text(""))],
        rows=[],
        expand=True,
    )

    status_text = ft.Text("", color=ft.Colors.RED)

    def run_query(e):
        query = query_field.value
        if not query:
            return

        try:
            columns, rows = db_manager.fetch_query(query)
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            table.columns = [ft_dt.DataColumn2(label=ft.Text(""))]
            table.rows = []
            page.update()
            return

        status_text.value = ""
        table.columns = [ft_dt.DataColumn2(label=ft.Text(col)) for col in columns]
        table.rows = [
            ft_dt.DataRow2(cells=[ft.DataCell(ft.Text(str(value))) for value in row])
            for row in rows
        ]
        page.update()

    query_field = ft.TextField(
        label="Enter your SQL query",
        on_submit=run_query,
        expand=True,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[query_field, ft.Button("Run", on_click=run_query)]),
                status_text,
                ft.Container(content=table, expand=True),
            ],
            spacing=20,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )