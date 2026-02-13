# monopoly-analysis
Analyzing Probabilities, ROIs and Break Evens

### Algorithmus Übergangswahrscheinlichkeiten
#### Schritt 1: Ausgangszustand festlegen
Wir haben einen Spieler im Zustand (Feld X, Pasch-Zähler P, Frei).
#### Schritt 2: Alle Würfelergebnisse durchgehen
Für jede Würfelsumme s (2 bis 12) und jeden Wurf-Typ (Pasch / Kein Pasch):
#### Schritt 3: Zielfeld berechnen
Zielfeld Y = (X+s) mod 40
#### Schritt 4: Zielzustand bestimmen
Fall A: Zielfeld ist Feld 30 (Gehe ins Gefängnis)
→ Zielzustand = (10, Eingesperrt, R1)

Fall B: Dritter Pasch (Ausgangszustand hat P=2 und Wurf ist Pasch)
→ Zielzustand = (10, Eingesperrt, R1)

Fall C: Zielfeld ist Ereignisfeld (7, 22, 36) 
→ Aufspaltung nach Kartenwahrscheinlichkeiten

Fall D: Zielfeld ist Gemeinschaftsfeld (2, 17, 33)
→ Aufspaltung nach Kartenwahrscheinlichkeiten:

Fall E: Normales Feld
→ Zielzustand basiert nur auf Pasch:

#### Schritt 5: Wahrscheinlichkeiten addieren
Wenn mehrere Pfade zum selben Zielzustand führen, werden die Wahrscheinlichkeiten addiert.