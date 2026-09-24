# Diese Datei beschreibt den Inhalt der Home-Seite.
import flet as ft

# Hier gab es starke unterstützung von KI

def make_stat_card(title, value, icon):
    # Erstellt jeweils eine Karte mit Icon und Text
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(icon, size=32, color=ft.Colors.PRIMARY),
                ft.Text(str(value), size=40, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=14, color=ft.Colors.ON_SURFACE_VARIANT),
            ],
            spacing=4,
        ),
        width=220,
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )


def make_type_row(type_name, count, total):
    # Prefab die mit daten gerufen wird und somit die Übersicht für Geräte pro Typ erstellt
    if total > 0:
        share = count / total
    else:
        share = 0

    return ft.Row(
        [
            ft.Text(type_name, width=120),
            ft.ProgressBar(value=share, expand=True, bar_height=10),
            ft.Text(str(count), width=40, text_align=ft.TextAlign.END),
        ],
        spacing=15,
    )


def DashboardView(page: ft.Page, db_manager):
    # Anzahl aus den 3 Tabellen anfordern
    columns, rows = db_manager.fetch_query("SELECT COUNT(*) FROM inventory")
    device_count = rows[0][0]

    columns, rows = db_manager.fetch_query("SELECT COUNT(*) FROM employees")
    employee_count = rows[0][0]

    columns, rows = db_manager.fetch_query("SELECT COUNT(*) FROM devicetypes")
    type_count = rows[0][0]

    # Anzahl für Geräte pro Typ
    columns, type_rows = db_manager.fetch_query(
        "SELECT Type_Id, COUNT(*) FROM inventory GROUP BY Type_Id"
    )

    # Erstellt die "Tabelle" für die Anzahl der Geräten pro Typ
    type_section = ft.Column(spacing=15)
    if len(type_rows) == 0:
        type_section.controls.append(ft.Text("No devices yet."))
    else:
        for row in type_rows:
            type_section.controls.append(
                make_type_row(row[0], row[1], device_count)
            )

    # Zusammenbau der Ansicht
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        make_stat_card("Total devices", device_count, ft.Icons.DEVICES),
                        make_stat_card("Employees", employee_count, ft.Icons.PEOPLE),
                        make_stat_card("Device types", type_count, ft.Icons.CATEGORY),
                    ],
                    wrap=True,
                    spacing=20,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Devices per type", size=20, weight=ft.FontWeight.BOLD),
                            type_section,
                        ],
                        spacing=20,
                    ),
                    padding=20,
                    border_radius=16,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                ),
            ],
            spacing=25,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=20,
        expand=True,
    )