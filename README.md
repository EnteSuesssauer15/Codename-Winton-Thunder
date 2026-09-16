![Logo](src/assets/white-keepup-logo.svg)

# KeepUp

KeepUp ist eine kleine Inventar-Anwendung. Mit ihr koennen Geraete gespeichert,
angezeigt, gesucht und wieder geloescht werden. Die Oberflaeche wird mit
[Flet](https://flet.dev/) gebaut, die Daten werden in einer lokalen SQLite-Datei
gespeichert.

Diese README ist fuer Personen geschrieben, die das Projekt zum ersten Mal sehen.
Python- oder Flet-Vorkenntnisse sind nicht erforderlich.

## Was wird benoetigt?

- Python 3.10 oder neuer
- Git, falls das Projekt aus einem Git-Repository geladen wird
- Ein Terminal (unter Windows: PowerShell oder Eingabeaufforderung)
- Optional: Visual Studio Code zum Bearbeiten der Dateien

Die benoetigte Python-Version kann im Terminal geprueft werden:

```bash
python3 --version
```

Unter Windows heisst der Befehl meistens:

```powershell
python --version
```

## Installation

1. Öffne ein Terminal im Hauptordner des Projekts. Das ist der Ordner, in dem
	`README.md` und `dev_setup.py` liegen.
2. Fuehre das Einrichtungs-Skript aus:

	```bash
	python3 dev_setup.py
	```

	Unter Windows:

	```powershell
	python dev_setup.py
	```

Das Skript erstellt den Ordner `.venv` und installiert dort die benoetigten
Pakete. `.venv` ist eine virtuelle Umgebung: Die Pakete dieses Projekts bleiben
dadurch von anderen Python-Projekten getrennt.

### Virtuelle Umgebung aktivieren

Linux und macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Wenn die Umgebung aktiviert ist, erscheint oft `(.venv)` am Anfang der
Terminalzeile.

## Anwendung starten

Die Befehle muessen im Hauptordner des Projekts ausgefuehrt werden.

Als Desktop-Anwendung:

```bash
flet run
```

Als Web-Anwendung im Browser:

```bash
flet run --web
```

Beim ersten Start wird automatisch die Datei `database.db` angelegt. Sie
enthaelt die Inventardaten und liegt im Hauptordner. Die Datei wird nicht von
Hand erstellt und sollte nicht in Git eingecheckt werden.

## Die Anwendung benutzen

- **Home** zeigt das Dashboard. Es ist derzeit eine einfache Startseite.
- **Table** zeigt alle Eintraege im Inventar.
- Mit dem **Plus-Symbol** kann ein Geraet angelegt werden. Alle drei Felder
  muessen ausgefuellt sein: Device, Type und Location.
- Das **Suchfeld** filtert die Inventartabelle.
- Ein oder mehrere Eintraege koennen markiert und ueber **delete selected**
  geloescht werden.
- **Settings** oeffnet die Einstellungsseite. Das Speichern von Einstellungen
  ist derzeit nur vorbereitet.

## Wo liegt welcher Code?

```text
.
├── README.md              Diese Anleitung
├── dev_setup.py           Erstellt .venv und installiert Pakete
├── pyproject.toml         Projektname, Abhaengigkeiten und Flet-Konfiguration
├── requirements.txt       Benoetigte Python-Pakete
├── src/
│   ├── main.py            Startpunkt und Navigation der Anwendung
│   ├── scripts/
│   │   └── database.py    Zugriff auf die SQLite-Datenbank
│   ├── views/
│   │   ├── dashboard.py   Dashboard-Seite
│   │   ├── settings.py    Einstellungsseite
│   │   └── table.py       Inventartabelle, Suche und Loeschen
│   └── assets/            Bilder und Logos
└── tests/                 Automatisierte Tests
```

### Wie fliesst eine Aktion durch das Programm?

1. `flet run` verwendet wegen der Einstellung in `pyproject.toml` den Ordner
	`src` und startet `main.py`.
2. `main.py` erstellt einen `DatabaseManager` und prueft, ob `database.db`
	existiert.
3. Fehlt die Datei, erstellt `database.py` die Tabellen `inventory` und
	`settings`.
4. `table.py` liest die Daten aus `inventory` und baut daraus die sichtbare
	Tabelle.
5. Beim Speichern eines Geraets ruft die Tabelle `device_create(...)` auf. Die
	Datenbank speichert den neuen Eintrag dauerhaft.

## Eine kleine Aenderung machen

Fuer eine Aenderung an der Inventartabelle ist meistens
`src/views/table.py` die richtige Datei. Fuer die Navigation oder das Layout
des Hauptfensters ist `src/main.py` zustaendig. Neue Datenbankfunktionen gehoeren
nach `src/scripts/database.py`.

Nach einer Aenderung:

1. Anwendung beenden und mit `flet run` neu starten.
2. Die betroffene Funktion in der Oberflaeche ausprobieren.
3. Tests ausfuehren:

	```bash
	pytest
	```

	Alternativ kann Flet-Tests mit folgendem Befehl starten:

	```bash
	flet test
	```

## Datenbank zuruecksetzen

Wenn du fuer einen frischen Test alle Inventardaten loeschen moechtest, beende
die Anwendung und entferne `database.db`. Beim naechsten Start wird die Datei
mit leeren Tabellen neu erstellt.

Linux und macOS:

```bash
rm database.db
```

Windows PowerShell:

```powershell
Remove-Item database.db
```

## App bauen

Die folgenden Befehle erzeugen ein Paket fuer die jeweilige Plattform. Fuer
mobile Plattformen koennen zusaetzliche SDKs und Signatur-Schluessel notwendig
sein.

```bash
flet build apk -v      # Android
flet build ipa -v      # iOS
flet build macos -v    # macOS
flet build linux -v    # Linux
flet build windows -v  # Windows
flet build web -v      # Web
```

Weitere Informationen stehen in der [Flet-Dokumentation](https://flet.dev/docs/).

## UI-Entwurf

Der aktuelle UI-Entwurf ist in [Excalidraw](https://excalidraw.com/#room=076266f0ae80d05fa866,UH7-gWjAp0Z2MI0mYbicHw)
zu finden.
