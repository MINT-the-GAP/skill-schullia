# Wochenaufgaben als Standard für Platzierung, Abwechslung und Spielfluss

## Qualitätsmaßstab

Der Nutzer hat die gamifizierten Wochenaufgaben ausdrücklich als akzeptablen
Standard benannt. Orientiere deshalb neue Entwürfe an ihren konkreten
Platzierungen, Fundfolgen, Spielphasen und Ressourcenmodellen. Eine erkennbare
Familienähnlichkeit ist erwünscht. Weder maximale Neuheit noch möglichst wenig
Gamification ist das Auswahlziel. Wiederkehrende Grundmuster, auch der Garten,
dürfen als Bausteine erhalten bleiben. Variiere ihre passende Kombination und
Einbettung in die tatsächlichen Aufgaben des Zielkurses.

Diese Einstufung ist eine Qualitätsvorgabe des Nutzers, keine Behauptung über
Fehlerfreiheit oder empirisch nachgewiesene Lernwirkung. Technische Sackgassen,
unpassende Importziele oder falsch gebundene Portale werden nicht übernommen.
Klärungsgate, eingefrorener Fachtext, unveränderte relative Aufgabenreihenfolge
und vollständiger Witness des Hauptskills gelten weiter. Vorhandene Prosa oder
Gartenüberschriften in den Beispielen erlauben keine neuen entsprechenden Texte.

## Provenienz und vollständiger Bestand

Geprüfter Snapshot: `MINT-the-GAP/Wochenaufgabe`, Commit
`3184ab1978075679b6f1ae060474541fbfd1554d`.
Der lokale Quellordner ist
`corpus/sources/ghrepo-mint-the-gap-wochenaufgabe-66366d21e5/` relativ zum
Repository-Stamm. `manifest.jsonl` belegt Pfad, Revision und gespeicherte Datei;
die Originale liegen unter `files/`.

Die Prüfung umfasst **41 ausgefüllte gamifizierte Kurse**:

- 36 Wochenfolgen 01–09 für Deutsch und Mathematik der Klassen 5 und 6;
- zwei Wochenfolgen 01–02 für Mathematik der Klasse 9;
- drei Einstiegskurse: `5/Deutsch/Lia5_00.md`,
  `5/Mathematik/Lia5_00.md` und `5/Lia5_SK.md` für Sachunterricht.

Die neueren Folgen **05–09 der Klassen 5/6 bilden eine Teilgruppe von genau
20 Kursen**. Halte diese Gruppe bei Vergleichen getrennt von den übrigen 21:
Sie belegt vor allem verteilte Werkzeuge, gestufte Geheimfolienzugänge und
aufgabenbezogene Puzzle. Die ältere Gartenfamilie und die großflächigen
Aufgabenfreigaben der Klasse 9 erweitern die Auswahl. Die ungefähre Nutzerzahl
„rund 20“ ist keine technische Obergrenze und kein Dateinamensfilter.

Nicht als Standardkurse zählen `5/Deutsch/Lia5_41.md` (Import-/Abgabehülle),
`5/Mathematik/Lia5_10.md` (Aufgabenplatzhalter), `ABs/Spezi/MO.md` (Loot-Import,
aber keine aktive Loot-Gamification) sowie Tests, Vortrag und Makrodemonstrationen
unter `Alt/`. Ein Import allein genügt nicht. Inventarisiere bei Aktualisierungen
alle Fach- und Klassenpfade, auch neue oder unnummerierte Kursnamen; filtere nicht
fest auf Klassen 5/6 oder auf die Folgen 01–03.

Der [versionierte Standardbestand](accepted-weekly-courses.json) hält die
geprüften Dateihashes, Vergleichsgruppen, Abschnittsanker und kompakten Profile
fest. Die vollständigen Ereignisprofile werden bei Bedarf aus den Originalen
erzeugt; lade den Gesamtexport nicht pauschal in den Modellkontext. Der
Akzeptanzeintrag hält auch die Auslegung des ungefähren Nutzerumfangs fest.

Das Inventar und die Profile lassen sich vom Repository-Stamm aus read-only
reproduzieren. Der Sachunterrichtseinstieg wird ausdrücklich eingeschlossen:

```text
python skills/schullia-gamification/scripts/profile_weekly_courses.py --include-course 5/Lia5_SK.md
python skills/schullia-gamification/scripts/profile_weekly_courses.py --include-course 5/Lia5_SK.md --json
python skills/schullia-gamification/scripts/profile_weekly_courses.py --check
```

Der Profilbericht hilft bei Mengen, Ankern und Reihenfolgen. Er ersetzt weder
das Lesen der gewählten Originalstellen noch den vollständigen Witness und
bewertet eine Platzierung nicht allein aufgrund ihrer technischen Möglichkeit.
Prüfe bei Parser-/Mapperdiagnosen die betroffenen Zuordnungen am Original.
Aus unvollständig erfassten Folien oder Fundfolgen darf keine Funddichte oder
Pacingvorgabe entstehen. Nach der korrigierten LLMQuiz-Zaunerkennung stimmen
die H1-/H2-Zahlen aller 41 Profile mit dem Originalinventar überein. Verbleibende
Meldungen betreffen ausschließlich `orphan_hint`; prüfe die Hinweiszuordnung
im gewählten Aufgabenabschnitt. Die Ankertabelle unten wurde unabhängig aus den
tatsächlichen Originalüberschriften erzeugt und mit den Kursphasen abgeglichen.

Es wurden die Originalausschnitte zu Start, Werkzeug-/Fundpositionen,
Freigaben, Spielphasen und Abschluss aller 41 Kurse gelesen. Die folgenden
Zeilen sind 1-basiert und gelten ausschließlich für diesen Commit. Öffne
Originale bei neuen Entscheidungen erneut gezielt. Gepinnte Weblinks entstehen
mit `https://github.com/MINT-the-GAP/Wochenaufgabe/blob/` + Commit + `/` + Pfad
und einem Zeilenanker. Beispielsweise:
[5 Deutsch 06, gestufter Geheimzweig](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/3184ab1978075679b6f1ae060474541fbfd1554d/5/Deutsch/Lia5_06.md#L575).

## Gemeinsamer Ablauf und unterschiedliche Ausgangsprofile

Die meisten Wochenkurse verbinden einen Startbereich, sechs fachliche
Aufgabenstationen, Selbsteinschätzung und eine eigene Abgabe. Klasse 9 hat
sieben Stationen; `5/Mathematik/Lia5_04.md` ebenfalls sieben. Der
Sachunterrichtseinstieg besitzt neun. Geheimfolien sind im Quelltext teils vor,
zwischen oder nach den Aufgaben und sogar nach der Abgabe angeordnet. Ihre
Lernendenreihenfolge muss deshalb aus Zugang, Freigaben und Rückwegen ermittelt
werden; die Quelltextposition allein beschreibt den Spielfluss nicht.

| Referenzgruppe | Beobachtete Grundform | Geeigneter Vergleich |
|---|---|---|
| Drei Einstiegskurse | Umfangreiche Einführung, Startbestand 50 Gold / 50 Diamanten / 150 Energie, UI-Funde, später Portal-/Schlüsselübungen | Einführung in Oberflächen und Mechaniken; nicht als universelle Startökonomie kopieren |
| Klassen 5/6, Folgen 01–02 | UI-Ressourcen und Schlüsselketten, Energiefunde im Lösungsschwanz, teils DynFlex-Freigaben | Aufgabennahe Belohnungen und verständliche UI-Ketten |
| Klassen 5/6, Folge 03 | Aufgabenpfad plus zusammenhängender Garten vor der Reflexion; 5 Deutsch zusätzlich Lupendepot | Wiederkehrende, eigenständige Spielphase |
| Klassen 5/6, Folge 04 | Geheimreserve, verteilte Puzzleteile, Tor in der Kursmitte oder vor dem Abschluss; 5 Mathematik bereits Werkzeuge in Aufgaben | Übergang von Sammelfunden zu gestuften Freigaben |
| Klassen 5/6, Folgen 05–09 | Werkzeuge in frühen Lösungen, später Schichtketten oder verteilte Namensfragmente, Geheimfolien mit Rückweg und teils Puzzle | Vorrangige Familie für Kombination von Platzierung, Abwechslung und Spielfluss in vergleichbaren Wochenkursen |
| Klasse 9, Folgen 01–02 | Früher Werkzeugzugang, geschichtete weitere Werkzeuge und UI-Funde, komplette Aufgabenblöcke unter Erde/Pflanze, Geheimfolie und Puzzle | Größere fachliche Träger und zusammenhängende Arbeitsphasen |

Alle 20 Kurse der Folgen 05–09 starten mit `@Ressourcen(0, 0, 50)` und
verwenden Achievements sowie `@Highscore(10000, 50, 100, 25, 100)`.
Die Klasse-9-Kurse starten mit 60 Energie und verwenden
`@Highscore(10000, 50, 100, 120, 100)` (jeweils Zeilen 34–36).
Das sind beobachtete Profile; übernimm sie nur nach Abgleich mit Aufgabenzahl,
Pflichtkosten, Fehlerreserve und bereits geklärten Nutzerwünschen.

## Belegte Platzierungs- und Ablauffamilien

### A. Startoberflächen und spätere Schlüssel bilden eine Rückkopplung

UI-Truhen und globale Schlösser werden häufig auf der Startfolie angelegt,
ihre Schlüssel kommen aus erreichbaren anderen Oberflächen oder aus Aufgaben.
Beispiel einer kurzen vollständigen Oberflächenfolge:
`6/Deutsch/Lia6_01.md`, Zeilen 49–61: ToC-Schlüssel → Menü mit nächstem
Schlüssel → Übersetzer mit nächstem Schlüssel → Info. In neueren Kursen ist
häufig zunächst nur ein Teil der Startoberflächen erschlossen:
`5/Mathematik/Lia5_08.md`, Zeilen 51–56, und
`6/Deutsch/Lia6_09.md`, Zeilen 46–54.

Übertragung: Wähle konkrete vorhandene Oberflächen und ordne spätere Funde
jeweils einer nutzbaren Freigabe zu. Nicht jeder Startfund muss sofort erreichbar
sein; der erste fachliche Arbeitsweg und die benötigten Werkzeuge müssen es
sein. Belege jeden Import und jede reale Zielinstanz gesondert. Ein weiterer
Schlüssel ist nur dann sinnvoll, wenn sein Ziel und die Rolle im Ablauf feststehen.

### B. Belohnungen und Werkzeuge liegen an abgeschlossenen Teilaufgaben

Ein häufiges Muster ist Aufgabenabsatz → Quiz → Sterntrenner → vorhandene
Musterlösung und Loot → Sterntrenner → `@ADetails`. Ein Werkzeug erscheint
also als Ergebnis einer bereits erledigten Teilaufgabe und ermöglicht später
weitere Funde. Es wird nicht automatisch vor die erste Aufgabe gelegt.

Konkrete Werkzeugfolgen aus den neueren Kursen:

| Kurs | Tatsächliche Fundfolge | Spätere Verwendung |
|---|---|---|
| `5/Deutsch/Lia5_06.md` | Lupe 245 → Schaufel 282 → Gießkanne 338, alle in Aufgabe 2 | Pflanze → Erde → unsichtbarer Geheimfolienname nach Aufgabe 4, 575–586 |
| `5/Deutsch/Lia5_07.md` | Gießkanne 117 → Schaufel 177 in Aufgabe 2 → Lupe 257 in Aufgabe 3 | Unsichtbare Erde → Pflanze nach Aufgabe 4, 478–489 |
| `6/Mathematik/Lia6_07.md` | Schaufel 188 in Aufgabe 1 → Gießkanne 368 in Aufgabe 2 → Lupe 618 in Aufgabe 3 | Geschichteter Geheimfolienname in der letzten Sachaufgabenlösung, 1400–1415 |
| `6/Deutsch/Lia6_08.md` | Schaufel 159 → Gießkanne 210 → Lupe 253, in Aufgaben 1, 2, 3 | Erde → Pflanze → unsichtbarer Name nach Aufgabe 5, 505–515 |

Die Abstände folgen fachlichen Teilaufgaben und Stationen, keinem festen
Zeilenraster. Mehrere Funde innerhalb einer Station sowie ein späterer Einsatz
nach mehreren Stationen sind belegt. Wähle passende abgeschlossene Einheiten
und prüfe deren tatsächliche Erreichbarkeit über das jeweilige Quiztemplate.
Energie und Werkzeug können gemeinsam belohnen; ein Werkzeug kann auch allein
stehen. Keine Pflicht, jede Lösung mit demselben Bündel zu füllen.

### C. Eine spätere Spielphase verwendet die zuvor gesammelten Werkzeuge

Die Varianten betreffen eine tatsächlich andere Aktionsfolge:

- Erde → Pflanze → Lupe am Geheimfoliennamen:
  `6/Deutsch/Lia6_05.md`, 396–406.
- Pflanze → Erde → Lupe am Namen:
  `5/Mathematik/Lia5_08.md`, 505–514.
- Lupe → unsichtbare Pflanze → Erde:
  `6/Deutsch/Lia6_06.md`, 709–722.
- Pflanze → Lupe → unsichtbare Erde:
  `5/Deutsch/Lia5_09.md`, 536–546.
- Ineinander verschachtelte Inline-Schichten im Lösungsschwanz:
  `6/Mathematik/Lia6_08.md`, 675 und 1159.

Jede Pflanzenaktion umfasst Gießen und anschließendes Anklicken der Blüte.
Der äußere Fundort muss bestimmbar sein; die zulässigen Hinweise beziehen sich
in diesen Beispielen auf den Zugang einer konkreten Geheimfolie. Eine andere
Schichtfolge zählt nur als passende Variation, wenn Werkzeugreihenfolge,
Auffindbarkeit und anschließender Nutzen dazu passen. Zusätzliche Schichten
brauchen eine Funktion im geplanten Ablauf; sie sind keine Pflichtsteigerung
von Woche zu Woche.

### D. Verteilte Namensfragmente verknüpfen mehrere Aufgabenstationen

`5/Mathematik/Lia5_06.md` verteilt den Zugang zum Formenlager über Hinweise
nach Aufgaben 2, 3 und 4; Erde steht bei 901–903, Pflanze bei 1096–1098.
`5/Deutsch/Lia5_08.md` setzt den Namen Blattversteck aus Funden nach Aufgaben
2, 3 und 6 zusammen (471–473, 869–871; Zusammenbau im vorhandenen Hinweis).
`5/Mathematik/Lia5_09.md` kombiniert einen geschichteten ersten Namensabschnitt
nach Aufgabe 2 mit dem zweiten in der Lösung zu 5f (504–510, 1118).

Dies liefert Abwechslung gegenüber einer vollständig an einem Ort geöffneten
Schichtkette. Lege im Plan die erste Begegnung, jeden späteren Fund und den
Zeitpunkt fest, ab dem der vollständige Name bekannt ist. Vermeide einen
Hinweis, der ohne erreichbare Werkzeuge oder Teile sofortiges Weitergehen
verspricht. Bereits vorhandene Hinweisprosa bleibt wortgleich; neue Prosa ist
nur als konkreter Geheimfolienhinweis zulässig.

### E. Puzzle schließen eine inhaltlich bestimmte Sammelphase ab

Die Beispiele belegen unterschiedliche Tororte und tatsächlich verschiedene
Kombinationsregeln:

- Tor zwischen Aufgaben: `6/Deutsch/Lia6_04.md`, 315–319; sowie
  `5/Deutsch/Lia5_05.md`, 848–852.
- Tor vor einem Geheimzugang: `6/Mathematik/Lia6_06.md`, 683–696.
- Tor auf einer Geheimfolie: `5/Deutsch/Lia5_08.md`, 895–917, mit einer
  Reihenfolge aus Mengen des Lesetexts; `6/Deutsch/Lia6_08.md`, 660–675,
  mit zeitlicher Reihenfolge des vorhandenen Lesetexts.
- Zwei verschieden früh lösbare Tore: `6/Deutsch/Lia6_06.md`, 709–719 und
  1011–1060; das erste nach Aufgabe 4, das zweite nach Aufgabe 6.
- Tor und Werkzeugfreigabe nach Aufgabe 2:
  `6/Mathematik/Lia6_09.md`, 564–568; erst dort folgt die Gießkanne.
- Tor am Abschluss: `6/Mathematik/Lia6_04.md`, 1244–1252.

Bestimme pro Tor ein konkretes Sammel- und Wissensende; prüfe Teile, Regel,
Matrix, Sichtbarkeit und Rückweg gemeinsam. Vier Teile sind kein universeller
Standard. Ein Bonustor wird nicht automatisch zur Sperre vor jeder Fachstation.
Auch puzzlefreie Geheimzweige sind belegt, etwa `5/Deutsch/Lia5_07.md`,
491–501, und `6/Mathematik/Lia6_08.md`, 1443–1464.

### F. Geheimfolien bieten einen Rückweg und können gestuft erschlossen werden

`5/Deutsch/Lia5_06.md`, 588–619, kombiniert ein erstes Geheimfach mit
Rückportal, Puzzle und geschütztem Portal zum zweiten Fund; anschließend folgt
der Anschluss an den Aufgabenpfad. `6/Deutsch/Lia6_09.md`, 1004–1029,
öffnet das zweite Geheimfach erst mit dem Schlüssel aus Aufgabe 6 und hält
einen Rückweg bereit. Einfache Fächer benötigen dieses Zusatznetz nicht:
`5/Deutsch/Lia5_07.md`, 491–501.

Ermittle Portalziele nach allen Folieneinfügungen erneut. Eine Geheimfolie
hinter der Abgabe im Quelltext wird für den vollständigen Witness trotzdem
vor dem Einfrieren besucht. Ein früher Rückweg darf erreichbar sein, bevor das
Puzzle fertig ist; er verhindert, dass eine noch unvollständige Sammelphase
zur Sackgasse wird. Behalte die fachliche Aufgabenfolge auch dann bei, wenn
die Referenz zufällig andere Portalnummern oder Sprünge verwendet.

### G. Ganze Aufgabenblöcke können eine zusammenhängende Freigabe erhalten

Klasse 9 erweitert die in den Folgen 05–09 dominierenden kleinen Fundstellen:
`9/Mathematik/Lia9_01.md`, 785–867, legt eine komplette DynFlex-Gruppe unter
Erde; 1431–1497 legt eine weitere unter eine Pflanze. In
`9/Mathematik/Lia9_02.md` liegt die Gießkanne bereits auf der Startfolie bei 73;
eine Pflanze umschließt die Gruppe 193–278 mit der Schaufel bei 266. Diese
erschließt später die Lupe unter Erde bei 436. Ein weiterer vollständiger
DynFlex-Block liegt unter Erde bei 873–941.

Das liefert eine Werkzeugprogression und bündelt die Spielaktion vor einer
Arbeitsphase. Schließe vollständige Container von außen ein, statt Grenzen
in `flex-child` zu setzen. Prüfe vor jeder Pflichtgruppe den Werkzeugpräfix.
Werkzeugbootstrap auf der Startfolie und Werkzeugbelohnungen in Lösungen
sind beide akzeptable Familien; entscheide anhand des folgenden Trägers.

### H. Der wiederkehrende Garten ist ein zulässiger Standardbaustein

Die vier Folge-03-Kurse enthalten denselben Gartenkern unmittelbar vor der
Selbsteinschätzung: Werkzeuge mit Einführungsfunden → vier geschichtete
Puzzleteile → lokales Tor → vier zusammenhängende Belohnungsblöcke.
Die geordnete Folge der vier Teile und der vier Schlussblöcke ist jeweils
Erde – Pflanze – Pflanze – Erde. Pro Garten sind fünf Erd- und fünf
Pflanzeninstanzen sowie 18 Energiekisten, acht Goldtruhen und vier
Diamanttruhen vorhanden; dies sind Fundinstanzen, keine Ressourcenmengen.

Belege: `5/Deutsch/Lia5_03.md`, 707–749;
`5/Mathematik/Lia5_03.md`, 1250–1292;
`6/Deutsch/Lia6_03.md`, 906–948;
`6/Mathematik/Lia6_03.md`, 1622–1664.

Zähle dies als eine wiederkehrende Familie und vier beobachtete Einsätze.
Die Wiederholung allein ist kein Qualitätsmangel und kein Ausschlussgrund.
Der Garten darf neben den anderen Familien gewählt und passend mit ihnen
kombiniert werden. Übernimm nicht automatisch seine Mengen in jeden Kurs.
Bei aktiven Achievements ist er Teil des vollständigen Bearbeitungspfads;
seine Belohnungen dürfen keine früher benötigten Pflichtkosten finanzieren.
Die vorhandene Gartenüberschrift und Erzählprosa bleiben Bestandsmerkmale,
keine Ausnahme vom Textvertrag.

## Konkreter Abgleich vor der Umsetzung

Wähle mindestens drei passende reale Vergleichskurse und lies ihre
Originalausschnitte. Vergleiche bei einem Kurs der Größenordnung von Klasse
5/6 bevorzugt auch die neueren Folgen 05–09; bei größeren zusammenhängenden
Aufgabenblöcken ziehe Klasse 9 hinzu. Liefere im internen Plan zu jedem
gewählten Fund oder Gate diese verbundenen Angaben:

| Entscheidung | Erforderlicher Abgleich |
|---|---|
| Platzierung | Bestehende Überschrift oder Teilaufgabe, vollständige Trägergrenze, erste mögliche Begegnung, Referenz mit Pfad/Zeile |
| Rolle | Startbestand, Belohnung einer konkreten Lernhandlung, Werkzeug für spätere Schicht, Puzzleteil, Geheimzugang oder Abschlussfreigabe |
| Abstand und Spielfluss | Welche fachlichen Teilaufgaben liegen vor der Begegnung, bis zur Verwendung und bis zur nächsten Spielphase? Welche Aktionen folgen ohne Facharbeit dazwischen? |
| Abwechslung | Welche belegte Familie bleibt wiedererkennbar? Was verändert sich durch konkreten Träger, Werkzeugreihenfolge, Schichten, verteilte Hinweise oder Freigabefolge? |
| Fortsetzung | Was ist nach Fund/Öffnung erreichbar, wo wird fachlich weitergearbeitet, welche Ressourcen und Rückwege bleiben? |

Ein kurzer Abstand ist bei Werkzeug → erster Verwendung oder einem bewusst
zusammenhängenden Garten sinnvoll; mehrere Stationen Abstand sind bei
verteiltem Sammeln belegt. Weder ein pauschales Mindestintervall noch eine
feste Höchstzahl aufeinanderfolgender Spielaktionen ist durch diese Baseline
begründet. Vergleiche eine auffällige Häufung mit der Funktion ihrer konkreten
Referenzfamilie und verbessere den Entwurf, wenn sie nur wiederholte
Freigabeklicks ohne erkennbaren neuen Nutzen erzeugt.

Durchlaufe den Entwurf anschließend aus Lernendensicht: Begegnung → verfügbare
Aktion → erkennbare Wirkung → fachliche Fortsetzung. Eine technische
Kandidatenmatrix allein bewertet diese Qualität nicht. Wiederhole bei
Nutzerwunsch nach dieser Standardfamilie keine erzwungene Jagd nach einer
anderen Primärmechanik; die passenden Kombinationen und der funktionsfähige
Ablauf entscheiden. Die genaue Ausgabe und der vollständige Witness folgen
dem Hauptskill.

## Grenzen der Übernahme

- Vorhandene Hinweise auf Werkzeuge oder UI-Funde sind keine Erlaubnis für
  neue allgemeine Hinweistexte. Die zwei engen Textausnahmen bleiben bestehen.
- Importierte Templates ohne reale Instanz liefern keinen Fundträger. Parse
  den ganzen Hauptkopf; feste Importzeilen und „Loot ist der letzte Import“
  sind unzulässige Annahmen. Beispielsweise folgt in
  `5/Mathematik/Lia5_03.md` noch der Pentomino-Import auf Loot.
- Globale Schlösser brauchen erreichbare passende Schlüssel; verwende nur die
  kanonischen öffentlichen Makros und geprüften Ziele des aktuellen Katalogs.
- Timertruhen und Timerschlösser erfordern unterschiedliche UI-Zustände.
  Ein überwiegend mit `oncheck` arbeitender Kurs belegt keinen sichtbaren
  Timer-Startbutton für ein Schloss.
- Der Bonusbereich nach `@Abgabe` in `5/Mathematik/Lia5_06.md`, 1327–1341,
  verlangt ausdrücklich einen Besuch vor dem Abgabequiz. Das ist ein Anlass
  zur Prüfung des tatsächlichen Ablaufs, kein Rezept für spät unerreichbare
  Abschlussbelohnungen.

Die vorliegende Referenzanalyse ist statisch. Sie behauptet weder einen
Browserdurchlauf aller Kurse noch einen bereits bestandenen vollständigen
Witness für sämtliche Ausgangsdateien.

## Kursmatrix und konkrete Abschnittsanker

Die Spalten enthalten Zeilen der tatsächlichen Überschriften. „Spiel-/Geheimfolie“
nennt Quelltextpositionen; der Zugangspfad folgt den oben beschriebenen
Abhängigkeiten. Die fachlichen Anker schließen Reflexion und Geheimfolien aus.
Die drei unnummerierten/00-Einstiege sind gesondert an ihrem Pfad erkennbar.

| Kurs | Start | Fachstationen | Spiel-/Geheimfolie | Reflexion / Abgabe |
|---|---:|---|---|---|
| `5/Deutsch/Lia5_00.md` | 43 | 528, 569, 702, 825, 846, 866 | – | 1049 / 1067 |
| `5/Deutsch/Lia5_01.md` | 43 | 112, 234, 634, 666, 712, 921 | – | 970 / 990 |
| `5/Deutsch/Lia5_02.md` | 41 | 102, 160, 335, 589, 625, 673 | – | 842 / 858 |
| `5/Deutsch/Lia5_03.md` | 41 | 156, 327, 435, 550, 582, 666 | Das versiegelte Lupendepot 124; Erholungsgarten 707 | 755 / 771 |
| `5/Deutsch/Lia5_04.md` | 42 | 147, 391, 573, 620, 839, 1021 | Ressourcenreserve 123 | 1087 / 1106 |
| `5/Deutsch/Lia5_05.md` | 36 | 120, 275, 410, 557, 713, 852 | Wortdepot 110 | 1027 / 1045 |
| `5/Deutsch/Lia5_06.md` | 36 | 97, 228, 402, 547, 622, 660 | Lesearchiv 588; Lesefund 609 | 697 / 715 |
| `5/Deutsch/Lia5_07.md` | 38 | 59, 88, 216, 387, 504, 598 | Silbenfach 491 | 779 / 795 |
| `5/Deutsch/Lia5_08.md` | 36 | 84, 272, 456, 475, 645, 823 | Blattversteck 889 | 873 / 920 |
| `5/Deutsch/Lia5_09.md` | 36 | 84, 123, 309, 483, 498, 548 | Wiesenfach 470 | 727 / 743 |
| `5/Lia5_SK.md` | 45 | 524, 553, 599, 685, 724, 771, 802, 847, 949 | – | 1051 / 1066 |
| `5/Mathematik/Lia5_00.md` | 40 | 570, 667, 761, 859, 1013, 1127, 1172 | – | 1227 / 1242 |
| `5/Mathematik/Lia5_01.md` | 43 | 123, 220, 376, 512, 618, 725 | – | 823 / 845 |
| `5/Mathematik/Lia5_02.md` | 42 | 115, 368, 543, 667, 763, 867 | – | 924 / 943 |
| `5/Mathematik/Lia5_03.md` | 43 | 141, 345, 439, 667, 895, 1148 | Erholungsgarten 1250 | 1298 / 1319 |
| `5/Mathematik/Lia5_04.md` | 43 | 134, 201, 310, 505, 741, 1029, 1158 | Das Diamantenlager 118 | 1268 / 1289 |
| `5/Mathematik/Lia5_05.md` | 43 | 113, 355, 531, 598, 753, 873 | Bonusfund 1062; Zahlenkeller 1074 | 1028 / 1047 |
| `5/Mathematik/Lia5_06.md` | 43 | 127, 400, 544, 906, 1116, 1149 | Formenlager 1101 | 1292 / 1311 |
| `5/Mathematik/Lia5_07.md` | 44 | 128, 349, 672, 899, 1052, 1316 | Rechenversteck 1433 | 1414 / 1444 |
| `5/Mathematik/Lia5_08.md` | 43 | 111, 351, 462, 516, 834, 1075 | Summenfach 1312 | 1293 / 1337 |
| `5/Mathematik/Lia5_09.md` | 40 | 106, 338, 525, 835, 993, 1130 | Formdepot 513 | 1196 / 1208 |
| `6/Deutsch/Lia6_01.md` | 41 | 114, 186, 232, 384, 598, 632 | – | 654 / 676 |
| `6/Deutsch/Lia6_02.md` | 39 | 105, 289, 478, 571, 752, 919 | – | 1007 / 1023 |
| `6/Deutsch/Lia6_03.md` | 41 | 113, 235, 384, 561, 580, 763 | Erholungsgarten 906 | 952 / 968 |
| `6/Deutsch/Lia6_04.md` | 39 | 123, 180, 286, 319, 489, 604 | Zusatzressourcen 115 | 636 / 648 |
| `6/Deutsch/Lia6_05.md` | 36 | 87, 239, 379, 408, 445, 496 | Wortkammer 684 | 659 / 675 |
| `6/Deutsch/Lia6_06.md` | 36 | 83, 181, 345, 533, 724, 813 | Wortfach 1011; Versfach 1036 | 995 / 1063 |
| `6/Deutsch/Lia6_07.md` | 36 | 88, 240, 476, 628, 664, 716 | Bühnenfach 704 | 915 / 931 |
| `6/Deutsch/Lia6_08.md` | 36 | 88, 166, 217, 260, 301, 517 | Leihfach 654 | 638 / 677 |
| `6/Deutsch/Lia6_09.md` | 36 | 88, 292, 453, 629, 799, 952 | Wortlager 1004; Wortfund 1019 | 988 / 1031 |
| `6/Mathematik/Lia6_01.md` | 41 | 125, 337, 561, 635, 763, 1011 | – | 1087 / 1105 |
| `6/Mathematik/Lia6_02.md` | 43 | 123, 234, 422, 580, 664, 950 | – | 1049 / 1067 |
| `6/Mathematik/Lia6_03.md` | 43 | 127, 364, 693, 869, 1192, 1426 | Erholungsgarten 1622 | 1669 / 1687 |
| `6/Mathematik/Lia6_04.md` | 41 | 142, 263, 444, 674, 977, 1030 | Rechenreserve 133 | 1228 / 1244 |
| `6/Mathematik/Lia6_05.md` | 41 | 110, 244, 362, 456, 660, 860 | Viereckdepot 926 | 905 / 917 |
| `6/Mathematik/Lia6_06.md` | 39 | 105, 248, 497, 711, 847, 1088 | Punktdepot 698 | 1230 / 1242 |
| `6/Mathematik/Lia6_07.md` | 39 | 99, 343, 507, 805, 1068, 1308 | Maßfach 1433 | 1421 / 1468 |
| `6/Mathematik/Lia6_08.md` | 39 | 99, 350, 530, 684, 884, 1168 | Formfach 1443; Bruchfach 1454 | 1431 / 1467 |
| `6/Mathematik/Lia6_09.md` | 39 | 100, 380, 582, 647, 825, 939 | Zahlenfach 570 | 1183 / 1195 |
| `9/Mathematik/Lia9_01.md` | 32 | 89, 378, 626, 779, 1080, 1425, 1644 | Wurzelfach 616 | 1951 / 1963 |
| `9/Mathematik/Lia9_02.md` | 32 | 83, 280, 468, 613, 799, 1071, 1217 | Kartenfach 1421 | 1436 / 1448 |

Nutze für Einfügungen die tatsächliche Überschrift und vollständige Blockgrenze.
Zeilen dürfen nach einem neuen Snapshot nicht ungeprüft weiterverwendet werden.
