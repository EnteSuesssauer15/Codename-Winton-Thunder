import flet as ft
import scripts.database as db

db_manager = db.DatabaseManager()



def SettingsView():
    # handler for the dark mode toggle switch
    def handle_toggle_darkmode(e):
        # declares the page variable to access the page object
        page = e.control.page
        # Access the keepup_icon from the page's controls
        
        if e.control.value:
            page.theme_mode = ft.ThemeMode.DARK
            page.keepup_icon.src = "white-keepup-icon.svg"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.keepup_icon.src = "black-keepup-icon.svg"
        page.update()


        # saves the states in the database settings table
    def handle_save_settings(e):
        db_manager.settings_set("dark_mode", str(e.control.page.theme_mode == ft.ThemeMode.DARK))

    return ft.Container(
        content=ft.Column([
            ft.Text("Settings Page", size=28, weight=ft.FontWeight.BOLD),
            ft.Button("Save Settings", on_click=handle_save_settings),
        ]),
        padding=20,
        expand=True,
    )