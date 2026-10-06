# dashboard.py
# Diese Datei beschreibt den Inhalt der Home-Seite (Dashboard).
# Sie zeigt Kennzahlen (Anzahl Geräte, Mitarbeiter, Typen) und wie viele
# Geräte es pro Typ gibt.
#
# Diese Datei wurde hauptsächlich von KI generiert.
import flet as ft


def make_stat_card(title, value, icon):
    # Erstellt eine Karte mit Icon, großer Zahl und Beschriftung darunter,
    # z. B. Icon + "12" + "Total devices".
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
    # Baustein (Vorlage), der mit Daten aufgerufen wird und eine Zeile der
    # Übersicht "Geräte pro Typ" erstellt: Typname, Fortschrittsbalken, Anzahl.
    # `share` ist der Anteil dieses Typs an allen Geräten (Wert zwischen 0 und 1)
    # und bestimmt, wie weit der Balken gefüllt ist.
    # Die Prüfung auf `total > 0` verhindert eine Division durch null.
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
    # Fragt die Anzahl der Einträge aus den drei Tabellen ab.
    # `COUNT(*)` liefert genau eine Zeile mit einer Spalte, deshalb steht
    # die Zahl in rows[0][0] (erste Zeile, erste Spalte).
    columns, rows = db_manager.fetch_query("SELECT COUNT(*) FROM inventory")
    device_count = rows[0][0]

    columns, rows = db_manager.fetch_query("SELECT COUNT(*) FROM employees")
    employee_count = rows[0][0]

    columns, rows = db_manager.fetch_query("SELECT COUNT(*) FROM devicetypes")
    type_count = rows[0][0]

    # Anzahl der Geräte pro Typ. `GROUP BY` fasst alle Geräte mit gleichem Typ
    # zusammen, sodass jede Zeile so aussieht: ("Computer", 5).
    columns, type_rows = db_manager.fetch_query(
        "SELECT Type_Id, COUNT(*) FROM inventory GROUP BY Type_Id"
    )

    # Erstellt die "Tabelle" mit der Anzahl der Geräte pro Typ.
    # Gibt es noch keine Geräte, wird stattdessen ein Hinweistext angezeigt.
    type_section = ft.Column(spacing=15)
    if len(type_rows) == 0:
        type_section.controls.append(ft.Text("No devices yet."))
    else:
        for row in type_rows:
            type_section.controls.append(
                make_type_row(row[0], row[1], device_count)
            )

    # Zusammenbau der Ansicht: Überschrift, eine Reihe mit den drei Karten
    # und darunter der Bereich "Devices per type".
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
                    # `wrap=True`: Ist das Fenster zu schmal, rutschen die Karten in die nächste Zeile.
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
            # Zeigt automatisch eine Scrollleiste, wenn der Inhalt nicht ins Fenster passt.
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=20,
        expand=True,
    )
