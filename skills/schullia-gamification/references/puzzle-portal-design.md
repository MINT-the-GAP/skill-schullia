# Puzzle- und Portalvertrag

## Geltung und Textgrenze

Diese Referenz gilt nur innerhalb der Gamificationphase. Der vorhandene
Kurstext und die relative Reihenfolge der vorhandenen Aufgaben bleiben
unverändert. Makros dürfen zwischen sichere bestehende Blöcke gesetzt oder um
vollständige Blöcke gelegt werden; sie rechtfertigen keine neuen Erzähl-,
Immersions-, Szenen-, Übergangs-, Belohnungs-, Fortschritts-, Motivations- oder
Questtexte und keine dekorativen Überschriften.

Neue lernendenseitige Prosa ist ausschließlich zulässig als:

1. knapper funktionaler Hinweis zu Fundort, Rekonstruktion oder Kombination
   eines konkreten Puzzletors;
2. knapper funktionaler Hinweis zum Auffinden einer konkreten Geheimfolie,
   einschließlich ihres minimalen normalisiert eindeutigen Titels.

Die Regel gilt auch für unsichtbare Texte, Tooltip-ähnliche Beschriftungen und
Portalfolien. Schlüssel-, Werkzeug-, Ressourcen- und Portalwege werden allein
durch Makros, Positionen und Zustände verständlich. Für jede neue Textzeile
werden Typ, Zieltor beziehungsweise Ziel-Geheimfolie, Fundort und Notwendigkeit
protokolliert. Außerhalb der beiden Typen beträgt das Textdelta null.

## Puzzletorkatalog

Für jedes Tor wird vor dem Schreiben ein Datensatz angelegt:

```text
Farbe
N und Matrixform Zeilen × Spalten
Permutation 1…N
Navigationstor oder anker-Inhaltstor
Quellposition des Tors
je Teil: Nummer, Quellposition, Fundform und vollständige Verbergungskette
je Hinweis: Position, Sichtbarkeit, Voraussetzung und erlaubter Texttyp
Decodierregel, Eingabewerte und daraus berechnete eindeutige Permutation
Portal-/Werkzeug-/Umweltpräfixe
geordnete Witness-Schritte
```

Harte Invarianten:

- `N` liegt zwischen 1 und 16 und darf von Tor zu Tor sowie von Kurs zu Kurs
  variieren. Es gibt keinen festen Viererstandard.
- Die rechteckige Matrix besitzt genau `N` Zellen und enthält jede ganze Zahl
  von `1` bis `N` genau einmal. Jede Faktorzerlegung von `N` ist als
  Matrixform möglich; auch `1×N` und `N×1` sind zulässig.
- Pro kanonischer Farbe gibt es höchstens ein Tor.
- Für jede Matrixzahl existiert genau ein gleichfarbiges Puzzleteil. Duplikate,
  Lücken, verwaiste Teile und Teile nach dem eigenen Tor sind ungültig.
- Alle Voraussetzungen jedes Pflichtteils und jeder Decodierinformation sind
  im Vor-Tor-Graphen erreichbar.
- Das Puzzletor steht nie innerhalb von `@lootif`, `@Erdhaufen`, `@Pflanze`
  oder deren Inlinepayload. Es gibt kein Endmakro für ein Tor.
- Ein Tor ohne `anker` sperrt alle späteren Folien auch gegen ToC, direkten
  Hash, Browserhistorie und Portal. Ein Tor mit `anker` sperrt lokalen Inhalt
  bis zur nächsten Markdown-H1, nicht bis zur nächsten H2.
- Eine andere Farbe, Zahl oder Matrix allein ist keine strukturelle Variation.

## Vollständige Puzzleteil-Positionsmatrix

Ein Puzzleteil besitzt kein Oberflächenziel. Es kann deshalb nie direkt an
`toc`, `menu`, `classroom`, `info`, `translator`, `mode` oder ein
Fremdtemplate-Ziel gebunden werden. Ein Fund neben einer Oberfläche oder auf
derselben Folie bleibt ein normaler Fund und wird nicht als Oberflächenfund
ausgegeben.

Technisch belegte oder durch die allgemeinen Containerverträge gedeckte Formen:

| Position oder Form | Status | Bedingung |
|---|---|---|
| eigenständige Makrozeile an sicherer Blockgrenze | erlaubt | vor eigenem Tor |
| inline zwischen unverändertem vorhandenem Inhalt | erlaubt | keine LiaScript-, Quiz- oder HTML-Syntax beschädigen; keine neue Begleitprosa |
| mehrere Teile auf derselben sicheren Zeile | erlaubt | Makroargumente bleiben balanciert und jedes Teil ist einzeln sammelbar |
| Start-/Werkzeugfolie | erlaubt | Pflichtwerkzeug und Lupe jeweils vor ihrer ersten benötigten Aktion |
| Anfang oder Ende einer H2-Aufgabenfolie | erlaubt | außerhalb der nativen Quizsyntax und vor eigenem Tor |
| direkt nach einer Aufgabe oder im vorhandenen Lösungsschwanz | erlaubt | Lösung, Hinweise und Feedback wortgleich lassen |
| neben einem vollständigen lokalen Fremdtemplate-Block | erlaubt | kein erfundenes Ziel und keine Einfügung in dessen interne Ausgabe |
| innerhalb eines vollständig von außen umschlossenen lokalen Blocks | bedingt | Bereichsgrenzen bleiben auf derselben Folie und LIFO |
| in einem Erd-/Pflanzenblock | erlaubt | Werkzeuge vorher erreichbar; das Teil bleibt vor seinem Tor |
| Payload von `@Erdhaufen.inline` oder `@Pflanze.inline` | erlaubt | einzeilig, Klammern balanciert, Werkzeuge vorher erreichbar |
| direkte Optionen `erde`/`pflanze` | erlaubt | beliebig viele, links nach rechts außen→innen; jede Schicht hat Werkzeugpräfix |
| direkte verborgene Schichten | erlaubt | `erde-unsichtbar`, `erde-zauberstaub`, `pflanze-unsichtbar` oder `pflanze-zauberstaub`; Lupe vor Scanbedarf |
| Fundoption `unsichtbar` oder `zauberstaub` | erlaubt | höchstens eine Itemverbergung; sie ist die letzte Stufe |
| `@Unsichtbar(@Puzzleteil(...))` oder `@Zauberstaub(...)` | erlaubt | vollständiger einzeiliger Payload; Lupe und bestimmbarer Scanort vorher |
| `@lootif(...; spawn)` | erlaubt | gültiger Bereich; Trigger außerhalb des eigenen noch verborgenen Bereichs erreichbar |
| erreichbarer Portalzweig | erlaubt | Ziel vor dem Tor; Rückweg oder Merge; kein Tor-Bypass |
| Geheimfolie | bedingt | ausdrücklich konfigurierte Folie und erlaubter Such-/Portalzugang vor dem Tor |
| Garten vor vorhandener Reflexion | erlaubt | kein zusätzlicher Garten- oder Immersionstext |
| vorhandene Selbsteinschätzung | bedingt | optionaler Fund stört die fachliche Struktur nicht |
| Abgabe-/Freeze-Bereich | bedingt | Teil liegt vor eigenem Tor und vor dem Abschlusszustand; vollständiger Witness |
| globale oder fremde Oberfläche als direktes Ziel | nicht unterstützt | `@Puzzleteil` besitzt kein Zielargument |
| nach dem eigenen Tor oder in dessen gesperrtem Nachbereich | ungültig | auch ein scheinbarer Portalweg repariert das Präfix nicht |

Gemeinsame Fundoptionen dürfen kombiniert werden: `anker`, höchstens eine
Dauer, Theme-/Farbmodus-/Annotationsbedingungen, höchstens eine
Itemverbergung und beliebig viele geordnete direkte Erd-/Pflanzenschichten.
Jede zusätzliche Bedingung wird als eigene Kante im Witness expandiert.

## Kombinationshinweise

Die Teile zeigen ihre Nummer nach dem Sammeln im Inventar. Die Rätsellogik
bestimmt deshalb die Slotanordnung; sie darf nicht davon ausgehen, dass die
Identität eines gesammelten Teils dauerhaft geheim bleibt.

Eine gültige Decodierung ist:

- aus sämtlichen benötigten Informationen vor dem Tor berechenbar;
- deterministisch und für die konkrete Matrix eindeutig;
- ohne externe Sachkenntnis, Zufallsraten, Reload, Browser-Zurück,
  Quelltexteinsicht oder neuen Tab lösbar;
- mit korrekten Aufgabenlösungen vereinbar und ohne erzwungene Fehlantwort;
- frei von ungeklärten Gleichständen, Rundungen und mehrdeutigen
  Reihenfolgen;
- nicht ausschließlich in einem kostenpflichtigen nativen Hinweis versteckt,
  wenn ein abzugsloser perfekter Highscore versprochen wird.

Zulässige Quellen sind unveränderte vorhandene Teilaufgabenergebnisse,
Antwortpositionen, Tabellen- oder Diagrammwerte, markierte Wörter, vorhandene
Materiallabels und verteilte Hinweisfragmente. Verändere keine Aufgabe, um
passende Ziffern zu erzeugen.

Beispiel einer knappen zulässigen Regel:

> Nimm in Aufgabenreihenfolge jeweils die erste Ziffer der
> Teilaufgabenergebnisse.

Diese Regel ist nur gültig, wenn das Ergebnis tatsächlich eine Permutation
`1…N` ergibt. Robuster ist eine Rangregel, etwa die Teilaufgaben nach ihrer
ersten Ergebnisziffer und bei Gleichstand nach vorhandener Teilaufgabenkennung
zu ordnen; die geordneten Teilaufgabenindizes bilden dann die Permutation.

Mögliche Verteilung:

- ein sichtbarer knapper Metahinweis an einer sicheren bestehenden Stelle;
- ein mit `@Unsichtbar` oder `@Zauberstaub` verdeckter Hinweis;
- ein Hinweis in einer erreichbaren Erd-/Pflanzenfreigabe;
- ein monoton erscheinender Hinweis in `@lootif(...; spawn)`;
- ein Hinweis auf einer Portalroute oder ausdrücklich geplanten Geheimfolie;
- mehrere Fragmente an unterschiedlichen Vor-Tor-Positionen.

Verteilte Fragmente benötigen eine erreichbare Regel, wie viele Fragmente
existieren, in welcher Ordnung sie gelesen und wie sie zusammengesetzt werden.
Ein unsichtbarer Pflichthinweis benötigt zuvor die Lupe und einen konkreten
Puzzletorhinweis auf den Scanbereich; „suche überall“ ist kein Witness.

## Portal-, Schlüssel- und Navigationsgraph

Öffentliche Autorenmakros sind `@Portal`, `@Einwegportal` und
`@Einbahnportal`. `PortalZurueck` ist kein Autorenmakro. Inventarisiere pro
Portal:

```text
Quellfolie
positive 1-basierte Zielfolie
Modus
unmittelbar folgende Portalschlösser
vorher benötigte Schlüssel und Zustände
erreichbares Zielobjekt, insbesondere Schlüssel
Rückkante, Folgekante oder Merge
betroffene ToC-, Seitenwechsel- und Puzzletorgrenzen
```

Portalregeln:

- Das Ziel existiert, ist eine andere Folie und wird als Zahl, nicht als Titel,
  angegeben.
- `@Portal(n)` und `@Portal(n; hinundher)` erzeugen ein temporäres Rückportal.
  Es verschwindet, sobald die Zielfolie auf einem anderen Weg verlassen wird.
- `@Portal(n; einweg)`, `@Einwegportal(n)` und `@Einbahnportal(n)` erzeugen
  kein Rückportal. Sie ersetzen nur ihren Browser-History-Schritt; offene
  LiaScript-Pfeile oder ein offenes ToC bleiben Auswege.
- `@Schloss(portal, farbe)` steht unmittelbar nach dem betroffenen
  Autorenportal und sperrt das letzte davor stehende Portal derselben Folie.
  Ein automatisch erzeugtes Rückportal wird nicht gesperrt.
- `seitenwechsel` sperrt Buttons, Pfeile, Tastatur und Swipe/Drag, aber weder
  ToC noch Portale. Ein wirklich portalgeführter Pfad muss deshalb jede andere
  sichtbare Kante – insbesondere ToC – separat schließen oder im Graphen
  ausschließen.
- Globale ToC- und `seitenwechsel`-Schlösser wirken ab Kursstart. Wenn beide
  aktiv sind, führt bereits vom Startzustand mindestens ein ungesperrtes Portal
  zu einem Schlüssel oder Reparaturpfad.
- Ein Portal darf zu einem Schlüssel führen. Der Schlüssel liegt dort als
  normaler Inlinefund oder an einer der sechs nativen LiaScript-Oberflächen;
  Schlüssel besitzen keine Fremdtemplate-Ziele.
- Der Schlüssel für ein Portalschloss ist vor diesem Portal erreichbar und
  liegt weder hinter dem eigenen Schloss noch in einer von ihm selbst
  gesperrten Oberfläche. Dieselbe Farbe an mehreren Schlössern benötigt je
  Schloss einen eigenen Schlüssel.
- Vor einem Einwegübergang werden alle nur am Ursprung erreichbaren
  Pflichtobjekte gesammelt. Das Ziel besitzt eine erreichbare Folgekante oder
  verschmilzt mit dem Hauptpfad.
- Ein Navigationstor blockiert jede Portalquerung in seinen Nachbereich. Teile
  und Hinweise für dieses Tor liegen deshalb im Vor-Tor-Portalgraphen.
- Portale und Portalschlüssel erhalten keine neue Begleit- oder
  Übergangsprosa.

Technisch brauchbare Muster sind ein Zweiweg-Hub mit Schlüsselrücktransport,
eine folienlokale Umleitung mit `seitenwechsel; anker` und ein Einwegpfad, bei
dem jeder Schlüssel vor dem nächsten Portalschloss liegt und die letzte Kante
mit dem Hauptpfad verschmilzt. Diese Muster sind keine Vorlage: Topologie,
Schlüsselverteilung, Puzzlebezug und Rückweg werden zwischen Kursen variiert.

## Witness-Prüfung

Der 100%-Witness protokolliert mindestens:

1. jedes Teil mit vollständigem Werkzeug-, Sichtbarkeits-, Umwelt-, Spawn- und
   Portalpräfix;
2. alle Hinweisquellen und die konkrete Berechnung der eindeutigen Permutation;
3. das Sammeln sämtlicher Teile vor dem eigenen Tor;
4. jede Portalkante mit Quelle, Ziel, Modus und Schlosszustand;
5. bei Zweiwegportalen die Rückkehr vor Verlust des temporären Rückportals;
6. bei Einwegportalen den Folgeweg oder Merge;
7. die Erreichbarkeit jedes Portalschlüssels vor seinem Schloss;
8. den Startschnitt bei global gesperrtem ToC oder `seitenwechsel`;
9. dass kein Portal ein geschlossenes Navigationstor umgeht;
10. Textdelta null außerhalb der katalogisierten Puzzle- und
    Geheimfolienhinweise.

Die logische Eindeutigkeit eines fachlichen Hinweises bleibt eine manuelle
Prüfung. Der Mapper kann Positionen, Makros und Teile der Abhängigkeiten
inventarisieren, aber keine semantische Eindeutigkeit behaupten.
