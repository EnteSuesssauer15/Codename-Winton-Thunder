# main.py
import flet as ft
from views.dashboard import DashboardView
from views.settings import SettingsView
from views.querry import QuerryView    

def main(page: ft.Page):
    page.title = "App with Bottom Settings"
    page.padding = 0

    content_area = ft.Container(content=DashboardView(), expand=True)

    def go_to_settings(e):
        rail.selected_index = None          # deselect all destinations
        content_area.content = SettingsView()
        page.update()

    def on_nav_change(e):
        index = e.control.selected_index
        if index == 0:
            content_area.content = DashboardView()
        elif index == 1:
            content_area.content = QuerryView()
        # Add other pages here...
        content_area.update()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=on_nav_change,

        # SVG logo above the Home button
        leading = ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                # Logo
                ft.Container(
                    content=ft.Image(
                        src="keepup-icon.svg",
                        width=70,
                        height=70,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    padding=0,
                ),

                # Fixed Divider with explicit thickness
                ft.Divider(height=1, thickness=1, color=ft.Colors.GREY_400),

                # Grey area
                ft.Container(
                    bgcolor=ft.Colors.GREY_500,
                    height=2,
                    width=60,
                    alignment=ft.Alignment.CENTER,
                    border_radius=5,
                ),
            ],
        ),

        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SEARCH_OUTLINED,
                selected_icon=ft.Icons.SEARCH,
                label="Querry",
            ),
        ],

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
    

    page.add(
        ft.Row(
            controls=[rail, ft.VerticalDivider(width=1), content_area],
            expand=True,
            spacing=0,
        )
    )

ft.app(target=main)