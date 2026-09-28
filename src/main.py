# main.py
import flet as ft

# Die drei Views sind die sichtbaren Seiten der Anwendung. Jede Funktion baut
# einen Teil der Benutzeroberfläche und gibt Flet-Steuerelemente zurück.
from views.dashboard import DashboardView
from views.settings import SettingsView
from views.device import DeviceView
from views.type import TypeView
from views.employee import EmployeeView
from scripts.database import DatabaseManager

# Die Datenbankdatei liegt im Ordner, aus dem `flet run` gestartet wird.
# Beim ersten Start wird sie automatisch angelegt.
DB_PATH = "database.db"
db_manager = DatabaseManager(DB_PATH)



def main(page: ft.Page):
    # `page` ist das Hauptfenster bzw. die Browser-Seite von Flet. Alles, was
    # der Benutzer sieht, wird später an diese Seite angehängt.
    page.title = "KeepIt"
    page.padding = 0

    # Die Anwendung benötigt ihre Tabellen, bevor eine View Daten lesen kann.
    # Wenn die Datei noch fehlt, legt DatabaseManager sie mit den Tabellen
    # `inventory` und `settings` an.
    if not db_manager.exists():
        (
        #alert_popup(
        #    "Database not found",
        #    f"The file '{DB_PATH}' could not be found. Would you like to create it now?",
        #    actions=[ft.TextButton("Create", on_click=create_file)],
        
        # Removing the alert popup and directly creating the database
        db_manager.initialize_database()
        )

    # DeviceView liefert zwei Dinge zurück:
    # - den Container, der später im Inhaltsbereich angezeigt wird
    # - eine Funktion, mit der die Tabelle neu aus der Datenbank gelesen wird
    device_container, refresh_devices = DeviceView(page, db_manager)
    type_container, refresh_types = TypeView(page, db_manager)
    employee_container, refresh_employees = EmployeeView(page, db_manager)

    # Dieses Bild ist das Logo oben in der Navigation. Die Quelle kann später
    # je nach hellem oder dunklem Farbschema ausgetauscht werden.
    keepit_icon = ft.Image(
        src="black-keepup-icon.svg",
        width=70,
        height=70,
        fit=ft.BoxFit.CONTAIN,
    )

    # Das Bild wird an `page` gespeichert, damit andere Funktionen dasselbe
    # Steuerelement später erreichen und seine Bilddatei ändern können.
    page.keepit_icon = keepit_icon 

    # Allgemeine Hilfsfunktion für ein Hinweisfenster. Sie wird aktuell nicht
    # benutzt, bleibt aber als Vorlage für spätere Dialoge erhalten.
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

    # Diese Funktion wäre der Klick-Handler für den alten "Create"-Button
    # des Datenbank-Dialogs. Die Datenbank wird inzwischen direkt beim Start
    # angelegt, daher wird diese Funktion aktuell nicht aufgerufen.
    def create_file(e):
        db_manager.initialize_database()
        page.pop_dialog()
        page.update()

    # Wenn das Betriebssystem ein dunkles Farbschema meldet, wird das helle
    # Logo verwendet. Im hellen Schema wird das dunkle Logo verwendet.
    if page.theme_mode == ft.ThemeMode.SYSTEM:
        if page.platform_brightness == ft.Brightness.DARK:
            page.keepit_icon.src = "white-keepup-icon.svg"
        else:
            page.keepit_icon.src = "black-keepup-icon.svg"



# ------------------------------------------------------------------------------------------------------

    # `content_area` ist ein Platzhalter für die aktuell ausgewählte Seite.
    content_area = ft.Container(content=DashboardView(page, db_manager), expand=True)

    # Dieser Handler tauscht die Seite aus, sobald sich die Auswahl der
    # Navigation ändert. Der Index 0 steht für Home, Index 1 für Table.
    def on_nav_change(e):
        index = e.control.selected_index
        match index:
            case 0:
                # Die Dashboard-Seite wird als neuer Inhalt eingesetzt.
                content_area.content = DashboardView(page, db_manager)
            case 1:
                # Vor dem Anzeigen wird die Tabelle erneut aus der Datenbank
                # geladen. So erscheinen neue Einträge sofort.
                content_area.content = device_container
                content_area.update()
                refresh_devices()
            case 2:
                content_area.content = type_container
                content_area.update()
                refresh_types()
            case 3:
                content_area.content = employee_container
                content_area.update()
                refresh_employees()

        page.update()

    def go_to_settings(e):
        # Einstellungen sind ein eigener Button und keine Destination der
        # Navigation. Deshalb wird dort keine Destination markiert.
        rail.selected_index = None
        content_area.content = SettingsView()
        page.update()

 

    # Die NavigationRail ist die senkrechte Leiste am linken Fensterrand.
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        on_change=on_nav_change,
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
        # Jede Destination besitzt ein normales und ein ausgewähltes Icon.
        # Flet zeigt ausserdem das hier angegebene Label an.
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
        # `trailing` platziert die Einstellungen am unteren Ende der Leiste.
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
    # `expand=True` nutzt den gesamten verfügbaren Platz.
    page.add(
        ft.Row(
            controls=[rail, ft.VerticalDivider(width=1), content_area],
            expand=True,
            spacing=0,
        )
    )


ft.run(main)