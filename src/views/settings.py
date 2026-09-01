import flet as ft
import scripts.database as db

db_manager = db.DatabaseManager()



def SettingsView():
    # handler for the dark mode toggle switch
    def handle_toggle_darkmode(e):
        # declares the page variable to access the page object
        page = e.control.page
        if e.control.value:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()


        # saves the states in the database settings table
    def handle_save_settings(e):
        db_manager.settings_set("dark_mode", str(e.control.page.theme_mode == ft.ThemeMode.DARK))

    return ft.Container(
        content=ft.Column([
            ft.Text("Settings Page", size=28, weight=ft.FontWeight.BOLD),
            ft.Switch(label="Dark Mode", value=db_manager.settings_get("dark_mode") == "True", on_change=handle_toggle_darkmode),
            ft.Button("Save Settings", on_click=handle_save_settings),
        ]),
        padding=20,
        expand=True,
    )