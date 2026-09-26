# Mathematik-Templates: Makros und Optionsfamilien

Diese Referenz deckt die öffentlichen Makros der sieben unten gepinnten
Templates ab. Sie ist ein Auswahl- und Optionsgedächtnis; vor konkreter
Generierung die passende lokale Originalstelle lesen. Die vollständigen
READMEs wurden statisch geprüft, bei zusätzlichen Parseroptionen außerdem die
genannten Implementierungsstellen. Private Hilfsmakros mit abschließendem
Unterstrich, DOM-Marker und Runtime-Funktionen sind keine zusätzlichen
Autorenmakros. Zeilenangaben sind 1-basiert und beziehen sich auf die genannte
Revision. Browserausführung wurde für diese Referenz nicht geprüft.

## Reichhaltige Auswahl beim Entwurf

Beachte für Mathematik und Physik die verbindliche
[Fachsprache des Hauptskills](../SKILL.md#verbindliche-fachsprache),
auch in Achsenbeschriftungen, Quizkommentaren und LLM-Anweisungen.
Technische Optionsnamen und dokumentierte Makroaufrufe bleiben unverändert.

- Bei Mathematikantworten algebraische Gleichwertigkeit, Toleranzen und passende
  Eingabehilfen sofort mitplanen: Algebrite für mathematische Texteingaben,
  `@canvas` bei geeigneten Handschriftaufgaben, `@BerechneOCR` für vollständige
  Rechenwege. Erzeuge die fachlich passende Variante bereits vollständig.
- Bei Brüchen Kreis-/Rechteckdarstellung und mathematische Eingaben, bei Funktionen
  Tabelle, Regler, Graph und Rekonstruktion, bei Geometrie Konstruktion und
  kombinierte Prüfkriterien mitdenken. Wähle passende Darstellungen und Hilfen,
  ohne auf eine spätere Einzelanforderung zu warten.
- Verwende Quizvarianten mit nativen Quizoptionen, wenn Hinweise, ausführliche
  Lösungen oder zeitgesteuerte Freigaben zum Entwurf gehören. Schreibe Hinweise
  und Lösungen gleich aus; technische Freigaben müssen tatsächlich vorhandene
  Inhalte und direkt importierte Abhängigkeiten haben.
- Liefere keine Sammelliste leerer Optionen. Eine Hilfe darf keine abzufragende
  Lösung vorwegnehmen: keine sichtbaren Flächenmaße, wenn genau diese berechnet
  werden sollen. Bei Erkundungsaufgaben dagegen Messwerte und Regler aktiv
  einsetzen. Routineentscheidungen selbst treffen und knapp kenntlich machen.
- Für Erklärungen `@Explain` und Glossarhilfen mitdenken; Themen zunächst in
  `Explain.md` beziehungsweise `Glossar.md` nachweisen.

## Quellen und direkte Imports

Die URLs sind die gepinnten README-Imports. Für GitHub-Quellbelege die Form
`https://github.com/<Owner>/<Repo>/blob/<SHA>/<Pfad>#L<Zeile>` verwenden.
Lokale Dateien liegen unter `corpus/sources/<source-dir>/files/`.

| Kürzel | Repository / Revision | source-dir |
|---|---|---|
| OCR | `MINT-the-GAP/lia-canvas-ocr`, `167982ed0804e57b12316c5b54ec9d97807d629e` | `ghrepo-mint-the-gap-lia-canvas-ocr-b602498873` |
| KO | `MINT-the-GAP/lia-coordinate`, `a4d24ee6c7c8b64f9379876f0c3d143e2229d7ff` | `ghrepo-mint-the-gap-lia-coordinate-ad5f35c719` |
| MA | `MINT-the-GAP/lia-Mathe`, `9f6048a438b649f1575609a4020dc63c09f93baf` | `ghrepo-mint-the-gap-lia-mathe-1df98115ce` |
| MP | `MINT-the-GAP/lia-mathpath`, `62548fa72170a7be67e3ad448a366598da1b14b1` | `ghrepo-mint-the-gap-lia-mathpath-011889c391` |
| PE | `MINT-the-GAP/lia-pentominos`, `33d7df37fdf3e2b0ee3d7a4543f3584ef0be025c` | `ghrepo-mint-the-gap-lia-pentominos-08098ff96a` |
| AL | `LiaTemplates/Algebrite`, `b5a675525d0be71e3cc37476a7fba065e9590f62` | `ghfile-liatemplates-algebrite-readme-md-deee131a9c` |
| JX | `LiaTemplates/JSXGraph`, `f426725ff10580b5ebdcc3230a4ca31c415faadb` | `ghfile-liatemplates-jsxgraph-readme-md-b608304eab` |

| Kürzel | Direkter Import | Weitere direkte Imports |
|---|---|---|
| OCR | `https://raw.githubusercontent.com/MINT-the-GAP/lia-canvas-ocr/167982ed0804e57b12316c5b54ec9d97807d629e/README.md` | Algebrite davor |
| KO | `https://raw.githubusercontent.com/MINT-the-GAP/lia-coordinate/a4d24ee6c7c8b64f9379876f0c3d143e2229d7ff/README.md` | JSXGraph davor; Ausnahme rein statischer Import |
| MA | `https://raw.githubusercontent.com/MINT-the-GAP/lia-Mathe/9f6048a438b649f1575609a4020dc63c09f93baf/README.md` | Algebrite bei CAS-Prüfung |
| MP | `https://raw.githubusercontent.com/MINT-the-GAP/lia-mathpath/62548fa72170a7be67e3ad448a366598da1b14b1/README.md` | FreezeREADME vor MathPath nur für automatischen `@ADetails`-Kontext |
| PE | `https://raw.githubusercontent.com/MINT-the-GAP/lia-pentominos/33d7df37fdf3e2b0ee3d7a4543f3584ef0be025c/README.md` | JSXGraph, lia-coordinate, Pentominos in dieser Reihenfolge |
| AL | `https://raw.githubusercontent.com/LiaTemplates/Algebrite/b5a675525d0be71e3cc37476a7fba065e9590f62/README.md` | Keine zusätzlichen Kursmakros |
| JX | `https://raw.githubusercontent.com/LiaTemplates/JSXGraph/f426725ff10580b5ebdcc3230a4ca31c415faadb/README.md` | Keine zusätzlichen Kursmakros |

Importbelege: OCR `README.md:81–91,195,372–378`; KO `README.md:341–354`;
MA `README.md:345–369`; MP `README.md:44–63`; PE `README.md:149–187`;
AL `README.md:18,238–244`; JX `README.md:14–15,68–74`.
Verschachtelte Imports nicht voraussetzen. Nur verwendete Templates
importieren. Gepinnte READMEs bedeuten allein noch keine vollständig gepinnte
transitive Laufzeit: Templateköpfe enthalten teils bewegliche Fremdimporte.

## lia-canvas-ocr

| Öffentlicher Aufruf | Optionen und Einsatz | Beleg |
|---|---|---|
| `@canvas` | Parameterlos unmittelbar unter ein bestehendes Antwortfeld. Handschrifteingabe; kein neues Quiz und kein fachlicher Validator. Auswahlrechteck überträgt den erkannten mathematischen Ausdruck in das Feld. | OCR `README.md:20–34,97–125` |
| `@BerechneOCR(aufgabe[, optionen])` | Genau ein natives Quiz für vollständigen Rechenweg samt Validator. Aufgabe in Backticks, besonders bei Kommata oder Klammern. Zweites Argument `1`/`0` schaltet Zeilenfeedback ein/aus; alternativ enthält ein gemeinsames Backtick-Argument die benannten Optionen. Quizattribute unmittelbar davor, native `[[?]]`-Hinweise unmittelbar danach. Keine separate detaillierte Lösung anhängen. | OCR `README.md:36–54,136–331` |

Die benannten Optionen stehen gemeinsam in **einem** Backtick-Argument und
werden durch Semikola getrennt. Dokumentiert sind `aufgabe`, `stelle`,
`ordnung`, `intervall`, `von`, `bis`, `zweitefunktion`, `seite`, `art`,
`familie`, `teile`, `winkelmass` und `zeilenrueckmeldung`. `aufgabe` kennt 26
Arten von `gleichung` und `nullstellen` über Analysisaufträge bis
`kurvendiskussion`; Pflichtangaben und mathematische Abdeckung für den
konkreten Typ in der aktuellen README nachschlagen. Unbekannte, doppelte,
leere oder für den Aufgabentyp unzulässige Optionen sind Fehler und werden
nicht stillschweigend ignoriert. `@BerechneOCRWithOptions` bleibt nur ein
Kompatibilitätsalias; neue Aufgaben verwenden `@BerechneOCR`.

```markdown
<!-- data-hint-button="1" data-solution-button="3" -->
@BerechneOCR(`f(x)=2*x^3-5*x^2+4*x-9`,`aufgabe=ableitung;ordnung=1;zeilenrueckmeldung=1`)
[[?]] Wende die Potenzregel auf jeden Summanden einzeln an.
```

Belege: OCR `README.md:136–331`,
`docs/berechneocr-functions.md:1–78`.

Nichtnegative ganzzahlige Aufgaben mit `+`, `-`, `\cdot`/`\times` oder `:`
wählen das schriftliche Verfahren automatisch. Keinen Modusparameter erfinden.
Bei Subtraktion Minuend mindestens so groß wie Subtrahend, bei Division
Divisor ungleich null. Zeilenfeedback gilt für Gleichungswege; schriftliche
Verfahren prüfen erforderliche Überträge und Teilrechnungen. Prüfbarkeit
und automatisch erzeugbare Musterlösung sind verschiedene Abdeckungen:
lineare/quadratische Gleichungen und bestimmte reine Potenzgleichungen haben
automatische Schritte; weitere Verfahrensklassen können geprüft werden, ohne
dass eine automatische Schritterzeugung zugesichert ist.
Belege: OCR `README.md:140–195,408–426`.

Stiftfarbe/-breite/-deckkraft, Radierer, leerer/karierter/linierter Hintergrund,
Undo/Redo, Auswahlbereich, Zoom und Größe sind Bedienmöglichkeiten, keine
weiteren öffentlichen Makroargumente. OCR bleibt ein experimenteller
Browserworkflow mit manueller Erkennungskorrektur; erster Modellabruf etwa
80 MiB, maximal 32 erkannte Rechenzeilen, keine automatische Inferenz während
des Schreibens. Keine universell sichere Handschrifterkennung zusichern.
Belege: OCR `README.md:245–310,312–370`.

## lia-Mathe

| Öffentlicher Aufruf | Optionen und Einsatz | Beleg |
|---|---|---|
| `@Strichliste(anzahl)` | Ganze Zahl ab null; inline und in Tabellen; Fünferbündelung. | MA `README.md:13,228–252` |
| `@circleQuiz(bruch)`, `@circleQuizC(bruch,quizKommentar)` | Bruch als Kreissektoren legen; Unterteilungen und Sektoren wählen. `C` reicht nativen Quizkommentar weiter. Sektorenregler 1–32. | MA `README.md:32–109,254–273` |
| `@rectQuiz(bruch)`, `@rectQuizC(bruch,quizKommentar)` | Bruch als Rechteckzellen legen; Zeilen/Spalten jeweils 1–20. `C` für Quizoptionen. | MA `README.md:113–198,275–294` |
| `@liaQuiz(lösung)`, `@liaQuizC(lösung,quizKommentar)` | Je `\liaquiz`-Platzhalter im mathematischen Ausdruck genau ein Makro in derselben Reihenfolge. Jede Eingabe ist ein eigenes natives Quiz, daher bei Bedarf je ein anschließendes `@Algebrite.check`. | MA `README.md:11–30,296–369` |

Alle Quizfamilien mit Lernhinweisen und angemessener Lösungsfreigabe mitdenken;
`C` nimmt beispielsweise einen Backtick-Kommentar
`<!-- data-solution-button="2" -->` entgegen.
`\liaquiz` ist die durch `formula:` definierte Ergänzung mathematischer Ausdrücke und kein
`@`-Makro. Die Reglergrenzen sind Implementationsvorgaben, keine
`min`-/`max`-Argumente. Interne `fqok...`-Antworten niemals selbst verfassen.
Quelle: MA `README.md:11–198,254–369`.

## lia-mathpath

| Öffentlicher Aufruf / Integration | Optionen und Einsatz | Beleg |
|---|---|---|
| `@Explain(thema)` | Erklärungskurs aus `Explain.md` im Overlay; Thema vorher nachweisen. Manuell auch ohne Quiz/Freeze. | MP `README.md:10,102–163` |
| `@Explain` | Automatisches Thema aus `@ADetails`, mehrere Themen dort kommasepariert. FreezeREADME und MathPath direkt importieren. Nativer Hint etwa `[[?]] @Explain`. | MP `README.md:44–63,118–163` |
| `@tooltip(on)`, `@tooltip(off)` | Automatische Glossarmarkierung an/aus bis zum nächsten Aufruf. `off` deaktiviert weder manuelle `data-lia-term`-Elemente noch Explain. | MP `README.md:12,199–231` |
| `*Glossarbegriff*`, `data-lia-term`, `class="notip"` | Vorhandene Glossarbegriffe/Aliasformen; kursive Volltreffer ohne Satzzeichen im `<em>`. `notip` sperrt auch manuelle Markierungen. TOC bleibt ohne Tooltips. | MP `README.md:66–99,166–177` |

Keine beliebigen Erklärungs-URLs oder neuen Glossareinträge als Makrooption
erfinden. `Explain.md` und `Glossar.md` gezielt durchsuchen; der vorhandene
Katalog ist keine Garantie für ein beliebiges Thema.

## Algebrite

| Öffentlicher Aufruf | Prüflogik / Optionen | Beleg |
|---|---|---|
| `@Algebrite.eval` | Direkt unter einem Codeblock; Ergebnisse standardmäßig als Klartext. `pretty(1)` schaltet auf Formeldarstellung. | AL `README.md:323–372` |
| `@Algebrite.pretty` | Wie `eval`, aber alle Ergebnisse dauerhaft als nummerierte LaTeX-Formeln; Fehler rot. | AL `README.md:374–400` |
| `@Algebrite.repl` | Führt den Codeblock aus und öffnet danach ein interaktives Terminal mit demselben Variablenzustand. | AL `README.md:402–416` |
| `@Algebrite.check(soll[, units=1])` | Algebraische Gleichwertigkeit; Ausdruck oder Semikolonliste `[a;b;c]` für mehrere Eingaben. Einheiten standardmäßig aus. | AL `README.md:457–545` |
| `@Algebrite.check2(soll,toleranz[, units=0])` | Absolute Abweichung **kleiner oder gleich** der Toleranz. Sollwerte als Semikolonliste; eine einzelne Toleranz gilt für alle Felder, sonst positionsgleiche Liste. Einheiten standardmäßig an. | AL `README.md:547–601` |
| `@Algebrite.check_margin(unten,oben[, units=0])` | Inklusives Intervall für die erste Eingabe; Einheiten standardmäßig an. | AL `README.md:603–617` |
| `@Algebrite.check_expression(sollgleichung[, units=1])` | Vergleicht die Differenzen linke minus rechte Seite. Einheiten standardmäßig aus; keine allgemeine Gleichheit von Lösungsmengen zusichern. | AL `README.md:619–634` |

Dezimalkomma, Prozent und LaTeX-Normalisierung sind Teil der Implementierung.
Keinen bestimmten Rechenweg oder eine bestimmte Schreibweise als erzwungen
behaupten. Validator ohne Leerzeile direkt an das jeweilige native Quiz
anschließen. Bei einer physikalischen Größe stehen Einheit und Zahlenwert im
Antwortfeld und im Sollwert; für `check` und `check_expression` dann zwingend
`units=1` setzen. Eine falsche oder fehlende Einheit muss falsch bewertet
werden. Bei `check2` darf die Toleranz eine andere, aber äquivalente Einheit
besitzen.

Als SchulLia-Autorenregel Sollterme und Sollgleichungen mit Klammern, Kommata,
Semikola oder verschachtelten Funktionen in Backticks setzen, damit die
LiaScript-Argumentgrenzen eindeutig bleiben; bei neuen symbolischen Aufgaben
Backticks generell bevorzugen, etwa
``@Algebrite.check(`-(K/2)*t^(-3/2)`)``. Diese Schreibweise ist in realen
MINT-the-GAP-Aufgaben belegt und verhindert insbesondere die wiederkehrende
Klammerfehlinterpretation.

Beleg: AL `README.md:189–253,418–634`.

## LiaTemplates/JSXGraph

| Öffentlicher Aufruf | Optionen und Einsatz | Beleg |
|---|---|---|
| `@JSX.Graph` | Codeblock-Makro für ein Board; `board` verfügbar, eigenes `initBoard` über `BOARDID`/`jxgbox` möglich. | JX `README.md:17–21,81–124` |
| `@JSX.Graph.withParams(attribute)` | Codeblock-Makro mit HTML-Attributargument in Backticks, belegt: `boundingbox="[-5,5,5,-5]" axis="false" showNavigation="false"`. | JX `README.md:23–27,126–245` |
| `@JSX.Script` | Board-Code für Lernende per Doppelklick einsehbar und veränderbar. | JX `README.md:29–37,247–309` |
| `@JSX.Eval` | Nach ausführbarem JSXGraph-Codeblock; HTML-Board-Ausgabe. | JX `README.md:39,311–426` |
| `@JSX.Load(url)`, `@[JSX.Load](url)` | Externe Code-Datei asynchron laden mit `LIA: wait`. | JX `README.md:41,428–435` |

Für gewöhnliche Schulgeometrie zuerst passende lia-coordinate-Makros wählen.
Freies JSXGraph für Visualisierungen/Programmieraufgaben, die diese nicht
abdecken. Die gesamte JavaScript-Objektbibliothek ist keine endliche
Makrooptionsliste; konkret benötigte API in Primärdokumentation prüfen.
Lokal ist bei dieser festen Quelle ausschließlich die README gespeichert;
`src/index.ts` und vollständige Attribut-Whitelist liegen hier nicht vor.
Keine unbelegten Webcomponent-Attribute zusichern.

## lia-pentominos

| Öffentlicher Aufruf | Optionen / Einsatz | Beleg |
|---|---|---|
| `@Pentomino(spec)` | Eigenes Zahlenfeld mit einem konfigurierten Stein. | PE `README.md:21–30,189–208` |
| `@Pentominos` | Codeblock; jede nichtleere Zeile eine Instanz auf demselben Feld; `#`-Kommentare. | PE `README.md:21–30,210–232,475–476` |
| `@PentominoDock` | Vollständiges Inventar der 20 Formen, mehrfach entnehmbar. | PE `README.md:32–60,234–273` |
| `@PentominoDockAuswahl(typen)` | Kommaliste in einem Backtick-Argument; Reihenfolge bleibt, unbekannte Typen/leere Auswahl ungültig. | PE `README.md:275–295` |
| `@PentominoQuiz(zielsumme,spec,quizKommentar)`, `@PentominoQuizN(...)` | Genau der konfigurierte Stein zählt; `N` verwendet Werte 50 bis −49. | PE `README.md:106–127,346–409` |
| `@PentominoDockQuiz(zielsumme,quizKommentar)`, `@PentominoDockQuizN(...)` | Ein einzelner Dockstein muss Zielsumme erreichen; Steinsummen werden nicht addiert. | PE `README.md:66–104,297–338` |
| `@PentominoDockQuizAuswahl(zielsumme,typen,quizKommentar)`, `@PentominoDockQuizAuswahlN(...)` | Dockquiz mit eingeschränkter Formauswahl. | PE `README.md:66–69,327–344` |

Vollständige `spec`-Familie: `name` (boardlokal eindeutig), `type`,
`numbers` (je Zelle eine eindeutige Feldposition 1–100), `fixed`
(`true`/`false`, Vorgabe `false`), `color` (sechsstelliges Hex) und
`opacity` (0.2–0.85, Vorgabe 0.58). `numbers` bestimmt Lage/Orientierung;
keinen Drehwinkel ergänzen. Maskierungen `6=x`, `x=6` oder eindeutig
rekonstruierbares nacktes `x` bleiben an der absoluten Feldposition.
Auch auf negativem Feld enthält `numbers` Positionsnummern 1–100, während
die Summe die sichtbaren Werte verwendet.
Belege: PE `README.md:396–409,458–499`.

Vollständige Typen: `I2`, `I3`, `L3`, `I4`, `O4`, `T4`, `L4`,
`S4`, `F5`, `I5`, `L5`, `P5`, `N5`, `T5`, `U5`, `V5`,
`W5`, `X5`, `Y5`, `Z5`. Groß-/Kleinschreibung wird toleriert,
alte Einbuchstabenkürzel nur bei Fünferformen. Kanonische Typnamen wählen.
Spiegeln ist in dieser Revision keine Bedienoption. Für offene Abdeckungen ist
`data-solution-button="off"` die dokumentierte Quizvorgabe; eine echte
Musterlage kann als anschließender Sternblock ergänzt werden.
Quelle: PE `README.md:319–325,355–373,411–499`.

Das Hunderterfeld ist höchstens 520 px breit und passt sich der verfügbaren
**Containerbreite** an. Das Inventar steht bei genügend Platz rechts, sonst
darunter; auch seine Spaltenzahl reagiert auf den Container und nicht nur auf
das Browserfenster. Keine starre Zweispaltenbreite um das Makro bauen.
Quelle: PE `README.md:234–252`.

## lia-coordinate: gemeinsame Regeln

Alle `spec`-Argumente in Backticks schreiben; Bestandteile durch Semikola
trennen. Deutsche/englische Namen sind öffentliche Aliase, einschließlich
`@Regession`. Auf Schreibweise achten: insbesondere `@distance` und
`@angle`. Vollständiger öffentlicher Kopf: KO `README.md:13–320`.

Aktionsknöpfe, Quizrückmeldungen, Tooltips und Eingabehilfen richten sich nach
`language: de` beziehungsweise `language: en` des Kurses. Bei `@DGS` stellt
„Restore initial state“ den autorenseitigen Ausgangszustand einschließlich
gelöschter Makroobjekte und Achsenbeschriftungen wieder her. Der
Vollbildschalter bewahrt beim Verlassen die vorherige eingebettete Größe und
deren Pan-/Zoom-Ausschnitt; Änderungen am Vollbildausschnitt überschreiben ihn
nicht. Diese Wiederherstellung nicht durch eigene Ersatzmakros nachbauen.
Belege: KO `README.md:631–635,1485–1499`.

Eindeutige Board-ID verbindet die Bestandteile. Board zuerst, danach
referenzierte Punkte/Objekte, abgeleitete Geometrie, Quiz und Hilfen.
Zeichenreihenfolge folgt Quellreihenfolge, maximaler Quellrang 20.
Name mit abschließendem `=0` verbirgt nur Beschriftung; technischer Name
bleibt referenzierbar. Belege: KO `README.md:356–369,675–690`.

Die Linienfamilie `linestyle`/`linienstil` kennt `solid`, `dashed`,
`dotted`, `dashdotted`. Sie gilt für Strecken, Geraden, Strahlen, Vektoren,
Bögen, Orthogonalen/Parallelen, Polygonränder, Winkel, Kreise, Tangenten,
Sektoren, Funktionsplots/-eingaben, Graphpunktquizze und Scharen.
Farbe, Füllung, Deckkraft, Pfeile/Endkappen und Linienbreite nur ergänzen,
wo die jeweilige Signatur sie annimmt. Kein allgemeines Durchreichen
beliebiger Stiloptionen. Quelle: KO `README.md:735–759`.

### Board, Punkt und Text

| Öffentliche Makros | Signatur/Optionsfamilien | Beleg in KO README.md |
|---|---|---|
| `@CoordinateSystem`, `@Koordinatensystem` | `xmin,xmax,ymin,ymax` (−4,4,−3,3), `width`, `id`; `axes`/`achsen`, `grid`, `border` oder drei letzte 0/1-Flags. `static`/`statisch` nur benannt. `border=0` sperrt Pan/Zoom/Resize und verbirgt Rahmen. | 371–418 |
| `@AxisLabel`, `@AchsenBeschriftung` | `id=board;xlabel=...;ylabel=...`, TeX möglich. | 607–625 |
| `@Point`, `@Punkt` | `board;name[=0];x;y;farbe;opacity;fix`. Ohne `fix` beweglich; Deckkraft 0–1. | 675–708 |
| `@CoordText`, `@KoordText` | `board;[x;y];inhalt;farbe;opacity`, Text/TeX; Deckkraft 0–1. | 710–733 |
| `@CreatePoint`, `@ErzeugePunkt` | `board;name;zielX;zielY`, zweites Argument zwingend Quizkommentar, minimal `<!-- -->`; Positionstoleranz 0.05. | 627–673 |

### Geometrische Objekte und Messungen

| Öffentliche Makros | Signatur/Optionsfamilien | Beleg in KO README.md |
|---|---|---|
| `@Strecke`, `@distance` | `board;[A;B]` oder direkte Koordinatenliste `[[x;y];...]`; danach Farbe, Name, `length=1`, Design, Linienbreite, Linienart. Namen dynamisch verbunden; Koordinatenliste mit unsichtbaren festen Stützpunkten. | 761–808 |
| `@Line`, `@Gerade`; `@Ray`, `@Strahl`; `@Vector`, `@Vektor` | `board;[A;B]` oder genau zwei Koordinaten, Farbe, Name, Linienart. Automatischer Vektorname aus Endpunkten, `name=0` blendet ihn aus. Strahlen ohne Pfeilspitze. | 810–851 |
| `@Arc`, `@Bogen` | `board;start;ausgangswinkel;ende;eingangswinkel;beschriftung;design;breite[;farbe]`; Endpunkte als Name oder `[x;y]`, Winkel im Einheitskreis. Alternative nach Beschriftung: Farbe, Design, Breite. Linienart anhängbar. | 853–900 |
| `@Perpendicular`, `@Orthogonale`; `@Parallel`, `@Parallele` | Board, Basisname oder Punktpaar, Durchgangspunkt, Farbe, Name, Linienart. | 902–941 |
| `@Midpoint`, `@Mittelpunkt` | Board, Punktpaar oder zwei direkte Koordinaten, Farbe, Name, `wert=1`/`value=1` für Koordinaten. Interaktiv später als Punkt referenzierbar. | 902–941 |
| `@Area`, `@Flaeche` | Board, Punktliste oder direkte Koordinatenliste, Farbe, Deckkraft; `inhalt=1`/`area=1`, `umfang=1`/`perimeter=1`, Linienart. | 943–980 |
| `@angle`, `@Winkel` | `board;name;[A;B;C];farbe;opacity;Wert=1`, alternativ `value=1`; B ist Scheitel, gegen Uhrzeigersinn BA→BC, Linienart. | 982–1021 |
| `@Circle`, `@Kreis` | `board;name;mittelpunkt;farbe;opacity;radius=zahl` oder `radius=punktname`; Radiusvorgabe 1. `inhalt`/`area`, `umfang`/`circumference`/`perimeter`, Linienart. | 1023–1056 |
| `@Tangent`, `@Tangente` | Board, Quellobjekt oder Punktpaar, `[kontaktX;kontaktY]`, Farbe, Linienname, Kontaktpunktname, Linienart. Quelle: Funktion, Kreis oder lineares Objekt. | 1058–1097 |
| `@CircularSector`, `@Sector`, `@CircleSegment`, `@CircularSegment`, `@Kreissektor`, `@Kreissegment` | `board;[zentrum;radiuspunkt;winkelpunkt];farbe;opacity;name;inhalt=1;umfang=1`, Linienart. Alle sechs sind Sektoren, keine durch Sehnen begrenzten Kreissegmente. | 119–127,474–479,1058–1097 |

Designwerte Strecke/Bogen: leer oder `-`, `->`, `<-`, `<->`, jeweils
mit optionaler führender/abschließender `|`-Endkappe; bei Polygonzügen nur
äußere Enden. Breite etwa `2px`, Vorgabe `3px`; Strecke akzeptiert auch
`design=...` und `width=...`. KO `README.md:777–786,868–880`.

### Funktionen, Parameter und Analyse

| Öffentliche Makros | Signatur/Optionsfamilien | Beleg in KO README.md |
|---|---|---|
| `@PlotFunction`, `@PlotFunktion` | `board;funktionsname;term;farbe;linestyle=...`. | 1101–1122 |
| `@PlotInput`, `@PlotEingabeLatex` | `board;funktionsname;farbe;linestyle=...`; LaTeX-Eingabe mit Livegraph. | 1194–1215 |
| `@Schar` | `name;variable;term;board;term=0/1;farbe;linestyle=...`; Parameterregler aus dem Term. | 1992–2131 |
| `@Slider`, `@Regler`, `@Schieberegler` | `board;name;min;max;schritt;startwert;farbe;[[x1;y1];[x2;y2]];lockposition=1`, zudem `visible=0`, `fontsize=...`. Reglerwerte sind Skalare für Terme. | 1155–1192 |
| `@Zeros`, `@Nullstellen`; `@Extrema`, `@Extrempunkte`; `@InflectionPoints`, `@Wendepunkte` | `board;funktionsname;farbe;präfix;wert=1`. `names=[...]`, `wert`/`value`, `werte`/`values=[1;0;...]`, `sichtbar`/`visible=[1;0;...]`. | 1124–1153 |
| `@OrdinateIntercept`, `@Ordinatenabschnitt`, `@Ordinatenachsenabschnitt` | `board;objektname;farbe;präfix;wert=1`; dieselben Listenoptionen. | 148–152,1155–1192 |
| `@Intersection`, `@Schnittpunkt` | `board;objekt1;objekt2;farbe;präfix;wert=1`; dieselben Listenoptionen. Funktionen, lineare Objekte oder Kreise. | 1155–1192 |
| `@Table`, `@Tabelle` | `n=startspalten;x;funktionsname;punktpräfix;id=board`; gekoppelte Wertetabelle. | 1281–1302 |
| `@Regression`, `@Regession`, `@PlotZeichnen` | `board`; Freihand/Regression aktiviert kompaktes DGS-Profil. | 305–307,1933–1958 |

### Graph- und Geometriequizze

| Öffentliche Makros | Signatur/Optionsfamilien | Beleg in KO README.md |
|---|---|---|
| `@PointOnGraph`, `@PunktGraph` | `board;punktname;funktionsname;formel;toleranz;linestyle=...`. | 1217–1248 |
| `@PointOnGraphWithOptions`, `@PunktGraphMitOptionen` | Gleicher erster Parameter, zweiter nativer Quizkommentar. | 236–249,1225–1228 |
| `@PointsOnGraph`, `@PunkteAufGraph` | `board;n=anzahl;d=schritt;punktname;funktionsname;formel;toleranz;linestyle=...`. | 1250–1279 |
| `@PointsOnGraphWithOptions`, `@PunkteAufGraphMitOptionen` | Gleicher erster Parameter plus Quizkommentar. | 252–264,1257–1259 |
| `@Reconstruction`, `@Rekonstruktion` | `board;zielterm;toleranz`; Schar anpassen oder Graph zeichnen. | 1961–1989 |
| `@ReconstructionWithOptions`, `@RekonstruktionMitOptionen` | Gleicher erster Parameter plus Quizkommentar. | 216–233,1970–1973 |
| `@PerimeterQuiz`, `@UmfangQuiz`; `@AreaQuiz`, `@FlaecheQuiz` | `board;eckenzahl;zielwert;absoluteToleranz`, zweites Argument Quizkommentar. Nur lernendenseitig konstruierte Polygone zählen. | 1605–1652 |
| `@ConstructionQuiz`, `@KonstruktionQuiz` | `board;eckenzahl;fest/offen;eigenschaftsliste`, danach `streckentoleranz`/`lengthTolerance`, `winkeltoleranz`/`angleTolerance`; zweites Argument Quizkommentar. | 1655–1720 |
| `@KoordQuiz`, `@GeometrieQuiz`, `@CoordinateQuiz`, `@GeometryQuiz` | `board;eckenzahl;bedingung;...`, zweites Argument Quizkommentar. Alle Bedingungen gelten für dasselbe Polygon. | 1724–1870 |

Bei mehreren Anforderungen an **eine** Konstruktion kombiniertes Quiz nutzen.
Es kennt die Familien `Konstruktion(fest/offen;liste;optionaleToleranzen)` /
`Construction(fixed/open;...)`, `Flaeche(ziel;toleranz)` / `Area(...)`,
`Umfang(ziel;toleranz)` / `Perimeter(...)`, `Form(typ[;exklusiv=...])`.
Formtypen bei genau vier Ecken: `Parallelogramm`/`Parallelogram`,
`Rechteck`/`Rectangle`, `Raute`/`Rhombus`, `Quadrat`/`Square`,
`Trapez`/`Trapezoid`, `Drachenviereck`/`Kite`.
Definitionen sind inklusiv; `exklusiv=Raute|Rechteck` schließt die genannten
Eigenschaften aus. `Form` hat keine öffentliche Toleranzoption und keine
`modus`-, `inklusiv`- oder `exakt`-Option.
Quelle: KO `README.md:1733–1809`.

Konstruktionslisten etwa `S4,W90,S3`; deutsche/englische Langformen vorhanden.
Bei `fest` geometrisch gegen Uhrzeigersinn, zyklischer Startpunkt frei,
niemals rückwärts; wiederholter Typ springt zum nächsten Merkmal desselben
Typs. Bei `offen` zählen Vorkommen und Häufigkeit im selben Polygon.
Standardtoleranzen 0.05 Längeneinheiten / 1 Grad.
Quelle: KO `README.md:1663–1694`.

Quizkommentare bei zweiparametrigen Familien ausdrücklich setzen, minimal
Backtick-Argument `<!-- -->`. Hinweise `[[?]]` und Sternblocklösungen
direkt anschließen. Für `data-solution-timer*` zusätzlich lia-timer direkt
importieren. Interne versteckte Quizantworten nicht nachbauen.
Belege: KO `README.md:635–653,1618–1632`.

### DGS und Instrumente

`@DGS(board[;tools=[...]][;restrictions=[...]])` stellt Werkzeuge bereit.
Fehlende/leere/nichtnumerische Werkzeugliste ergibt vollen DGS-Umfang;
`tools=[0]` nur permanente Infrastruktur. Explizites Profil gewinnt gegen
das von Regression/Rekonstruktion erzeugte kompakte Profil `[910;920;930]`,
unabhängig von Makroreihenfolge. Kein zusätzliches `@Regression` nötig,
wenn `@DGS` bereits Zeichenwerkzeuge anbietet.
Belege: KO `README.md:1502–1577`.

| Werkzeug-ID | Funktion |
|---|---|
| `100` | Format übertragen |
| `140`, `150` | Reservierte IDs Geodreieck/Zirkel; bei explizitem DGS immer vorhanden, nicht über Werkzeugauswahl konfigurierbar |
| `200` | Punkt |
| `310`, `320`, `330`, `340`, `350` | Strecke, Strahl, Gerade, Vektor, Bogen |
| `410`, `420`, `430`, `440` | Orthogonale, Parallele, Mittelpunkt, Winkelhalbierende |
| `510`, `520`, `530` | Polygon, Kreis, Kreissektor |
| `610`, `620` | Winkel, Winkel mit Vorgabemaß |
| `700` | Funktion |
| `810`, `820`, `830`, `840`, `850`, `860` | Nullstellen, Extrema, Wendepunkte, Ordinatenabschnitt, Tangente, Schnittpunkt |
| `910`, `920`, `930` | Freihandzeichnen, Radierer, Regression |
| `1000`, `1010`, `1110`, `1120` | Regler, Text, Zoomrichtung, Achsenskalierung |

IDs sind stabile Fähigkeiten, keine Toolbarpositionen.
Quelle: KO `README.md:1517–1539`.

`restrictions=[100]` sperrt Objekteigenschaften, `200` erlaubt nur Farbe,
Deckkraft und Punktspuren, `300` sperrt und verbirgt Mess-/Werteanzeigen,
`400` sperrt Export. Bei 100+200 gewinnt 100. Einschränkungen mitdenken,
wenn Messwerte oder Funktionsgleichungen die Lösung preisgeben würden;
zur freien Erkundung verfügbar lassen. KO `README.md:1506–1516`.

`@SetSquare(board)` / `@Geodreieck(board)` zeigt direkt das Geodreieck,
allein mit schlankem Overlaycontroller.
`@Compass(board)` / `@Zirkel(board)` aktiviert direkt den Zirkel.
Freie/feste Radien sind Bedienmodi, keine weiteren Makroargumente.
Quelle: KO `README.md:288–303,1525–1530,1874–1929`.

### Zusätzliche statisch belegte Parserformen

Vorhandene Formen erkennen; für neue Inhalte die dokumentierten
Hauptschreibweisen bevorzugen. Auch Exportfähigkeit und interne
Integrationsfelder erkennen, ohne sie als allgemeine Quizoptionen zu erfinden.

| Familie | Zusätzliche Formen / Grenze | Implementierungsbeleg in KO |
|---|---|---|
| Board | `rahmen` alias `border`; Flags auch `true/false`, `ja/nein`, `yes/no`, `on/off`. | `src/shared/coordSpec.ts:24–28,61–76` |
| Linie | `line-style`, `line style`; `dashdot`, Trennstrich-/Leerzeichenvarianten normalisiert. | `src/shared/lineStyle.ts:14–42` |
| Punkt | Export-/Integrationsfelder `helper`/`hilfspunkt=1`, `xexpr`, `yexpr`, `parameter`/`param` für Koordinatenbindungen. Parser nennt sie intern; keine beliebigen allgemeinen Aufgabenoptionen. | `src/subsystems/createPoint.ts:66–75,96–137` |
| Regler | `position=...`; `lockposition`/`positionlocked`/`lock`/`fix`/`fixed` (auch nacktes Flag, 0/1); `visible`/`show`/`anzeigen`; `fontsize`/`font-size`/`schriftgroesse`/`schriftgröße` (8–96). | `src/subsystems/slider.ts:85–171` |
| Tabelle | Spaltenzahl `rows`/`cols`/`columns`/`n`; Punktpräfix `p`/`point`/`points`/`prefix`. | `src/subsystems/table.ts:54–106` |
| Schar | Alte Reihenfolge Farbe vor Termflag; maximal sechs erkannte Parameter. | `src/subsystems/schar.ts:343–414` |
| Konstruktion | Geordnet `geordnet`/`ordered`; offen `frei`/`unordered`; Seitenpräfixe `s`/`seite`/`strecke`/`side`/`length`/`edge`; Winkel `w`/`winkel`/`angle`; Länge zusätzlich `laengentoleranz`/`sidetolerance`/`stol`/`ltol`, Winkel `wtol`/`atol`. | `src/subsystems/constructionQuiz.ts:43–80,136–157` |
| Analyse/Mittelpunkt | Anzeige auch `koordinaten=1`/`coordinates=1`; Analyse `name`/`names`, `prefix=...`. | `src/subsystems/functionAnalysisPoints.ts:85–153`, `src/subsystems/objectAnalysisPoints.ts:100–199`, `src/subsystems/relationObjects.ts:88–115` |
| Sichtbarkeit | `visible`/`sichtbar` bei Strecke, linearen Objekten, Bogen, Relationen, Polygon, Winkel, Kreis, Tangente/Sektor, Funktionsplot. Flagformen unterscheiden sich; kanonisch 0/1 verwenden. | `src/subsystems/distance.ts:125–130`, `src/subsystems/linearObjects.ts:61–66`, `src/subsystems/arc.ts:203–208`, `src/subsystems/relationObjects.ts:92–99`, `src/subsystems/area.ts:74–76`, `src/subsystems/angle.ts:90–92`, `src/subsystems/circle.ts:59–61`, `src/subsystems/tangentSector.ts:105–111`, `src/subsystems/plotFunction.ts:25–30` |
| Namen/Breite | Lineare Objekte/Relationen/Sektoren `name=...`; Tangente `name`/`line`/`gerade`/`tangente`, Kontaktpunkt `point`/`punkt`/`contact`/`beruehrpunkt`/`berührpunkt`; Strecke `stroke-width`, `linewidth`, `width`, `linienstärke`/`linienstaerke`. | `src/subsystems/linearObjects.ts:101–108`, `src/subsystems/relationObjects.ts:102–115`, `src/subsystems/tangentSector.ts:134–139,183–189`, `src/subsystems/distance.ts:111–120` |

### Grenze des statischen Imports

Ein rein statischer Kurs kann statt normaler README `README.static.md`
desselben KO-Commits importieren. Beide Imports niemals zusammen verwenden.
Jedes Board braucht `static=1`/`statisch=1`; allein `border=0` aktiviert
das nicht. Kein automatischer Rückfall auf interaktiv. Beim normalen Import
werden auch mit statischem Board JSXGraph-Abhängigkeiten geladen.
Quelle: KO `README.md:402–418,572–605`.

Statisches Teilset: Board, Achsenbeschriftung, numerisch feste Punkte,
Koordinatentext, Strecken, Geraden/Strahlen/Vektoren, Bögen,
Orthogonalen/Parallelen/Mittelpunkte, Polygone, Winkel, Kreise, alle
Sektoraliases und selbständige Funktionsplots. Referenzen lösen nur direkt
verfasste numerische Punkte desselben Boards auf. Abgeleitete Mittelpunkte,
benannte Linien als Relationsbasis, Regler/fremde Funktionsbindungen sind
nicht verfügbar. Tangenten, Analysepunkte, Tabellen, Scharen, DGS,
Regressions-/Rekonstruktionsaufgaben und sämtliche Quizfamilien brauchen
interaktive Boards. Quelle: KO `README.md:420–495,542–550`.

## Abdeckungsgrenzen festhalten

Diese Referenz kennt öffentliche Makronamen und dokumentierte Optionsfamilien
der genannten Revisionen einschließlich gezielt geprüfter Parserergänzungen.
Sie behauptet weder alle denkbaren JSXGraph-/CAS-Funktionen noch vollständige
Browserkompatibilität oder universelle OCR-/CAS-Beweisbarkeit. Bei neuen
Makros, unklaren Argumenten oder Versionswechseln zuerst lokal suchen und die
Definition/README lesen. Neue Optionen mit eigener Provenienz ergänzen.
