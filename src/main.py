# main.py
import flet as ft
import os
from views.dashboard import DashboardView
from views.settings import SettingsView
from views.query import QueryView
from scripts.database import DatabaseManager

DB_PATH = "database.db"
db_manager = DatabaseManager(DB_PATH)


def main(page: ft.Page):
    page.title = "App with Bottom Settings"
    page.padding = 0

    # reusable alert dialog
    def alert_popup(title, message, actions=None):
        def default_ok(e):
            page.pop_dialog()
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=actions or [ft.TextButton("OK", on_click=default_ok)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    # --- handler that actually creates the DB ---
    def create_file(e):
        db_manager.initialize_database()
        page.pop_dialog()
        page.update()

    # --- startup check: file missing? - loading settings ---

    if db_manager.exists():
        if db_manager.settings_get("dark_mode") == "True":
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
    else:
        alert_popup(
            "Database not found",
            f"The file '{DB_PATH}' could not be found. Would you like to create it now?",
            actions=[ft.TextButton("Create", on_click=create_file)],
        )



# ------------------------------------------------------------------------------------------------------

    # Main Window
    content_area = ft.Container(content=DashboardView(), expand=True)

    # simple navbar index page handler that switches the content area based on the selected index
    def on_nav_change(e):
        index = e.control.selected_index
        match index:
            case 0:
                content_area.content = DashboardView()
            case 1:
                content_area.content = QueryView(page, db_manager)
        content_area.update()

    def go_to_settings(e):
        rail.selected_index = None
        content_area.content = SettingsView()
        page.update()


    # Navbar
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=on_nav_change,
        leading=ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                # navbar icon at the top
                ft.Container(
                    content=ft.Image(
                        src="keepup-icon.svg",
                        width=70,
                        height=70,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    padding=0,
                ),
                ft.Divider(height=1, thickness=1, color=ft.Colors.GREY_400),
                # horizontal divider line below the icon
                ft.Container(
                    bgcolor=ft.Colors.GREY_500,
                    height=2,
                    width=60,
                    alignment=ft.Alignment.CENTER,
                    border_radius=5,
                ),
            ],
        ),
        # declaration of the navbar icons and names - more here https://studio.flet.dev/gallery/run/apps/icons_browser/
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SEARCH_OUTLINED,
                selected_icon=ft.Icons.SEARCH,
                label="Query",
            ),
        ],
        # trailing = Settings button at the bottom of the navbar
        trailing=ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                tooltip="Settings",
                on_click=go_to_settings,
            ),
            padding=20,
        ),
        pin_trailing_to_bottom=True,
        group_alignment=-1.0,
    )

    # construct the main page layout with the navbar and content area
    page.add(
        ft.Row(
            controls=[rail, ft.VerticalDivider(width=1), content_area],
            expand=True,
            spacing=0,
        )
    )


ft.run(main)