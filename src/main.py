# main.py
import flet as ft
import os
import sys

from views.dashboard import DashboardView
from views.settings import SettingsView

#* der Inhalt dieser 3 ähnelt sich start - man hätte einige funktionen zusammenlegen können, so aber verständlicher zu verstehen
from views.device import DeviceView
from views.type import TypeView
from views.employee import EmployeeView
#* ---
from scripts.database import DatabaseManager


DB_PATH = "database.db"
db_manager = DatabaseManager(DB_PATH)



def main(page: ft.Page):
    page.title = "KeepIt"
    page.padding = 0

    content_area = None

    #? Kleine die das Fenster schließt
    async def quit_app():
        await page.window.destroy()

    #? Löscht die Datenbank und schließt die Anwendung
    async def delete_database_and_quit():
        db_manager.close()
        os.remove(str(os.path.abspath(db_manager.db_name)))
        await quit_app()

    #? erzeugt ein Pop-Up Fenster, dass die Anwendung schließt
    #? Nur verwendet bei kritischen fehlern, die die Anwendung nicht mehr starten lassen.
    def alert_popup(title, message, actions=None):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=actions or [ft.TextButton("Delete Database and Quit", on_click=delete_database_and_quit), ft.TextButton("Quit", on_click=quit_app)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialog)

    #? Die Anwendung benötigt ihre Tabellen, bevor eine View Daten lesen kann.
    #? Wenn die Datei noch fehlt, legt DatabaseManager sie mit den Tabellen
    #? `employees`, `devicetypes`,`inventory` und `settings` an.
    if not db_manager.exists():
        db_manager.initialize_database()
        db_manager.execute("PRAGMA foreign_keys = ON;")
    else:
        db_manager.execute("PRAGMA foreign_keys = ON;")

    #* Jede View liefert zwei Dinge zurück:
    #* - den Container, der später im Inhaltsbereich angezeigt wird
    #* - eine Funktion, mit der die Tabelle neu aus der Datenbank gelesen wird
    
    #* werden die views nicht korrekt geladen, wird ein Pop-Up angezeigt und die Anwendung beendet.
    try:
        device_container, refresh_devices = DeviceView(page, db_manager)
        type_container, refresh_types = TypeView(page, db_manager)
        employee_container, refresh_employees = EmployeeView(page, db_manager)

        #? `content_area` ist ein Platzhalter für die aktuell ausgewählte Seite.
        content_area = ft.Container(content=DashboardView(page, db_manager), expand=True)
    except Exception as ex:
        #? Wenn die Datenbank nicht initialisiert wurde oder nicht gelesen werden konnte, wird ein Popup angezeigt und die Anwendung beendet.
        alert_popup("Database couldn't be read correctly", "Please check the database and restart the application." + "\n\nError:\n" + str(ex) + "\n\nDatabase Path:\n" + str(os.path.abspath(db_manager.db_name)))

    #? Icon in der Seitenleiste
    keepit_icon = ft.Image(
        src="black-keepup-icon.svg",
        width=70,
        height=70,
        fit=ft.BoxFit.CONTAIN,
    )

    #? Das Bild wird an `page` gespeichert, damit andere Funktionen dasselbe
    #? Steuerelement später erreichen und seine Bilddatei ändern können.
    page.keepit_icon = keepit_icon 

    #? Jenachdem wie das System Theme ist wird das Icon auf Schwarz oder Weiß geändert
    if page.theme_mode == ft.ThemeMode.SYSTEM:
        if page.platform_brightness == ft.Brightness.DARK:
            page.keepit_icon.src = "white-keepup-icon.svg"
        else:
            page.keepit_icon.src = "black-keepup-icon.svg"

    #? Dieser Handler tauscht die Seite aus, sobald sich die Auswahl der Navigation ändert. Der Index 0 steht für Home, Index 1 für Devices.
    def on_nav_change(e):
        index = e.control.selected_index
        match index:
            case 0:
                #? Dashboard
                content_area.content = DashboardView(page, db_manager)
            case 1:
                #? Devices
                content_area.content = device_container
                content_area.update()
                refresh_devices()
            case 2:
                #? Types
                content_area.content = type_container
                content_area.update()
                refresh_types()
            case 3:
                #? Employees
                content_area.content = employee_container
                content_area.update()
                refresh_employees()

        page.update()

    def go_to_settings(e):
        #? Einstellungen sind ein eigener Button und keine Destination der Navigation. Deshalb wird dort keine Destination markiert.
        rail.selected_index = None
        content_area.content = SettingsView()
        page.update()

    #? Navbar ist die Seitenleiste am linken Rand
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=on_nav_change,
        leading=ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                #? Logo und Trennlinien am oberen Ende der Navigation.
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
        #? Jede Destination besitzt ein normales und ein ausgewähltes Icon.
        #? Flet zeigt ausserdem das hier angegebene Label an.
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
        #? `trailing` platziert die Einstellungen am unteren Ende der Leiste.
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

    #? Eine Row legt Navigation, Trennlinie und Inhaltsbereich nebeneinander.
    #? `expand=True` nutzt den gesamten verfügbaren Platz.
    page.add(
        ft.Row(
            controls=[rail, ft.VerticalDivider(width=1), content_area],
            expand=True,
            spacing=0,
        )
    )


ft.run(main)