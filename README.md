![Logo](src/assets/white-keepup-logo.svg)

# KeepIt

KeepIt ist eine kleine Inventar-Anwendung. Mit ihr können Geräte gespeichert,
angezeigt, gesucht und wieder gelöscht werden. Die Oberfläche wird mit
[Flet](https://flet.dev/) gebaut, die Daten werden in einer lokalen SQLite-Datei
gespeichert.

## Was wird benötigt?

- Python 3.10 oder neuer

## Installation

1. Öffne ein Terminal im Hauptordner des Projekts. Das ist der Ordner, in dem
	`README.md` und `dev_setup.py` liegen.
2. Führe das Einrichtungs-Skript aus:

	```bash
	python3 dev_setup.py
	```

	Unter Windows:

	```powershell
	python dev_setup.py
	```

Das Skript erstellt den Ordner `.venv` und installiert dort die benötigten
Pakete. 
`.venv` ist eine virtuelle Umgebung: Die Pakete dieses Projekts bleiben
dadurch von anderen Python-Projekten getrennt.

### Virtuelle Umgebung aktivieren

In den meisten fällen sollte die Umgebung automatisch aktiviert sein.
Erkennbar ist das an dem (.venv) am anfang der Befehlszeile.

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

Die Befehle müssen im Hauptordner des Projekts ausgeführt werden.

Als Desktop-Anwendung:

```bash
flet run
```

Als Web-Anwendung im Browser:

```bash
flet run --web
```

Beim ersten Start wird automatisch die Datei `database.db` angelegt. Sie
enthält die Inventardaten und liegt im Hauptordner.

## Die Anwendung benutzen

- **Home** zeigt das Dashboard. Es ist derzeit eine einfache Startseite.
- **Table** zeigt alle Einträge im Inventar.
- Mit dem **Plus-Symbol** kann ein Gerät angelegt werden. Alle drei Felder
  müssen ausgefüllt sein: Device, Type und Location.
- Das **Suchfeld** filtert die Inventartabelle.
- Ein oder mehrere Einträge können markiert und über **delete selected**
  gelöscht werden.
- **Settings** öffnet die Einstellungsseite. Das Speichern von Einstellungen
  ist derzeit nur vorbereitet.

## Wo liegt welcher Code?

```text
.
├── README.md              Diese Anleitung
├── dev_setup.py           Erstellt .venv und installiert Pakete
├── pyproject.toml         Projektname, Abhängigkeiten und Flet-Konfiguration
├── requirements.txt       Benötigte Python-Pakete
├── src/
│   ├── main.py            Startpunkt und Navigation der Anwendung
│   ├── scripts/
│   │   └── database.py    Zugriff auf die SQLite-Datenbank
│   ├── views/
│   │   ├── dashboard.py   Dashboard-Seite
│   │   ├── settings.py    Einstellungsseite
│   │   └── table.py       Inventartabelle, Suche und Löschen
│   └── assets/            Bilder und Logos
└── tests/                 Automatisierte Tests
```

### Wie fliesst eine Aktion durch das Programm?

1. `flet run` verwendet wegen der Einstellung in `pyproject.toml` den Ordner
	`src` und startet `main.py`.
2. `main.py` erstellt einen `DatabaseManager` und prüft, ob `database.db`
	existiert.
3. Fehlt die Datei, erstellt `database.py` die Tabellen `devicetypes`, `inventory` und
	`settings`.
4. `table.py` liest die Daten aus `inventory` und baut daraus die sichtbare
	Tabelle.
5. Beim Speichern eines Geräts ruft die Tabelle `device_create(...)` auf. Die
	Datenbank speichert den neuen Eintrag dauerhaft.

## Eine kleine Aenderung machen

Für eine Änderung an der Inventartabelle ist meistens
`src/views/table.py` die richtige Datei. Für die Navigation oder das Layout
des Hauptfensters ist `src/main.py` zuständig. Neue Datenbankfunktionen gehören
nach `src/scripts/database.py`.

Nach einer Änderung:

1. Anwendung beenden und mit `flet run` neu starten.
2. Die betroffene Funktion in der Oberfläche ausprobieren.
3. Tests ausführen:

	```bash
	pytest
	```

	Alternativ kann Flet-Tests mit folgendem Befehl starten:

	```bash
	flet test
	```

## Datenbank zurücksetzen

Wenn du für einen frischen Test alle Inventardaten löschen möchtest, beende
die Anwendung und entferne `database.db`. Beim nächsten Start wird die Datei
mit leeren Tabellen neu erstellt.

Linux und macOS:

```bash
rm .flet/storage/data/database.db
```

Windows PowerShell:

```powershell
Remove-Item .flet\storage\data\database.db
```

## App bauen

Die folgenden Befehle erzeugen ein Paket für die jeweilige Plattform. Für
mobile Plattformen können zusätzliche SDKs und Signatur-Schlüssel notwendig
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

## Anforderungen

[Excalidraw](https://excalidraw.com/#json=XEy9W-YD03nUIpjvDkBY7,yv5Lv6JnRmQZxdDQ-oAcMw)

## UI-Entwurf

[Excalidraw](https://excalidraw.com/#room=076266f0ae80d05fa866,UH7-gWjAp0Z2MI0mYbicHw)

## ER Diagramm

[Excalidraw](https://excalidraw.com/#json=DnFHi2AWA6FnGXiiEVL2p,ao85zTtm19U3zLYcwQSQGQ)

## Programm Ablauf

[Excalidraw](https://excalidraw.com/#json=FJyzCcZHyuCK4zTrdpnlJ,PhK3vY6ElGv_O3ld0joidg)
