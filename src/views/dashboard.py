# Diese Datei beschreibt den Inhalt der Home-Seite.
import flet as ft
from scripts.database import DatabaseManager

# Dieser globale Manager wird aktuell nicht benoetigt; main.py uebergibt den
# zentralen Manager bereits an DashboardView. Er bleibt als spaetere Vorlage.
db_manager = DatabaseManager()

def DashboardView(page: ft.Page, db_manager):
    # Eine View ist eine Funktion, die Flet-Steuerelemente zurueckgibt.
    # `page` und `db_manager` stehen fuer spaetere Dashboard-Funktionen bereit.

    return ft.Container(
        content=ft.Column(
            [
                # Aktueller Platzhalter fuer den spaeteren Dashboard-Inhalt.
                ft.Text("Dashboard Page", size=28, weight=ft.FontWeight.BOLD),
            ],
            expand=True,
        ),
        padding=20,
        expand=True,
    )