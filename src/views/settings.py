import flet as ft
import scripts.database as db

db_manager = db.DatabaseManager()



def SettingsView():
        # saves the states in the database settings table
        # Dieser Handler wird beim Klick auf den Speichern-Button ausgefuehrt.
        # Die eigentliche Speicherung ist noch auskommentiert und daher vorbereitet,
        # aber noch nicht aktiv.
    def handle_save_settings(e):
        print("Settings saved successfully.")
        #db_manager.settings_set("dark_mode", str(e.control.page.theme_mode == ft.ThemeMode.DARK))

        # Container und Column ordnen Ueberschrift und Button untereinander an.
    return ft.Container(
        content=ft.Column([
            ft.Text("Settings Page", size=28, weight=ft.FontWeight.BOLD),
            ft.Button("Save Settings", on_click=handle_save_settings),
        ]),
        padding=20,
        expand=True,
    )