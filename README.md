![Logo](src/assets/white-keepup-logo.svg)

# KeepIt

KeepIt ist eine kleine Inventar-Anwendung. Mit ihr können Geräte gespeichert,
angezeigt, gesucht und wieder gelöscht werden. Die Oberfläche wird mit
[Flet](https://flet.dev/) gebaut, die Daten werden in einer lokalen SQLite-Datei
gespeichert.

## Was wird benötigt?

- Python 3.10 oder neuer
- flet==0.86.5
- flet-datatable2==0.86.5
- pysqlite3==0.6.0

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

## Die Anwendung benutzen

- Beim ersten Start ist die Datenbank völlig leer, ausgenommen von 3 Beispieltypen.
---
- Um Geräte anlegen zu können, muss zuerst einen Mitarbeiter und ein Typ definiert werden.
- Der Mitarbeiter wird in der `Employees` Ansicht erstellt.
- Dort sowie auf den folgenden Ansichten befindet sich oben rechts ein Knopf mit dem sich ein Popup öffnet, in dem Der Name, Nachname und die Abteilung gefragt wird.
- Drückt man dann auf Speichern hat man seinen ersten Mitarbeiter im System.
---
- Als nächstes wird ein Typ in der `Types` Ansicht erstellt.
- Typen agieren als eine art Kategorie, hierzu legt man den Kategorienamen fest und auch den Prefix der später in der Inventarnummer stehen wird.
- Auch hier sieht man nach dem speichern seinen ersten Typ in der Tabelle.
---
- Nun wird das erste Gerät in der `Devices` Ansicht erstellt.
- Die Erstellung von Geräten ist Besonders einfach gestaltet. Zuerst wird nach der Gerätebezeichnung gefragt, Könnte Marke Modell oder auch Seriennummer enthalten - Freie entscheidung.
- Da gerade schon ein Mitarbeiter und ein Typ erstellt wurde, wird hier nur noch per Dropdown jeweiliges ausgewählt.
- Ist das Gerät gespeichert sieht man in der Tabelle die Inventarnummer, Marke Modell oder Seriennummer sowie den Typ, die Eindeutige ID eines Mitarbeiters als auch den Namen und Nachnamen.
---
- Wenn man jetzt in die Home Ansicht sich das Dashboard anschaut sieht man, dass alles was man gerade angelegt hat auch dort gezählt wird.

- Möchte man sein System extern Speichern als Backup beispielsweise kann man auf dem Zahnrad in der Seitenleiste die Einstellungsansicht öffnen.
- Dort werden Alle werte aus der Datenbank als Json exportiert und auch wieder importiert. 
- Beim Import werden sämtliche Daten die zu dem Zeitpunkt in der Datenbank stehen überschrieben, sodass die Daten aus der Json absolut sind.

- Außerdem hat man die Funktion die Einstellungen zu speichern, jedoch gibts keine einstellungen...man kann diese aber speichern in der Datenbank, da die logik implementiert ist.

## Wo liegt welcher Code?

```text
.
├── README.md              Diese Anleitung
├── dev_setup.py           Erstellt .venv und installiert Pakete
├── pyproject.toml         (Automatisch erstellt) Projektname, Abhängigkeiten und Flet-Konfiguration
├── requirements.txt       Benötigte Python-Pakete
├── src/
│   ├── main.py            Startpunkt und Navigation der Anwendung
│   ├── scripts/
│   │   └── database.py    Zugriff auf die SQLite-Datenbank
│   ├── views/
│   │   ├── dashboard.py   Dashboard-Seite
│   │   ├── devices.py     Geräte-Seite
|   |   ├── type.py        Gerätetypen-Seite
|   |   ├── employee.py    Mitarbeiter-Seite
│   │   ├── settings.py    Einstellungen-Seite
│   └── assets/            Bilder und Logos
└── tests/                 (Automatisch erstellt) Automatisierte Tests
```

### Wie fließt eine Aktion durch das Programm?

1. `flet run` verwendet wegen der Einstellung in `pyproject.toml` den Ordner
	`src` und startet `main.py`.
2. `main.py` erstellt den `DatabaseManager` aus `scripts/database.py` und prüft, ob `database.db`
	existiert.
3. Fehlt die Datei, erstellt `database.py` die Tabellen `inventory`, `types`, `employees` und
	`settings`.
4. `devices.py` liest die Daten aus `inventory` und baut daraus die sichtbare
	Tabelle. Selbes vorgehen ist auch bei `type.py` und `employee.py` aus den
	Tabellen `devicetypes` und `employees`.
5. Beim erstellen eines `Typen`, `Employee` oder `Device` wird jeweils ihre eigene Funktion verwendet.
	Jede Funktion führt jeweils einen SQL Befehl auf die dementsprechende Tabelle aus mit mitgegebenen werten aus variablen.

## Eine kleine Änderung machen

Für eine Änderung an der Anwendung ist es übersichtlich gestaltet.

Beispielsweise ist man unzufrieden wie Geräte dargestellt werden, ändert man den code in der `devices.py`.

Nach einer Änderung:

Anwendung beenden und mit `flet run` neu starten.


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

## Verwendung von KI

KI wurde meist als hilfestellung für syntax verwendet, sprich copilot autocomplete oder beispiele gegeben wie sowas programmiert wird es aber selbst implementiert.
Ebenfalls wurden teilweise kommentare von KI geschrieben.

In der `dashboard.py` und `settings.py` wurde fast ausschließlich von KI geschrieben und selbst kommentiert, sodass es verständlicher wird.

## Anforderungen

[Excalidraw](https://excalidraw.com/#room=8af59903bd29f5051c35,2fg6w04Sic9SkeJsk8R1cA)

## UI-Entwurf

[Excalidraw](https://excalidraw.com/#room=076266f0ae80d05fa866,UH7-gWjAp0Z2MI0mYbicHw)

## ER Diagramm

[Excalidraw](https://excalidraw.com/#room=0e5fddbb5bf03e019d6b,Rz1cnnvJuAKWnrCQ02-RFA)

## Programm Ablauf
Nicht aktuell
[Excalidraw](https://excalidraw.com/#room=72d51e287efb5137f5da,1CbI4XAkwgdmZ-BM5AprtQ)
