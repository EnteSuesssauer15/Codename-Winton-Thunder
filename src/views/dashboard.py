# pages/home.py
import flet as ft
from scripts.database import DatabaseManager

db_manager = DatabaseManager()

def DashboardView(page: ft.Page, db_manager):

    device_field = ft.TextField(label="Device")
    type_field = ft.TextField(label="Type")
    location_field = ft.TextField(label="Location")

    def close_dialog(e):
        page.pop_dialog()
        page.update()

    def save_entry(e):
        device = device_field.value.strip()
        type = type_field.value.strip()
        location = location_field.value.strip()

        if not device:
            device_field.error_text = "Device is required"
            page.update()
            return

        if not type:
            type_field.error_text = "Type is required"
            page.update()
            return

        if not location:
            location_field.error_text = "Location is required"
            page.update()
            return

        db_manager.device_create(device, type, location)

        device_field.value = ""
        type_field.value = ""
        location_field.value = ""

        page.pop_dialog()
        page.update()

    add_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Device"),
        content=ft.Column(
            [device_field, type_field, location_field],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Save", on_click=save_entry),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_add_dialog(e):
        device_field.value = ""
        type_field.value = ""
        location_field.value = "None"
        page.show_dialog(add_dialog)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=open_add_dialog,
    )

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