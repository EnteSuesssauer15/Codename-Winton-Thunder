# pages/home.py
import flet as ft

def DashboardView():
    return ft.Container(
        content=ft.Column([
            ft.Text("Dashboard Page", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Welcome to the main dashboard!"),
        ]),
        padding=20,
        expand=True,
    )