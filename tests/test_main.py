import flet.testing as ftt


async def test_increment(flet_app: ftt.FletTestApp):
    """Prüft den mit Flet gelieferten Beispieltest.

    `flet_app` wird vom Flet-Pytest-Plugin bereitgestellt. Der Test ist aktuell
    noch ein Platzhalter aus dem Flet-Projektgerüst und prüft noch keinen
    KeepUp-Inventarworkflow.
    """
    tester = flet_app.tester

    await tester.pump_and_settle()

    # Warten, bis die erste Darstellung der App abgeschlossen ist.
    # Ausgangszustand des Beispielzählers.
    assert (await tester.find_by_text("0")).count == 1

    # Den Plus-Button über seinen Key anklicken und die UI aktualisieren.
    await tester.tap(await tester.find_by_key("increment"))
    await tester.pump_and_settle()

    # Danach soll der Zähler den Wert 1 anzeigen.
    assert (await tester.find_by_text("1")).count == 1
