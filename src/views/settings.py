# pages/settings.py
import flet as ft

def SettingsView():
    return ft.Container(
        content=ft.Column([
            ft.Text("Settings Page", size=28, weight=ft.FontWeight.BOLD),
            ft.Switch(label="Dark Mode"),
        ]),
        padding=20,
        expand=True,
    )