# main.py
import flet as ft

# Die drei Views sind die sichtbaren Seiten der Anwendung. Jede Funktion baut
# einen Teil der Benutzeroberflaeche und gibt Flet-Steuerelemente zurueck.
from views.dashboard import DashboardView
from views.settings import SettingsView
from views.table import TableView
from scripts.database import DatabaseManager

# Die Datenbankdatei liegt im Ordner, aus dem `flet run` gestartet wird.
# Beim ersten Start wird sie automatisch angelegt.
DB_PATH = "database.db"
db_manager = DatabaseManager(DB_PATH)



def main(page: ft.Page):
    # `page` ist das Hauptfenster bzw. die Browser-Seite von Flet. Alles, was
    # der Benutzer sieht, wird spaeter an diese Seite angehaengt.
    page.title = "KeepUp"
    page.padding = 0

    # Die Anwendung benoetigt ihre Tabellen, bevor eine View Daten lesen kann.
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

    # TableView liefert zwei Dinge zurueck:
    # - den Container, der spaeter im Inhaltsbereich angezeigt wird
    # - eine Funktion, mit der die Tabelle neu aus der Datenbank gelesen wird
    table_container, refresh_table_view = TableView(page, db_manager)

    # Dieses Bild ist das Logo oben in der Navigation. Die Quelle kann spaeter
    # je nach hellem oder dunklem Farbschema ausgetauscht werden.
    keepup_icon = ft.Image(
        src="black-keepup-icon.svg",
        width=70,
        height=70,
        fit=ft.BoxFit.CONTAIN,
    )

    # Das Bild wird an `page` gespeichert, damit andere Funktionen dasselbe
    # Steuerelement spaeter erreichen und seine Bilddatei aendern koennen.
    page.keepup_icon = keepup_icon 

    # Allgemeine Hilfsfunktion fuer ein Hinweisfenster. Sie wird aktuell nicht
    # benutzt, bleibt aber als Vorlage fuer spaetere Dialoge erhalten.
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

    # Diese Funktion waere der Klick-Handler fuer den alten "Create"-Button
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
            page.keepup_icon.src = "white-keepup-icon.svg"
        else:
            page.keepup_icon.src = "black-keepup-icon.svg"



# ------------------------------------------------------------------------------------------------------

    # `content_area` ist ein Platzhalter fuer die aktuell ausgewaehlte Seite.
    content_area = ft.Container(content=DashboardView(page, db_manager), expand=True)

    # Dieser Handler tauscht die Seite aus, sobald sich die Auswahl der
    # Navigation aendert. Der Index 0 steht fuer Home, Index 1 fuer Table.
    def on_nav_change(e):
        index = e.control.selected_index
        match index:
            case 0:
                # Die Dashboard-Seite wird als neuer Inhalt eingesetzt.
                content_area.content = DashboardView(page, db_manager)
                page.floating_action_button.visible = True
            case 1:
                # Vor dem Anzeigen wird die Tabelle erneut aus der Datenbank
                # geladen. So erscheinen neue Eintraege sofort.
                page.floating_action_button.visible = True
                content_area.content = table_container
                content_area.update()  # attach it to the page tree FIRST
                refresh_table_view()
            #case 2:
                #content_area.content = QueryView(page, db_manager)
            #    page.floating_action_button.visible = True

        page.update()

    def go_to_settings(e):
        # Einstellungen sind ein eigener Button und keine Destination der
        # Navigation. Deshalb wird dort keine Destination markiert.
        rail.selected_index = None
        content_area.content = SettingsView()
        page.floating_action_button.visible = False
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
                    content=keepup_icon,
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
        # Jede Destination besitzt ein normales und ein ausgewaehltes Icon.
        # Flet zeigt ausserdem das hier angegebene Label an.
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationRailDestination(
                icon=ft.CupertinoIcons.TABLE,
                selected_icon=ft.CupertinoIcons.TABLE_FILL,
                label="Table",
            ),
            #ft.NavigationRailDestination(
            #    icon=ft.Icons.SEARCH_OUTLINED,
            #    selected_icon=ft.Icons.SEARCH,
            #    label="Query",
            #),
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
    # `expand=True` nutzt den gesamten verfuegbaren Platz.
    page.add(
        ft.Row(
            controls=[rail, ft.VerticalDivider(width=1), content_area],
            expand=True,
            spacing=0,
        )
    )


ft.run(main)