import flet.testing as ftt


async def test_increment(flet_app: ftt.FletTestApp):
    """Prueft den mit Flet gelieferten Beispieltest.

    `flet_app` wird vom Flet-Pytest-Plugin bereitgestellt. Der Test ist aktuell
    noch ein Platzhalter aus dem Flet-Projektgeruest und prueft noch keinen
    KeepUp-Inventarworkflow.
    """
    tester = flet_app.tester

    await tester.pump_and_settle()

    # Warten, bis die erste Darstellung der App abgeschlossen ist.
    # Ausgangszustand des Beispielzaehlers.
    assert (await tester.find_by_text("0")).count == 1

    # Den Plus-Button ueber seinen Key anklicken und die UI aktualisieren.
    await tester.tap(await tester.find_by_key("increment"))
    await tester.pump_and_settle()

    # Danach soll der Zaehler den Wert 1 anzeigen.
    assert (await tester.find_by_text("1")).count == 1
