# Erde/Pflanze: Positions-, Import- und Lösbarkeitsvertrag

## Geprüfte Grundlage

Diese Referenz beruht auf `lia-loot` Revision
`ae970951fb7304ec9d1dd0f11048ae8a8ee676cb`, README-SHA-256
`08087ab78b6183d6ba1f0ea83437f36bdd2ea452d11658c778502abe336978f1`,
einschließlich `TemplateTargets.md`, Quellparser und Browserfixtures.

## Textneutrale Einbettung

Erde, Pflanzen und ihre Schichten sind strukturelle Hüllen. Sie umschließen
vorhandenen Kurstext wortgleich oder enthalten öffentliche Loot-Makros. Neue
Immersions-, Erzähl-, Szenen-, Übergangs-, Belohnungs-, Fortschritts-,
Motivations- oder Questtexte und dekorative Überschriften sind unzulässig.
Neue Prosa innerhalb oder neben einer Schicht ist nur ein knapper funktionaler
Hinweis für ein konkretes Puzzletor oder eine konkrete Geheimfolie. Jede andere
Einbettung hat gegenüber dem Basiskurs ein Textdelta von null und bewahrt die
relative Aufgabenreihenfolge.

## Drei nicht austauschbare Einbettungsformen

### Blockbereich

```text
@Erdhaufen

… beliebiger lokaler LiaScript-Inhalt …

@EndeErdhaufen
```

Für Pflanzen entsprechend `@Pflanze`/`@EndePflanze`; `@Blume` ist Alias.

Vertrag:

- Öffner und Ende stehen jeweils allein.
- Beide liegen auf derselben Folie und derselben Strukturebene.
- Sie stehen außerhalb von Listen, Zitaten und gemeinsamem HTML.
- Verschachtelung ist erlaubt und schließt strikt LIFO.
- Eine vollständige Liste oder ein vollständiger HTML-Block darf zwischen
  außen stehenden Markern liegen.
- Lokale Quizschlösser bleiben unmittelbar nach ihrem Quiz und vor dem
  Bereichsende.
- Eine Markdown-Überschrift setzt einen noch offenen Bereich zurück; Bereiche
  dürfen nie eine Foliengrenze überqueren.

### Inlinebereich

```text
@Erdhaufen.inline(@Energiekiste)
@Pflanze.inline(@Puzzleteil(tuerkis; 1))
```

Der Payload bleibt in derselben Quellzeile. Verschachtelte öffentliche
Loot-Makros mit eigenen Klammerargumenten sind browserbelegt. Für dynamische
Fremdtemplate-Ausgaben ist weiterhin die Blockform sicherer.

Inlinebereiche besitzen kein Endmakro und erhalten nicht zusätzlich selbst
eine direkte Erd-/Pflanzenschicht.

### Direkte Fundschicht

```text
@Schatztruhe(25; erde; pflanze)
@Puzzleteil(tuerkis; 1; pflanze; erde-unsichtbar)
```

Kanonische Erzeugungstokens:

- `erde`, `pflanze`
- `erde-unsichtbar`, `erde-zauberstaub`
- `pflanze-unsichtbar`, `pflanze-zauberstaub`

Beim Scannen normalisiere zusätzlich den dokumentierten Pflanzenalias
`blume` sowie dessen beiden Verbergungssuffixe. Der kompatible Parser
akzeptiert außerdem die Arten `erdhaufen`, `soil`, `dirt`, `plant` und
`flower` sowie die Suffixe `solid`, `verdeckt` und `dust`. Erzeuge
trotzdem ausschließlich `erde`/`pflanze` mit
`unsichtbar`/`zauberstaub`.

Sie werden links nach rechts als außen nach innen gelesen. Wiederholungen sind
zulässig. Itemverbergung ist eine unabhängige letzte Stufe.

Direkte Schichten sind nur an diesen Fundobjekten zulässig:

- Energie-, Gold- und Diamanttruhen samt `@Energietruhe` und
  `@Diamantentruhe`;
- Schlüssel;
- Puzzleteile;
- Lupe;
- Schaufel;
- Gießkanne.

Nicht direkt schichtbar sind Portale, Schlösser, Puzzletore,
`@Unsichtbar`, `@Zauberstaub`, `@Abgabe`, `@ADetails`,
Quizmakros sowie Erd-/Pflanzencontainer selbst. Solche lokalen Inhalte können
nur vollständig in einem Blockbereich liegen.

## Werkzeug- und Sichtbarkeitspräfix

- Schaufel vor der ersten Pflichterde.
- Gießkanne vor der ersten Pflichtpflanze.
- Lupe vor jedem verborgenen Pflichtobjekt. Der Ort ist mechanisch erzwungen,
  durch unveränderten vorhandenen Kurstext belegt oder – ausschließlich bei
  Puzzletor/Geheimfolie – durch einen zulässigen neuen Hinweis bestimmbar.
- Eine Schaufel hinter Erde bzw. Gießkanne hinter Pflanze ist selbstsperrend.
- Die einzige Lupe hinter einer ohne frühere Lupe nicht auffindbaren
  Pflichtverbergung ist ebenfalls selbstsperrend.
- Werkzeuge sind kursweite Singletons; mehrfache Deklarationen reparieren einen
  unlösbaren Erstfund nicht zuverlässig.
- Pflanzen haben unabhängig von optionaler Verbergung drei Aktionszustände:
  `sichtbar/ungegossen → blühend/gegossen → Inhalt nach Blütenklick
  freigegeben`. `unsichtbar` oder `zauberstaub` kann als eigene
  vorgelagerte Sichtbarkeitsstufe hinzukommen.
- Umweltbedingungen und `@lootif` zählen als zusätzliche Kanten im
  Erreichbarkeitsgraphen.

## Puzzleteile in Erde und Pflanzen

`@Puzzleteil` ist ein direkter Schichtträger und darf beliebig viele geordnete
Optionen `erde`/`pflanze` sowie ihre Verbergungsvarianten tragen. Die Optionen
werden links nach rechts als außen nach innen gelesen; eine Itemverbergung
`unsichtbar` oder `zauberstaub` bleibt eine getrennte letzte Stufe. Alternativ
kann das Teil in einem vollständigen Erd-/Pflanzenblock oder browserbelegt als
Payload von `@Erdhaufen.inline` beziehungsweise `@Pflanze.inline` liegen.

Jede Schicht benötigt ihr eigenes erreichbares Werkzeug- und gegebenenfalls
Lupenpräfix. Das Teil, alle Werkzeuge, alle Spawn- oder Umweltvoraussetzungen
und jede notwendige Decodierinformation liegen vor dem eigenen Tor. Das Tor
selbst darf weder geschichtet noch von Erde, Pflanze oder `@lootif` umschlossen
werden. Ein Puzzleteil besitzt kein Oberflächenziel; eine Platzierung neben
einer importierten oder globalen Oberfläche ist nur ein normaler Fund.

Die vollständige Positionsmatrix, Kombinationsregeln und Portalwechselwirkungen
stehen in [puzzle-portal-design.md](puzzle-portal-design.md).

## Portale innerhalb von Freigaben

Portale akzeptieren keine direkten Erd-/Pflanzenschichten und keine gemeinsamen
Fundoptionen. Ein Autorenportal darf jedoch vollständig in einem lokalen
Erd-/Pflanzenblock liegen, wenn Werkzeug, Portalziel, Schlüsselpräfix und
Rückweg bereits im Zustandsgraphen nachgewiesen sind. Alternativ liegt ein
geschichtetes Fundobjekt unmittelbar neben dem Portal. Ein Portalschloss folgt
weiterhin unmittelbar auf das betroffene Portal und darf durch die
Bereichsgrenze nicht von ihm getrennt werden.

Eine Freigabe macht aus einem Einwegportal keinen Rückweg und aus einem
`seitenwechsel`-Schloss keine Portalexklusivität. ToC, normale Navigation,
temporäre Rückportale und Puzzletorgrenzen werden als getrennte Kanten geprüft.
Portal-/Schlüsselpfade erhalten keinen neuen Begleittext.

## Blockpositionen relativ zu Kursstrukturen

| Träger | Sichere Form | Ausschluss |
|---|---|---|
| Startfolie nach Werkzeugfund | Top-Level-Block erst hinter sichtbarem Werkzeug-Bootstrap öffnen | Werkzeug darf nicht im eigenen Block liegen |
| ganze H2-Folie | Öffner nach Folienauftakt, Ende vor nächster Überschrift | Werkzeug muss auf früher erreichbarer Folie liegen |
| H2-Präfix oder -Suffix | nur einen top-level Teilblock am Anfang oder Ende schließen | keine HTML-/Feedback-/Foliengrenze kreuzen |
| DynFlex-Gruppe | Öffner vor `<section class="dynFlex">`, Ende nach `</section>` | nie in `flex-child` öffnen oder schließen |
| eigenständiges natives Quiz | Frage, Quiz, Hinweis und Lösung vollständig einschließen | nicht über die Folie hinaus |
| lokale Fremdkomponente | vollständigen Top-Level-Komponentenblock umschließen | nicht innerhalb ihrer HTML-Ausgabe |
| Lösungsschwanz | Block um Belohnungsband oder direkte Schicht am Funditem | fachliche Musterlösung nicht beschädigen |
| Fließtext | kurze Inlineform | kein mehrzeiliger Payload |
| global erzeugte UI | keine scheinbar lokale Blockhülle | Zieltruhe oder gegatete Deklaration verwenden |
| Abgabebereich | Block um lokalen Inhalt möglich | nie ohne vorherigen vollständigen Pflichtwitness |

## Native LiaScript-Oberflächen

Truhen können zusätzlich an sechs nativen Oberflächen liegen. Ein
`@Schluessel` kann genau eines dieser Ziele tragen; sowohl Zieltruhen als auch
solche Oberflächenschlüssel dürfen direkte Erd-/Pflanzenschichten besitzen.

| Ziel | Scope | Erforderlicher Zustand |
|---|---|---|
| `toc` | global | Inhaltsverzeichnis sichtbar |
| `menu` | global | Hauptmenü sichtbar |
| `classroom` | global | Classroom-Oberfläche sichtbar |
| `info` | global | Infooberfläche sichtbar |
| `translator` | global | Übersetzungsoberfläche sichtbar |
| `mode` | global | Modusoberfläche sichtbar |

Globale Funde benötigen bei folienbezogener Variation einen `anker`. Ihre
Oberflächen liegen nicht physisch innerhalb eines lokalen Erdblocks.

## Vollständige Matrix der zwölf Fremdtemplate-Ziele

Direkte Erde/Pflanze liegt an diesen Zielen ausschließlich als Schicht einer
Energie-, Gold- oder Diamanttruhe. Die Zieldatensätze in
`placement-catalog.json` sind die maschinenlesbare Entsprechung.

| Ziel-ID | Direkter Import | Ort/Scope | Reale Instanz und Zustand | Blockalternative |
|---|---|---|---|---|
| `dynflex` | lia-DynFlex | erste sichtbare DynFlex-Fläche der Quellfolie | echte `.dynFlex`-Registry/Fläche | gesamten `section` von außen umschließen |
| `timer` | lia-timer | sichtbares Timerquiz | Truhe bei sichtbarem Timer; Schloss nur bei `onclick`-Startbutton | vollständiges Top-Level-Quiz |
| `boardmode` | lia-board-mode | globales Board-Menü | Schriftmenü geöffnet | keine lokale Hülle |
| `marker` (Alias `textmarker`) | lia-marker | globales Markermenü | Panel geöffnet; `anker` für Folienbindung | keine lokale Hülle |
| `markerquiz` | lia-marker | erste sichtbare Markerquiz-Fläche | echte lokale Markerquizinstanz | ganzen Top-Level-Quizblock umschließen |
| `annotation` | lia-annotation | globale Annotationleiste | Annotationen ausgeblendet | keine lokale Hülle |
| `canvasocr` | lia-canvas-ocr | echtes `canvas.lia-draw` | Canvas geöffnet | vollständige lokale Canvas-Aufgabe |
| `kachel` | lia-kachel | ganze Kachelaufgabe | echte sichtbare Kachelinstanz | vollständige lokale Aufgabe |
| `mathpath` | lia-mathpath | gesamter zugehöriger Quizbereich | sichtbarer `@Explain`-Link; nicht bloßer Import | vollständiges Top-Level-Quiz |
| `llm` | lia-llm | ganzer zugehöriger Quizbereich | sichtbarer Ownership-/Runtime-Marker | vollständiges Top-Level-Quiz |
| `coordinate` | lia-coordinate; JSXGraph wird vom Template mitgeführt, ein zusätzlicher Direktimport ist nur konservatives Fixturemuster | registriertes Board | sichtbarer registrierter `containerObj`; DOM-ID allein reicht nicht | vollständigen Board-/Aufgabenblock umschließen |
| `freeze` | lia-freeze-v2 | erste sichtbare Abgabe-/Exam-/ADetails-/Bar-/Eval-Fläche | Truhe auch am Eval-Platzhalter; Schloss nur an echten Controls | lokalen Abgabeblock umschließen |

`textmarker` ist ein Eingabealias des kanonischen Ziels `marker`. Die
Tabelle enthält damit zwölf kanonische Ziel-IDs.

Für folienlokale Ziele gilt:

- Zieldeklaration und sichtbare Instanz liegen auf derselben Quellfolie.
- Die Runtime nimmt das erste sichtbare passende Exemplar dieser Folie.
- Die Deklaration darf textuell davor oder danach liegen.
- Es gibt keine Zielsyntax für das zweite oder dritte Exemplar.
- Eine unmittelbar folgende Deklaration verbessert Lesbarkeit, ändert aber
  nicht die Auswahlregel.

## Imports ohne Truhenziel

Keine Ziel-ID besitzen:

- `lia-orthography`,
- `lia-Mathe` und Bruchquizvarianten,
- `lia-navigation`,
- `lia-resetter`,
- Algebrite,
- JSXGraph allein.

Ihre lokalen Ausgaben können als vollständiger Blockinhalt umschlossen oder mit
einem benachbarten geschichteten Fundobjekt kombiniert werden. JSXGraph bleibt
für `coordinate` eine direkte technische Abhängigkeit.

`pentominoquiz` ist ein Schlossziel, aber kein Truhenziel und daher kein
direkter Erd-/Pflanzenträger. Erde/Pflanze kann nur den gesamten lokalen
Pentominoquizblock umschließen.

## Importreihenfolge und Positionsvariation

Vollständig belegte Erzeugungsreihenfolge:

1. ausdrücklich direkt importierte technische Abhängigkeiten vor ihrem
   Template; steht JSXGraph separat im Kopf, dann vor `lia-coordinate`;
2. benötigte Fremdtemplates;
3. `lia-freeze-v2` vor `lia-mathpath`, wenn dessen `@ADetails` genutzt
   wird;
4. `lia-loot`.

Explizite Browserfixtures belegen beide Reihenfolgen nur für:

- `lia-loot` ↔ `lia-navigation`;
- `lia-loot` ↔ `lia-freeze-v2`.

Für DynFlex, Timer, Board-Mode, Marker, Annotation, Canvas, Kachel, LLM,
Coordinate und MathPath ist die Gegenreihenfolge Loot vor Fremdtemplate nicht
gesondert belegt. Daraus folgen:

- Ein Mapper enumeriert bei `N` Imports alle `N+1` Quellslots und
  protokolliert pro relevantem Paar `course_observed`,
  `browser_tested` oder `unproven`.
- vorhandene Reihenfolge erhalten;
- keine beliebige Permutation behaupten;
- in neuen Köpfen bis zu weiteren Tests Fremdtemplates vor Loot setzen;
- `lia-loot` weder über Zeile noch „letzter Import“ erkennen;
- rohe Import-URLs unverändert erhalten und nur für Erkennung sowie
  Deduplikation eine normalisierte Vergleichsform bilden; für Targetprovider
  nicht auf transitive Importe vertrauen.

## Zielvertrag und Katalogexpansion

Eine lokale Zieltruhe ist nur gültig, wenn der Provider direkt importiert ist,
auf derselben Quellfolie eine echte passende Instanz existiert und der
erforderliche UI-Zustand erreichbar ist. Bei `boardmode`, globalem `marker`
und `annotation` ersetzt die durch den Direktimport erzeugte globale
Oberfläche die lokale Instanz; ihr erforderlicher Zustand muss erreichbar sein
und eine foliengebundene Variation benötigt `anker`.

Bei mehreren Zielargumenten erzeugt jedes Ziel seine eigene vollständige
Fund- und Schichtkette. Beispiel:

```text
@Schatztruhe(25; dynflex; canvasocr; erde; pflanze)
```

ist im Witness nicht eine, sondern zwei Truhen, zwei Erd- und zwei
Pflanzeninstanzen. Fehlende Ziele können Phantomobjekte im Achievement-Katalog
erzeugen.

## Abschluss- und Achievement-Witness

Aktueller Highscore-Vertrag:

- alle Kursfolien wurden mindestens einmal geladen;
- jedes katalogisierte bewertbare native Quiz ist `solved` oder
  `resolved`;
- erst der letzte noch offene Status löst die Abschlussprüfung aus;
- für das Achievement „alle Quizze korrekt“ müssen alle Quizze korrekt sein.

Der Witness muss zusätzlich zeigen:

1. Werkzeug-/Lupenpräfix jeder Pflichtschicht;
2. richtige LIFO-Schließung und Foliengrenzen;
3. alle Schlüssel vor ihren Schlössern;
4. alle Puzzleteile vor dem Puzzletor;
5. Rückweg jedes Pflichtportals;
6. Gießen und Blütenklick jeder Pflichtpflanze;
7. Expansion aller Mehrzieltruhen;
8. erreichbare Abgabe;
9. keine für den korrekten Quizpfad notwendige Fehlantwort.

Bei aktivem `@achievements` ist eine nicht erreichbare Erd- oder
Pflanzeninstanz kein dekorativer Randfehler, sondern bricht den 100%-Pfad.

## Variationsfingerprint

Speichere pro Entwurf mindestens:

```text
Primärmechanik
| Topologie
| Ressourcenmodell aus Startbestand, Pflichtkosten, Reserve und Belohnungen
| Werkzeugbootstrap
| Trägerklassen
| Erd/Pflanzen-Reihenfolge und Tiefe
| Sichtbarkeit/Umwelt
| Zielorte lokal/global
| Puzzle/Portal
| Belohnungsmix
| Pacing
```

Ein neuer Kurs unterscheidet sich vom ähnlichsten früheren Kurs in mindestens
drei strukturellen Dimensionen; darunter liegt mindestens Primärmechanik,
Topologie oder Ressourcenmodell. Gegenüber dem unmittelbar vorherigen Entwurf
wechselt zusätzlich Primärmechanik oder Topologie. Eine andere Farbe, Matrix
oder Anzahl allein genügt nicht. Eine neue Erzähloberfläche ist nach dem
Textvertrag ohnehin unzulässig.
