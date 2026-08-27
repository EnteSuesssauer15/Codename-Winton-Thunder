# pages/home.py
import flet as ft
import flet_datatable2 as ft_dt

def QuerryView():
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.TextField(label="Enter your query", expand=True),
                ft_dt.DataTable(
                    columns=[
                        ft_dt.DataColumn(label=ft.Text("Column 1")),
                        ft_dt.DataColumn(label=ft.Text("Column 2")),
                    ],
                    rows=[
                        ft_dt.DataRow(cells=[ft_dt.DataCell(ft.Text("Row 1, Col 1")), ft_dt.DataCell(ft.Text("Row 1, Col 2"))]),
                    ],
                ),
            ]),
        ]),
        padding=20,
        expand=True,
    )