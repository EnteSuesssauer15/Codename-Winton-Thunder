# main.py
# Einstiegspunkt der Anwendung. Diese Datei wird gestartet und baut das
# Hauptfenster zusammen: links die Navigationsleiste, rechts der Inhaltsbereich,
# in dem die jeweils ausgewählte Seite (View) angezeigt wird.
import flet as ft
import os
import sys

from views.dashboard import DashboardView
from views.settings import SettingsView

# Die folgenden drei Views (Geräte, Typen, Mitarbeiter) sind fast gleich aufgebaut.
# Man hätte gemeinsame Funktionen zusammenlegen können. Getrennt sind sie aber
# leichter zu lesen, weil jede Datei für sich allein verständlich ist.
from views.device import DeviceView
from views.type import TypeView
from views.employee import EmployeeView
from scripts.database import DatabaseManager


# Pfad zur SQLite-Datenbankdatei. Ein relativer Pfad bedeutet: Die Datei liegt
# in dem Ordner, aus dem die Anwendung gestartet wurde.
DB_PATH = "database.db"
# Ein einziges DatabaseManager-Objekt, das an alle Views weitergegeben wird.
# Über dieses Objekt laufen alle Lese- und Schreibzugriffe auf die Datenbank.
db_manager = DatabaseManager(DB_PATH)


# Flet ruft diese Funktion beim Start einmal auf und übergibt `page`.
# `page` ist das Anwendungsfenster, in das alle Steuerelemente eingefügt werden.
def main(page: ft.Page):
    page.title = "KeepIt"
    page.padding = 0

    # Wird weiter unten mit dem Inhaltsbereich befüllt. Hier schon auf None
    # gesetzt, damit die Variable auch dann existiert, wenn das Laden fehlschlägt.
    content_area = None

    # Kleine Hilfsfunktion, die das Fenster schließt und die Anwendung beendet.
    # `async` ist nötig, weil `page.window.destroy()` mit `await` aufgerufen wird.
    async def quit_app():
        await page.window.destroy()

    # Schließt die Verbindung zur Datenbank, löscht die Datenbankdatei und beendet
    # die Anwendung. Beim nächsten Start wird dann eine neue, leere Datenbank angelegt.
    async def delete_database_and_quit():
        db_manager.close()
        os.remove(str(os.path.abspath(db_manager.db_name)))
        await quit_app()

    # Zeigt ein Pop-up-Fenster mit Titel und Nachricht an.
    # Wird nur bei kritischen Fehlern verwendet, bei denen die Anwendung nicht
    # sinnvoll weiterlaufen kann. Werden keine eigenen Buttons (`actions`)
    # übergeben, bietet das Fenster "Datenbank löschen und beenden" oder
    # "Beenden" an.
    def alert_popup(title, message, actions=None):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=actions or [ft.TextButton("Delete Database and Quit", on_click=delete_database_and_quit), ft.TextButton("Quit", on_click=quit_app)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    # Die Anwendung benötigt ihre Tabellen, bevor eine View Daten lesen kann.
    # Wenn die Datei noch fehlt, legt DatabaseManager sie mit den Tabellen
    # `employees`, `devicetypes`, `inventory` und `settings` an.
    # "PRAGMA foreign_keys = ON" schaltet in SQLite die Prüfung von
    # Fremdschlüsseln ein. Dadurch kann z. B. kein Mitarbeiter gelöscht werden,
    # dem noch ein Gerät zugewiesen ist. SQLite merkt sich diese Einstellung nur
    # für die aktuelle Verbindung, deshalb wird sie bei jedem Start gesetzt.
    if not db_manager.exists():
        db_manager.initialize_database()
        db_manager.execute("PRAGMA foreign_keys = ON;")
    else:
        db_manager.execute("PRAGMA foreign_keys = ON;")

    # Jede der drei Tabellen-Views liefert zwei Dinge zurück:
    # - den Container, der später im Inhaltsbereich angezeigt wird
    # - eine Funktion, mit der die Tabelle neu aus der Datenbank gelesen wird
    #
    # Werden die Views nicht korrekt geladen (z. B. weil die Datenbank defekt ist),
    # wird ein Pop-up angezeigt, über das die Anwendung beendet werden kann.
    try:
        device_container, refresh_devices = DeviceView(page, db_manager)
        type_container, refresh_types = TypeView(page, db_manager)
        employee_container, refresh_employees = EmployeeView(page, db_manager)

        # `content_area` ist ein Platzhalter für die aktuell ausgewählte Seite.
        # Beim Start wird dort das Dashboard (Home) angezeigt.
        content_area = ft.Container(content=DashboardView(page, db_manager), expand=True)
    except Exception as ex:
        # Wenn die Datenbank nicht initialisiert wurde oder nicht gelesen werden
        # konnte, wird ein Pop-up mit Fehlermeldung und Datenbankpfad angezeigt.
        alert_popup("Database couldn't be read correctly", "Please check the database and restart the application." + "\n\nError:\n" + str(ex) + "\n\nDatabase Path:\n" + str(os.path.abspath(db_manager.db_name)))

    # Logo, das oben in der Seitenleiste angezeigt wird.
    # Die Bilddatei wird im Ordner `src/assets` gesucht.
    keepit_icon = ft.Image(
        src="black-keepup-icon.svg",
        width=70,
        height=70,
        fit=ft.BoxFit.CONTAIN,
    )

    # Das Bild wird an `page` gespeichert, damit andere Funktionen dasselbe
    # Steuerelement später erreichen und seine Bilddatei ändern können.
    page.keepit_icon = keepit_icon

    # Je nachdem, ob das Betriebssystem im hellen oder dunklen Modus läuft, wird
    # das schwarze oder weiße Logo verwendet, damit es auf dem Hintergrund sichtbar ist.
    if page.theme_mode == ft.ThemeMode.SYSTEM:
        if page.platform_brightness == ft.Brightness.DARK:
            page.keepit_icon.src = "white-keepup-icon.svg"
        else:
            page.keepit_icon.src = "black-keepup-icon.svg"

    # Wird aufgerufen, sobald in der Navigationsleiste ein anderer Eintrag
    # angeklickt wird. `selected_index` gibt an, welcher Eintrag gewählt wurde.
    # Die Reihenfolge entspricht der Liste `destinations` weiter unten:
    # 0 = Home, 1 = Devices, 2 = Types, 3 = Employees.
    def on_nav_change(e):
        index = e.control.selected_index
        match index:
            case 0:
                # Dashboard: wird jedes Mal neu erstellt, damit die Zahlen aktuell sind.
                content_area.content = DashboardView(page, db_manager)
            case 1:
                # Devices: View anzeigen und danach die Tabelle neu laden.
                content_area.content = device_container
                content_area.update()
                refresh_devices()
            case 2:
                # Types: View anzeigen und danach die Tabelle neu laden.
                content_area.content = type_container
                content_area.update()
                refresh_types()
            case 3:
                # Employees: View anzeigen und danach die Tabelle neu laden.
                content_area.content = employee_container
                content_area.update()
                refresh_employees()

        # Änderungen an Steuerelementen werden erst nach `update()` im Fenster sichtbar.
        page.update()

    # Öffnet die Einstellungsseite.
    def go_to_settings(e):
        # Die Einstellungen sind ein eigener Button und kein Eintrag (Destination)
        # der Navigation. Deshalb wird die Markierung in der Leiste entfernt.
        rail.selected_index = None
        content_area.content = SettingsView()
        page.update()

    # Die NavigationRail ist die Seitenleiste am linken Rand.
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=on_nav_change,
        # `leading` ist der Bereich ganz oben in der Leiste, über den Einträgen.
        leading=ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                # Logo und Trennlinien am oberen Ende der Navigation.
                ft.Container(
                    content=keepit_icon,
                ),
                ft.Divider(height=1, thickness=1, color=ft.Colors.GREY_400),
                ft.Container(
                    bgcolor=ft.Colors.GREY_500,
                    height=2,
                    width=60,
                    alignment=ft.Alignment.CENTER,
                    border_radius=5,
                ),
            ],
        ),
        # Die Einträge der Navigation. Jeder Eintrag besitzt ein normales und ein
        # ausgewähltes Icon. Flet zeigt außerdem das hier angegebene Label an.
        # Die Reihenfolge bestimmt den Index, der in `on_nav_change` ankommt.
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.COMPUTER,
                selected_icon=ft.Icons.COMPUTER,
                label="Devices",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.APPS,
                selected_icon=ft.Icons.APPS,
                label="Types",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PERSON_OUTLINE,
                selected_icon=ft.Icons.PERSON,
                label="Employees",
            ),
        ],
        # `trailing` platziert den Einstellungen-Button am unteren Ende der Leiste.
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

    # Eine Row legt Navigation, Trennlinie und Inhaltsbereich nebeneinander.
    # `expand=True` nutzt den gesamten verfügbaren Platz im Fenster.
    page.add(
        ft.Row(
            controls=[rail, ft.VerticalDivider(width=1), content_area],
            expand=True,
            spacing=0,
        )
    )


# Startet die Flet-Anwendung und ruft dabei die Funktion `main` auf.
ft.run(main)
