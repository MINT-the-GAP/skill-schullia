# Referenzprofil der Wochenaufgaben 5/6, Folgen 01–03

## Provenienz und Geltungsbereich

Analysiert wurden zwölf Dateien aus `MINT-the-GAP/Wochenaufgabe`, Revision
`f55442bd5aa8804040e53f144bde461653defbbc`:

- `5/Deutsch/Lia5_01.md` bis `Lia5_03.md`
- `5/Mathematik/Lia5_01.md` bis `Lia5_03.md`
- `6/Deutsch/Lia6_01.md` bis `Lia6_03.md`
- `6/Mathematik/Lia6_01.md` bis `Lia6_03.md`

Alle zwölf importieren und verwenden bereits `lia-loot`. „Normal“ bedeutet
hier also: vorhandene Gamification ohne Erde/Pflanzen in 01/02 und mit einem
ersten, stark duplizierten Garten in 03.

## Gemeinsame Kursgrammatik

Der robuste Aufbau lautet:

1. einmaliger LiaScript-Hauptkopf mit direkten Templateimports;
2. H1-Startfolie mit Ressourcen, Achievements, Highscore und UI-Funden;
3. Begrüßung, Abgabehinweis, Tutorial und Bedienhinweise;
4. sechs fachliche H2-Stationen;
5. drei unbewertete Selbsteinschätzungen;
6. eigene H1-Abgabefolie mit `@Abgabe`, Freeze-Schloss und `@Auswertung`.

Die häufigste Aufgabeneinheit ist:

```text
Operator/Teilaufgabe
→ Timer-Metadaten
→ natives Quiz oder importiertes Aufgabenmakro
→ ****************
→ Musterlösung und Loot
→ ****************
→ @ADetails
```

Mehrere Einheiten liegen oft in
`<section class="dynFlex"><div class="flex-child">…`. Schlüssel befinden
sich häufig in einer früheren Karte, das zugehörige DynFlex-Schloss nach dem
abschließenden `</section>`.

Begrüßung, Tutorial, Gartenüberschrift und vorhandene Bedienhinweise sind hier
nur Bestandsmerkmale der zwölf analysierten Kurse. Sie sind keine Erlaubnis,
beim Gamifizieren neue Immersions-, Übergangs-, Portal-, Garten- oder
Belohnungstexte und keine neuen dekorativen Überschriften zu erzeugen. Der
vorhandene Text und die relative Aufgabenreihenfolge bleiben unverändert; neue
Prosa ist ausschließlich ein knapper konkreter Puzzletor- oder
Geheimfolienhinweis.

## Drei Ausgangsprofile

### Folge 01

- Basiskette aus UI-Truhen, Aufgabenbelohnungen, Schlüsseln und Schlössern.
- Stärker gemischte fachliche Darstellungen; teilweise DynFlex, teilweise
  eigenständige Aufgaben.
- Keine Erde und keine Pflanzen.

### Folge 02

- Dichte Aufgabenserien und klarere Schlüssel-/DynFlex-Schlossketten.
- Viele importierte Quizformen wie Orthography, Markerquiz, Coordinate und
  Canvas.
- Keine Erde und keine Pflanzen.

### Folge 03

- Die regulären sechs Aufgabenstationen bleiben erhalten.
- Anschließend liegt ein `## Erholungsgarten` vor der Selbsteinschätzung.
- Deutsch 5 besitzt zusätzlich einen optionalen Lupen-/Portalzweig; Mathematik
  5 nutzt zusätzlich Pentominoquizze.
- Der Garten ist kein gutes Generatormuster, sondern der wichtigste
  Duplikat-Gegentest.

## Kursmatrix und konkrete Abschnittsanker

Zeilen sind 1-basiert und beziehen sich auf die oben genannte Revision.

| Kurs | Kopf | Start | Fachstationen | Garten | Selbstreflexion | Abgabe |
|---|---:|---:|---|---:|---:|---:|
| 5 Deutsch 01 | 1–41 | 43–109 | 110–967 | – | 968–987 | 988–997 |
| 5 Deutsch 02 | 1–39 | 41–99 | 100–839 | – | 840–855 | 856–866 |
| 5 Deutsch 03 | 1–39 | 41–153 | 154–646 | 647–694 | 695–710 | 711–723 |
| 5 Mathematik 01 | 1–41 | 43–122 | 123–822 | – | 823–844 | 845–853 |
| 5 Mathematik 02 | 1–39 | 42–114 | 115–924 | – | 925–943 | 944–951 |
| 5 Mathematik 03 | 1–41 | 43–140 | 141–1249 | 1250–1297 | 1298–1318 | 1319–1327 |
| 6 Deutsch 01 | 1–39 | 41–111 | 112–651 | – | 652–673 | 674–683 |
| 6 Deutsch 02 | 1–37 | 39–102 | 103–1004 | – | 1005–1020 | 1021–1030 |
| 6 Deutsch 03 | 1–39 | 41–110 | 111–903 | 904–949 | 950–965 | 966–976 |
| 6 Mathematik 01 | 1–39 | 41–124 | 125–1086 | – | 1087–1104 | 1105–1113 |
| 6 Mathematik 02 | 1–41 | 43–122 | 123–1048 | – | 1049–1066 | 1067–1075 |
| 6 Mathematik 03 | 1–41 | 43–126 | 127–1621 | 1622–1668 | 1669–1686 | 1687–1695 |

Für neue Einfügungen ist die Überschrift der stabile Anker. Zeilennummern
dienen nur dem Rückbezug auf die geprüfte Revision.

## Importvarianten, die der Mapper beherrschen muss

- Der Kopf reicht je nach Kurs bis Zeile 37, 39 oder 41.
- In Deutsch steht `mode` nach den Imports, in Mathematik vor ihnen.
- Leerzeilen trennen Importgruppen; Imports bilden keinen lückenlosen Block.
- Die Reihenfolge `navigation`/`kachel` variiert.
- `mathpath` steht in 5 Mathematik 02/03 deutlich früher als in den übrigen
  Kursen.
- `lia-loot` ist in elf Kursen zufällig der 18. Direktimport, aber nicht
  immer der letzte: In `5/Mathematik/Lia5_03.md` folgt anschließend
  `lia-pentominos`.
- `6/Mathematik/Lia6_01.md` besitzt nur 17 Importe, weil `lia-resetter`
  fehlt.

Daraus folgen vier harte Regeln:

1. Den gesamten Hauptkopf parsen.
2. Nie feste Importzeilen oder „Loot ist letzter Import“ voraussetzen.
3. Bestehende Reihenfolge und URL bewahren.
4. Importpräsenz und reale Zielinstanz getrennt erfassen.

## Fachliche Trägerfamilien

Die zwölf Kurse decken folgende relevante Positionen ab:

- native Text-, Zahlen-, Auswahl-, Matrix-, Tabellen- und
  Drag-and-drop-Quizze;
- `@orthography` und `@diktat`;
- `@TextmarkerQuiz` und Markerquiz-Flächen;
- Canvas/OCR und Coordinate-/DGS-Boards;
- Geometrie-, Bruch-, Kachel- und Pentomino-Komponenten;
- offene LLM-Quizze;
- einzelne Top-Level-Aufgaben und große DynFlex-Gruppen;
- Lösungsschwänze zwischen Sterntrennern;
- lokale Zielkomponenten und globale Werkzeugleisten.

Ein Generator darf daher nicht nur „nach Aufgabe 6“ kennen. Er muss mindestens
die Startfolie, jede H2-Grenze, jeden Top-Level-HTML-Container, jeden
eigenständigen Quizblock, jeden Lösungsschwanz, jede reale Templateinstanz und
die Abgabefolie als eigene Kandidatenklasse erfassen.

## Der vorhandene Garten als Anti-Fingerabdruck

Die vier 03-Kurse verwenden denselben strukturellen Garten; die Deutsch- und
Mathematikpaare der jeweiligen Klassen sind sogar inhaltlich kopiert:

- je eine sichtbare Schaufel und Gießkanne;
- je fünf Erd- und fünf Pflanzeninstanzen;
- vier Puzzleteile in der Folge Erde–Pflanze–Pflanze–Erde;
- ein lokales türkisfarbenes 2×2-Puzzletor;
- vier Blockcontainer in der Folge Erde–Pflanze–Pflanze–Erde;
- in jedem Block derselbe Payload aus vier Energiekisten, zwei Goldtruhen und
  einer Diamanttruhe.

Pro Garten entstehen dadurch 18 Energiekisten, acht Goldtruhen und vier
Diamanttruhen. Topologie, Werkzeugkette, Schichtfolge, Puzzle, Belohnungsmix,
Pacing und die vorhandene textliche Oberfläche wiederholen sich.

Die eigentlichen Gartenblöcke sind nach LF-Normalisierung in allen vier Kursen
zeichenidentisch: 1493 Zeichen, SHA-256
`ab77a4dee31950aff71b338d29a4cfc51afdbcb1e03f269711d598a3731176de`.
Geprüfte Bereiche: 5 Deutsch 03 Zeilen 647–689, 5 Mathematik 03
1250–1292, 6 Deutsch 03 904–946 und 6 Mathematik 03 1622–1664.

Der Fingerabdruck muss als Duplikat gelten. Eine neue Variante darf ihn nicht
durch bloße andere Farben, Zahlen, Preise oder Überschriften reproduzieren.

## Statische Warnbefunde der Ausgangskurse

Die Referenzkurse sind Strukturbelege, keine fehlerfreien Master:

- In mehreren Mathematik-6-Kursen stehen UI-Schlösser ohne alle passenden
  Schlüssel. Bei aktivem `@achievements` ist der vollständige Pfad statisch
  nicht gesichert.
- Importierte Templates `kachel`, `llm` oder `mathpath` besitzen in
  einzelnen Kursen keine belegte reale Zielinstanz.
- Alle Timer laufen überwiegend mit `oncheck`. Eine Timertruhe ist möglich,
  ein Timer-Schloss braucht dagegen einen sichtbaren `onclick`-Startbutton.

Übernimm daher nie die bloße Existenz eines Musters als Gültigkeitsbeleg.

## Strukturelle Variantenfamilien

Aus der Baseline ergeben sich mindestens diese voneinander unabhängigen
Topologien:

1. Werkzeug-Bootstrap auf der Startfolie, Erde/Pflanzen über Stationen verteilt;
2. vollständige Fachstation als Erd- oder Pflanzenfreigabe;
3. komplette DynFlex-Gruppe von außen umschlossen;
4. einzelne Lösungsschwänze oder vorhandene Loot-Funde geschichtet;
5. Expedition über reale lokale Templateziele;
6. Suche über globale Oberflächenziele mit foliengebundenem Anker;
7. optionaler mechanischer Geheim-/Portalzweig mit Rückweg und ohne neuen
   Übergangstext;
8. makrobasierte Gartenfreigabe vor der Selbsteinschätzung ohne neue
   Gartenüberschrift oder Begleitprosa;
9. Abschlussfreigabe mit vorab nachgewiesenem Pflichtpfad.

Wähle pro Kurs nur ein verständliches Teilset, aber kartiere vor der Auswahl
alle technisch möglichen Positionen und ihre Ausschlussgründe.
