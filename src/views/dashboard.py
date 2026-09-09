# pages/home.py
import flet as ft
from scripts.database import DatabaseManager

db_manager = DatabaseManager()

def DashboardView(page: ft.Page, db_manager):

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Dashboard Page", size=28, weight=ft.FontWeight.BOLD),
            ],
            expand=True,
        ),
        padding=20,
        expand=True,
    )