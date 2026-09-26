# Sprach-, Freitext- und Zuordnungs-Templates

Diese Referenz deckt die öffentlichen Makros der fünf unten genannten Templates
im lokal gespeicherten Stand ab. Sie unterscheidet **Template-Defaults** von
**Erstellungsdefaults dieses Skills**. Die Erstellungsdefaults setzen passende
Optionen ausdrücklich ein, sodass Autorinnen und Autoren sie anschließend
entfernen oder ändern können. Unverträgliche Optionen werden nie gemeinsam
aktiviert. Für konkrete Aufgaben zuerst den betreffenden Abschnitt lesen und
anschließend die gepinnte Originalquelle prüfen.

## Quellenstand

Alle Zeilenangaben sind 1-basiert; der SHA gilt auch für die jeweils genannten
Implementierungsdateien. Lokale Dateien liegen unter
`corpus/sources/<Ordner>/files/<Pfad>`.

| Template / Repository | Corpus-Ordner | Revision | öffentliche API |
| --- | --- | --- | --- |
| MINT-the-GAP/lia-llm | `ghrepo-mint-the-gap-lia-llm-0b36ccd3a7` | `684914a814468ddbe2fcc47f2eeea74cf62af54f` | [README.md:25–26, 447–998](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/README.md#L447-L998) |
| MINT-the-GAP/lia-orthography | `ghrepo-mint-the-gap-lia-orthography-3651bf66a5` | `edfca9a9b3fa075a2e977fb3589209508be14bbd` | [README.md:11–78, 106–205](https://github.com/MINT-the-GAP/lia-orthography/blob/edfca9a9b3fa075a2e977fb3589209508be14bbd/README.md#L106-L205) |
| MINT-the-GAP/lia-kachel | `ghrepo-mint-the-gap-lia-kachel-f45fe69aad` | `15b84fba845e783d05d3b77c5cb1f76401146bee` | [README.md:11–39, 103–311](https://github.com/MINT-the-GAP/lia-kachel/blob/15b84fba845e783d05d3b77c5cb1f76401146bee/README.md#L103-L311) |
| MINT-the-GAP/lia-marker | `ghrepo-mint-the-gap-lia-marker-a240ea587f` | `80fe9b1e0b07ee18242f35003bff3660d37da707` | [README.md:11–27, 104–212](https://github.com/MINT-the-GAP/lia-marker/blob/80fe9b1e0b07ee18242f35003bff3660d37da707/README.md#L104-L212) |
| LiaTemplates/Speech-Recognition-Quiz | `ghfile-liatemplates-speech-recognition-quiz-readme-md-560d9ed8c4` | `0edc1ecdd6688af34521133000a795986203cd46` | [README.md:10–86, 118–203](https://github.com/LiaTemplates/Speech-Recognition-Quiz/blob/0edc1ecdd6688af34521133000a795986203cd46/README.md#L118-L203) |

Der Abgleich erfolgte statisch gegen die vollständig gelesenen READMEs und die
unten genannten Implementierungen. Keine Korpusdatei wurde ausgeführt. Diese
Referenz behauptet weder eine aktuelle Live-Revision noch einen Browser- oder
Modelltest. Nach einer Synchronisierung mit verändertem SHA Optionen erneut
prüfen; alte Tag-Beispiele der READMEs garantieren nicht die neuere API.

## Entscheidung vor der Makrowahl

| Lernleistung | Passende Wahl und ausdrückliche Standardausstattung |
| --- | --- |
| Mehrere fachliche Aussagen in einer freien deutschen Antwort | `@LLMQuiz` mit atomaren Kriterien, ausformulierter Lösung, `coverage`, Kurzfeedback, Rechtschreibung und Satzbau; Profil unten verwenden. |
| Ganzheitlicher Lösungsweg oder ausdrücklich zu prüfende Antwortform | Ganzheitliches `@LLMQuiz`; gegebenenfalls passendes `operator`-Profil; ohne `coverage` und Kriterienmarker. |
| Vorgegebenen fehlerhaften Satz/Text verbessern | `@orthography` / `@orthographytext` mit bewusst gewählter Lösungsfreigabe, `doublespacehelp`, Hinweis und erklärender Lösung. Einschränkung der Groß-/Kleinschreibung unten beachten. |
| Nach Gehör schreiben | `@diktat` und passende Kursstimme; Absatzgrenzen als gemeinsame Quizgrenzen planen. |
| Wörter zu einem vorgegebenen korrekten Satz anordnen | Native zielweise Drops; bei austauschbaren gleichen Wörtern `div.Kachel`. `@Kachelfolge(N)` akzeptiert jede Reihenfolge und prüft daher keine feste Satzstellung. |
| Wörter ohne innere Reihenfolge sammeln / Wortarten zuordnen | `@Kachelfolge`, bei unbekannter Anzahl `@KachelfolgeN`, in einer gemeinsamen Tabelle die Gruppen-API. |
| Satzglieder, Wortarten oder Textbelege markieren | `@mark...` plus `@TextmarkerQuiz` und ausformulierter Erklärung; Farblegende fachlich vorgeben. |
| Markierbeispiel demonstrieren | `@marked...`; vorgegebene Markierungen sind keine Lernendenantworten. |
| Einen erwarteten Satz sprechen | `@SpeechRecognition.withFeedback` plus einmaligem Support-Hinweis; Erkennung ist ein Transkriptvergleich und keine Bewertung der Aussprachequalität. |
| Quellenzeilen im Lesetext referenzieren | `@linenumbers` mit bewusst gesetzten physischen Zeilenumbrüchen. |

Importiere jedes tatsächlich verwendete Template direkt im vorhandenen
LiaScript-Hauptkopf. Ein Aufgabenausschnitt bekommt keinen zweiten Kopf.
Importiere nicht alle fünf Templates vorsorglich. Die Wünsche nach vollständigen
Optionen gelten innerhalb der passend gewählten Makrofamilien.

## lia-llm: vollständige Makrooptionen

Kanonische Schreibweise: `@LLMQuiz`, nicht erfundenes `@llmquiz`.
`@LLMQuiz.question` ist im Kopf ein Alias mit identischer Signatur; neue Aufgaben
verwenden `@LLMQuiz`. `@LLMQuiz_` ist die interne Expansion.

Der geprüfte Stand ist Version `0.6.9`; die öffentliche Makrosyntax blieb beim
Laufzeitumbau erhalten. Im ausdrücklichen Quality-Pfad wird bei ausreichendem
Origin-Speicher Qwen3-4B bevorzugt, Qwen3-1.7B ist der kleinere Rückfall. Ist
selbst dafür nach Reserve zu wenig Platz bekannt, startet kein neuer
Quality-Download. Chromium-basierte Browser speichern Quality-Artefakte über
OPFS, andere Browser fallen auf CacheStorage zurück. Daraus keine
Modellgrößenoption für `@LLMQuiz` erfinden und Quality nicht pauschal für jedes
Schulgerät zusichern. Beleg: `README.md:1–6,626–687,725–770`.

Der Aufruf steht direkt an der öffnenden Fence:

````markdown
[[Antwort]]
```text @LLMQuiz(Optionen,`vollständiger Aufgabenwortlaut`)
Musterlösung oder Kriterienblock
```
````

Der erste Parameter enthält immer zuerst den numerischen Schwellenwert.
Weitere Angaben werden mit Semikolon getrennt. Nutze benannte Optionen; die
Kurzform erlaubt nur `Schwelle;solution;feedback;operator`. Benannte und
positionale Angaben dürfen nicht vermischt werden. Optionsnamen und boolesche
Werte sind case-insensitiv; leere, unbekannte und doppelte Optionen sind Fehler.
Der zweite Parameter muss denselben vollständigen Aufgabenwortlaut wie die
sichtbare Aufgabe enthalten und wird mit Backticks gegen Kommas geschützt.
In allen Fächern gilt die
[Fachsprache des Hauptskills](../SKILL.md#verbindliche-fachsprache)
auch für Aufgabenargument, selbst verfasste Kriterien, Musterlösung und
Feedback-Anweisungen. Halte sie mit der sichtbaren Aufgabe konsistent; die
Autorenpräferenz allein ist kein zusätzliches fachliches Bestehenskriterium.
Falsche Aussagen über Energieerhaltung oder eine Verwechslung von Masse und
Gewichtskraft sind dagegen fachlich zu prüfen.

| Option | Zulässige Werte / tatsächlicher Default | Erstellungsregel |
| --- | --- | --- |
| Erster Zahlenwert | `0` bis `1`, Dezimalpunkt; Pflicht, auch wenn der interne Default `0.66` heißt | Meist `0.66` ganzheitlich, `0.55` atomar. Dies ist Konfidenz pro Aussage, keine Gesamtquote. |
| `solution` | `0`, `1`, `false`, `true`; Default `true` | `solution=1` ausschreiben; Lösung erscheint nach bestandener Prüfung. Bei `0` bleibt sie visuell verborgen, im Quelltext weiterhin vorhanden. |
| `feedback` | dieselben booleschen Werte; Default `false` | `feedback=1` ausschreiben; Voraussetzung beider Sprachoptionen. |
| `coverage` | `0 < Wert <= 1`, Dezimalpunkt; Default nicht gesetzt | Im geeigneten Kriterienprofil `coverage=0.80` ausdrücklich setzen. Quote fachlich begründen und erforderliche Anzahl berechnen. Bei unverzichtbaren Einzelanforderungen `coverage=1` wählen oder die Option entfernen. |
| `assessmentengine` | `compact`, `quality`; Default automatische Wahl | Im ausführlichen Kriterien-/Operatorprofil `quality` ausschreiben. `compact` für ausdrücklich kompakte Inhaltsprüfung; Sprache kann getrennt dennoch Quality benötigen. |
| `operator` | `erklaeren`, `erlaeutern`, `beschreiben`, `begruenden`, `vergleichen`, `beurteilen`; Default nicht gesetzt | Nur beim ganzheitlichen Profil passend zum Auftrag setzen; keine automatische AB-Zuordnung. Unterstützte Umlaute/Imperativ-Aliasse werden normalisiert, neue Aufrufe nutzen die genannten IDs. |
| `Rechtschreibung` | boolesch; Default `false` | Bei freien deutschen Textantworten `Rechtschreibung=1` bereits einsetzen; prüft Rechtschreibung und Zeichensetzung nach zusätzlichem Klick. |
| `Satzbau` | boolesch; Default `false` | Bei freien deutschen Textantworten `Satzbau=1` bereits einsetzen; prüft Grammatik/Satzbau nach zusätzlichem Klick. |
| `maxthinkingtime` | `0s`, `5s`, `10s`, `15s`, `20s`, `30s`; adaptiver Default `15s` | Im ausführlichen Quality-Profil `15s` explizit machen; `0s` deaktiviert optionalen Einzelrecheck und Thinking. Dies begrenzt nicht Ladezeit oder gesamte Prüfung. |
| `maxthinkingtokens` | `low=256`, `medium=512`, `high=768`, `ultra=1024`, `extreme=2048`; adaptiver Default `medium` | Im ausführlichen Quality-Profil `medium` explizit machen. Keine freie Tokenzahl im Makro; `extreme` nicht als Schulstandard. |

Beleg: [README.md:458–505](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/README.md#L458-L505),
[Optionsparser src/macro-options.ts:23–238](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/src/macro-options.ts#L23-L238),
[Thinking-Werte src/thinking-config.ts:1–79](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/src/thinking-config.ts#L1-L79).
Explizite `15s`/`medium` behalten diese Werte auch bei langen Antworten; fehlen
sie, werden die fehlenden Dimensionen ab 160 Wörtern adaptiv auf `30s`/`ultra`
erhöht. Der Skill setzt somit nachvollziehbare Erstellungswerte, statt diesen
Unterschied zu verschweigen.

### Kompatibilität und begleitende Optionen

- `coverage` benötigt einen Kriterienblock; ohne diese Option sind alle Kriterien
  einzeln erforderlich. Auch `coverage=1` aktiviert ausdrücklich den Quotenmodus.
- Kriterien vertragen weder `operator=...` noch vollständige Lösungsalternativen.
  Das Operatorverb darf selbstverständlich im sichtbaren Auftrag stehen.
- `assessmentengine=compact` verträgt weder Operatorprüfung noch aktives Thinking.
  `maxthinkingtime=0s` ist damit zulässig. Sprachoptionen bleiben getrennt möglich.
- `Rechtschreibung=1` oder `Satzbau=1` benötigt `feedback=1`. Entfernt man
  `feedback=1`, müssen beide Sprachoptionen mit entfernt oder auf `0` gesetzt
  werden. Für Fremdsprachen die deutsche Sprachanalyse nicht als passend annehmen.
- Native Annotation `data-solution-button="off"` gehört bei LLMQuiz dazu;
  die Lösung wird mit `solution` gesteuert. `data-llm-textarea="2"` bis `"12"`
  stellt die sichtbare Zeilenanzahl ein, meist `"6"`. Dies sind
  Quizattribute, keine Semikolonoptionen. Native Hinweise `[[?]]` stehen
  zwischen Texteingabe und LLM-Fence.
- Es gibt keine öffentliche Modellgrößen-, `temperature`-, `prompt`-,
  `weight`-, `required`-, Rechtschreib-Toleranz- oder Satzbau-Punkteoption.
  Felder der JavaScript-API `CriterionInput` sind keine Optionen des Makros.
  Insbesondere lassen Kriterienmarker keine individuellen Gewichte zu.

Beleg: [README.md:229–267, 720–726, 830–850, 1248–1258](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/README.md#L229-L267),
[src/types.ts:103–150](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/src/types.ts#L103-L150).

### Ausführlicher Standard für freie deutsche Antworten

Dieses neu verfasste Beispiel ist ein vollständiger Aufgabenausschnitt. Im
Kurskopf benötigt es den direkten Import
`https://raw.githubusercontent.com/MINT-the-GAP/lia-llm/684914a814468ddbe2fcc47f2eeea74cf62af54f/README.md`.
Kriterien, Quote und Musterlösung bei der Übernahme fachlich anpassen.

````markdown
Beschreibe fünf Merkmale eines Rechtecks: Seitenzahl, Eckenzahl, Innenwinkel sowie Länge und Lage gegenüberliegender Seiten.

<!-- data-solution-button="off" data-llm-textarea="6" -->
[[Antwort]]
[[?]] Untersuche zuerst die Ecken und danach jeweils zwei gegenüberliegende Seiten.
```text @LLMQuiz(0.55;coverage=0.80;solution=1;feedback=1;assessmentengine=quality;Rechtschreibung=1;Satzbau=1;maxthinkingtime=15s;maxthinkingtokens=medium,`Beschreibe fünf Merkmale eines Rechtecks: Seitenzahl, Eckenzahl, Innenwinkel sowie Länge und Lage gegenüberliegender Seiten.`)
<!-- lia-llm:criterion -->
Ein Rechteck hat vier Seiten.
<!-- lia-llm:criterion -->
Ein Rechteck hat vier Ecken.
<!-- lia-llm:criterion -->
Alle Innenwinkel eines Rechtecks sind rechte Winkel.
<!-- lia-llm:criterion -->
Gegenüberliegende Seiten eines Rechtecks sind gleich lang.
<!-- lia-llm:criterion -->
Gegenüberliegende Seiten eines Rechtecks sind parallel.
<!-- lia-llm:solution -->
Ein Rechteck hat vier Seiten und vier Ecken. Alle vier Innenwinkel sind rechte Winkel. Je zwei gegenüberliegende Seiten sind gleich lang und verlaufen parallel.
```
````

Hier genügen beim formativen Selbstcheck vier der fünf Aussagen:
`ceil(5 × 0.80) = 4`. Die Aufgabe verlangt weiterhin die Überarbeitung zu fünf
Merkmalen; die Bestehensquote toleriert eine fehlende Aussage. Soll jede Aussage
zwingend vorliegen, `coverage=1` wählen. `contradicted` ist unabhängig von der
Quote ein Veto. `uncertain` zählt nicht als erfüllt; könnte die Quote nur mit
unsicheren Aussagen erreicht werden, bleibt das Ergebnis neutral unbewertet.
Dies ist eine gewählte didaktische Schwelle, kein vom Template erzwungener
Standard. [README.md:643–725](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/README.md#L643-L725).

Für die ganzheitliche Operatorprüfung wird derselbe ausführliche Rahmen so
umgestellt: erster Zahlenwert `0.66`, `operator` fachlich setzen, `coverage`
entfernen und im Fence ausschließlich die vollständige Musterlösung schreiben.
Beispiel eines gültigen Aufrufs:

````markdown
```text @LLMQuiz(0.66;solution=1;feedback=1;assessmentengine=quality;operator=erklaeren;Rechtschreibung=1;Satzbau=1;maxthinkingtime=15s;maxthinkingtokens=medium,`Erkläre, warum ein nasses Handtuch beim Trocknen leichter wird.`)
Wasser verdunstet aus dem nassen Handtuch und gelangt als Wasserdampf in die Umgebungsluft. Dadurch enthält das Handtuch weniger Wasser und seine Masse nimmt ab.
```
````

### Erwartungshorizonte und Laufzeitgrenzen mitdenken

Kriterien: Der erste `<!-- lia-llm:criterion -->` ist die erste nichtleere Zeile
im Block. Ein Marker beginnt genau eine selbstständig prüfbare Aussage;
1 bis 16 nichtleere, verschiedene Kriterien. Genau ein
`<!-- lia-llm:solution -->` folgt nach allen Kriterien und leitet die
zusammenhängende Lösung ein. Der Kompatibilitätsfallback ohne Lösungsmarker
verkettet Kriterien; neue Aufgaben formulieren die Lösung ausdrücklich.
Keine zusätzlichen Kriterien nach dem Lösungsmarker.

Ganzheitliche Alternativen: alleinstehendes `<!-- lia-llm:alternative -->`
trennt höchstens acht vollständige Lösungsvarianten insgesamt. Mehrere Varianten
enthalten zusammen höchstens 8000 normalisierte Zeichen; keine leeren oder
doppelten Varianten. ODER-Semantik gilt für eine vollständige Variante, nicht
für zusammengesetzte Teilstücke. Die Parser-Aliasse `lia-llm-variant` und
`lia-llm-variante` werden für alte Dokumente erkannt; neue Aufgaben benutzen
`lia-llm:alternative`. Beleg:
[src/scoring.ts:28–195](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/src/scoring.ts#L28-L195),
[README.md:521–641](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/README.md#L521-L641).

Sprachprüfung ist ein nachgelagerter eigener Klick: bei beiden Optionen heißt
er „Sprache prüfen“. Sie ändert weder das Inhaltsurteil noch die ursprüngliche
Antwort. Fehlerstatistik und begrenzte Korrekturvorschläge sind keine garantierte
vollständige Korrektur; breitere Satzumstellungen werden nicht automatisch
angewendet. Unverfügbare Fehlerzahlen dürfen nicht als null ausgegeben werden.
Die Funktionen benötigen lokal verfügbare Quality-Modelle und entsprechende
Browserunterstützung. Ein explizites `quality` ist kein Versprechen, dass jedes
Gerät diesen Pfad ausführen kann; die Zustimmung zum Modell-Download erfolgt
in der Template-Oberfläche. Der spätere Sprachklick verwendet ein eigenes
Budget, nicht `maxthinkingtime` der Inhaltsprüfung. Die README enthält in den
allgemeinen Modellabschnitten ältere Kurzformulierungen zur impliziten
Enginewahl; für diese Trennung sind Makrocode und dedizierter Sprachabschnitt
maßgeblich. [README.md:314–341, 893–998](https://github.com/MINT-the-GAP/lia-llm/blob/684914a814468ddbe2fcc47f2eeea74cf62af54f/README.md#L893-L998).

## lia-orthography: Korrigieren, Diktat und Zeilennummern

| öffentliches Makro | Vollständige Signatur / Optionen | Mitdenken |
| --- | --- | --- |
| `@orthography` | ``@orthography(`Kommentaroptionen`,`Starttext`,`Lösung`)`` | Einzeiliges Korrekturfeld; alle drei Parameter bewusst angeben. |
| `@orthographytext` | Dieselben drei Parameter | Mehrzeiliges, vergrößerbares Feld; intern zunächst vier Zeilen, kein öffentlicher vierter Zeilenparameter. |
| `@linenumbers` | Fence ` ```markdown @linenumbers ` mit Text als Blockargument | Jede physische Quellzeile einschließlich Leerzeilen erhält genau eine Nummer; kein weiterer Optionsparameter. |
| `@diktat` | ``@diktat(`Wort oder Phrase`)`` | Stimme aus Kursnarrator; Kommaphrasen mit Backticks schützen. Mehrere Diktatlücken im selben Absatz ergeben ein gemeinsames natives Multi-Quiz. |

Die Backticks innerhalb der Signaturnotation markieren die einzelnen geschützten
Makroargumente; konkrete Aufrufe siehe Beispiel unten. Unterstrichmakros sind
intern. Öffentlich dokumentiert sind `data-solution-button` und
`doublespacehelp` im ersten Kommentarparameter; weitere native Quizoptionen nur
nach der offiziellen Grundsyntax verwenden.

In Containern bis 20 em Breite nutzt das Eingabefeld die volle Breite und der
Reset rutscht in die nächste Zeile; breitere Container zeigen beide nebeneinander.
Das gilt auch für schmale Karten auf einem breiten Bildschirm. Keine feste
Viewportbreite oder manuelle Zeilenbruch-Hülle ergänzen.

`data-solution-button="2"` ist ein sinnvoller expliziter Erstellungswert, wenn
Auflösen nach zwei Versuchen gewünscht ist. Der Parser versteht positive
Ganzzahlen als Versuchszahl, `off`/`false`/`0`/`no` als deaktiviert und ansonsten
das eingeschaltete Gate. Nutze neue gültige Angaben `on`, `off` oder eine positive
Ganzzahl; Parser-Fallbacks sind keine zusätzlichen empfohlenen Optionen.
`doublespacehelp="on"` standardmäßig einsetzen, sofern Abstände/Zeilenumbrüche
nicht Lerngegenstand sind; das trimmt Randabstände und reduziert alle
Whitespace-Folgen auf ein Leerzeichen. Ohne diese Angabe bleiben Abstände
bewertungsrelevant. `true`, `1`, `yes` sind implementierte Einschalt-Aliasse.

**Bewertungsgrenze:** Beide Korrekturmakros normalisieren außerdem NFKC,
Anführungszeichen und Groß-/Kleinschreibung. Eine Aufgabe ausschließlich zur
Groß-/Kleinschreibung lässt sich damit in diesem Stand nicht streng bewerten.
Die README-Syntax allein macht diese Einschränkung nicht deutlich.
Belege: [README.md:106–205](https://github.com/MINT-the-GAP/lia-orthography/blob/edfca9a9b3fa075a2e977fb3589209508be14bbd/README.md#L106-L205),
[src/types.ts:62–120](https://github.com/MINT-the-GAP/lia-orthography/blob/edfca9a9b3fa075a2e977fb3589209508be14bbd/src/types.ts#L62-L120),
[src/sync.ts:46–67](https://github.com/MINT-the-GAP/lia-orthography/blob/edfca9a9b3fa075a2e977fb3589209508be14bbd/src/sync.ts#L46-L67).

```markdown
Korrigiere die Schreibfehler und ergänze das fehlende Komma.

@orthography(`<!-- data-solution-button="2" doublespacehelp="on" -->`,`Ich hoffe das du morgen komst.`,`Ich hoffe, dass du morgen kommst.`)
[[?]] Prüfe das Wort nach dem Komma und die Schreibung der Verbform.
**************
Der Nebensatz wird durch „dass“ eingeleitet und mit einem Komma abgetrennt. Die Form „kommst“ enthält zwei m.
**************
```

Hinweise stehen nach dem Makro und vor der erklärenden Lösung. Die Lösung wird
nach erfolgreicher Prüfung oder Auflösen sichtbar. Bei `@linenumbers` inline
LiaScript nutzen; Tabellen, verschachtelte Listen und weitere Fences sind keine
unterstützten mehrzeiligen Blockinhalte. Keine erfundene Option `start`, `step`,
`rows`, `caseSensitive` oder `language` ergänzen.

## lia-kachel: alle vier Makros und Inhaltsregion

| API | Parameter / genaue Bedeutung |
| --- | --- |
| ``@Kachelfolge(`Dropspezifikation`)`` | Ein geschütztes Argument mit nativen `[->[(richtig)\|falsch]]`-Einheiten; richtige Quellidentitäten dürfen in beliebiger Reihenfolge liegen. |
| ``@KachelfolgeN(`Dropspezifikation`)`` | Gleiche Bewertungsregel; zunächst ein Target sichtbar, weitere beim Belegen, schließlich inertes N+1-Anzeigefeld. Keine öffentliche Anzahloption. |
| ``@KachelgruppeN(gruppenschlüssel,`Dropspezifikation`)`` | Einzeilig für Tabellenzellen; jede Zelle hat eine unabhängig fortschreitende Gruppe mit beliebiger Reihenfolge innerhalb ihrer Gruppe. |
| `@KachelgruppenCheck(gruppenschlüssel)` | Genau einmal unmittelbar auf der nächsten Quellzeile nach der Tabelle; keine Leerzeile dazwischen. |
| `<div class="Kachel"> ... </div>` | Kein Makro: native Inline-Multi-Drop-Quizze werden zielweise nach sichtbarem Inhalt geprüft; gleichlautende Quellen sind austauschbar. |

Ein Gruppenschlüssel folgt exakt `[A-Za-z][A-Za-z0-9_-]*`, steht in allen
Zellmakros und im gemeinsamen Check und ist für jedes Tabellenquiz auf der
Folie eindeutig. Keine Umlaute als vermeintlich beliebige „Buchstaben“ einsetzen.
Die Gruppen müssen alle Multi-Drop-Targets des Tabellenquiz abdecken; weitere
native Eingaben oder ungruppierte Targets gehören nicht in diese Tabelle.
Die Blockmakros `@Kachelfolge` und `@KachelfolgeN` bekommen eigene Zeilen und
werden nicht in Tabellenzellen eingesetzt. Kein zusätzlicher nativer Drop im
selben Absatz außerhalb ihres Parameters.

Pro Drop ist genau eine richtige Option geklammert; ohne Alternativen ist die
einzige Option automatisch richtig. Klammern müssen ausgeglichen sein;
Literales `|` wird als `\|` geschrieben. Optionen können Ablenker enthalten.
Bei unbekannter Anzahl sinnvolle Ablenker und `data-randomize="true"`
standardmäßig ergänzen; sonst verrät der Quellenpool die Menge.
`data-solution-button` ist weiterhin eine native Quizoption.

Die Drag-Schicht unterstützt Maus, Touch und Stift über Pointer Events, besitzt
einen Touch-Fallback und lässt ein Antippen durch eine Bewegungsschwelle von
8 px weiterhin ein Antippen bleiben. Aufgaben deshalb nicht mehr als
„nur per Touch ziehbar“ beschreiben; die native Klick-/Tippbedienung bleibt
zusätzlich erhalten.

**Satzbau:** Für eine feste Wortstellung native zielweise Drops mit
`data-randomize="true"` verwenden. `@Kachelfolge` akzeptiert jede Permutation
und darf nicht als Reihenfolgenprüfung angeboten werden. In `div.Kachel`
bleiben Groß-/Kleinschreibung und Satzzeichen relevant, während NFC und
Whitespace normalisiert werden. Ein einzelnes Drop-Target benötigt begleitenden
Fließtext, damit es als Inline-Multi-Drop gerendert wird. Bei rein bildlichen
Kacheln liefern `alt` oder `aria-label` den Vergleichsinhalt.

Belege: [README.md:120–311](https://github.com/MINT-the-GAP/lia-kachel/blob/15b84fba845e783d05d3b77c5cb1f76401146bee/README.md#L120-L311),
[src/groups.ts:15, 156–224](https://github.com/MINT-the-GAP/lia-kachel/blob/15b84fba845e783d05d3b77c5cb1f76401146bee/src/groups.ts#L156-L224),
[src/kachelfolge.ts:32–125](https://github.com/MINT-the-GAP/lia-kachel/blob/15b84fba845e783d05d3b77c5cb1f76401146bee/src/kachelfolge.ts#L32-L125).

Gestaltung ist von der Bewertung getrennt. Dokumentierte CSS-Variablen sind
`--lia-kachel-radius` (12px), `--lia-kachel-background`,
`--lia-kachel-target-min-width` (5.85rem, mit CSS-Unterstützung
`clamp(5.85rem, 14.3vw, 9.1rem)`) und `--lia-kachel-min-height` (3rem).
Die Implementierung verwendet zusätzlich `--lia-kachel-transition-duration`
(140ms), `--lia-kachel-accent` und Fallbackvariablen
`--lia-kachel-ghost-background` / `--lia-kachel-ghost-color` für die Drag-Vorschau.
Diese zusätzlichen CSS-Hooks sind implementiert, aber keine dokumentierten
Makrooptionen; keine eigenständige öffentliche Makro-API daraus erfinden.
[styles.css:9–21, 231–249](https://github.com/MINT-the-GAP/lia-kachel/blob/15b84fba845e783d05d3b77c5cb1f76401146bee/styles.css#L9-L21).

## lia-marker: alle Ziel- und Demonstrationsmakros

| API | Vollständige Namen / Parameter |
| --- | --- |
| Quizabschluss | `@TextmarkerQuiz`, ohne Argumente, innerhalb von `<div class="markerquiz">` nach den Zieltexten |
| Farbgebundene Quizziele | `@markred(Text)`, `@markblue(Text)`, `@markgreen(Text)`, `@markyellow(Text)`, `@markpink(Text)`, `@markorange(Text)` |
| Farbunabhängiges Quizziel | `@mark(Text)` akzeptiert jede Farbe |
| Vorgegebene Demonstrationsmarkierungen | `@markedred(Text)`, `@markedblue(Text)`, `@markedgreen(Text)`, `@markedyellow(Text)`, `@markedpink(Text)`, `@markedorange(Text)` |

Das ist die vollständige öffentliche Makroliste. Alle Textmakros haben ein
inhaltliches Textargument; Texte mit Kommas in Backticks schützen. Die in der
Expansion vorkommenden `@1` bis `@9` sind Weiterleitungs-/Reparaturdetails,
keine Farb-, Punkte- oder Optionsparameter. Es gibt kein öffentliches
`@marked`, keine frei wählbaren neuen Farbnamen und keinen öffentlichen
Toleranzparameter. Die Bewertungsgrenzen sind interne Konstanten
([src/quiz/eval.ts:9–14](https://github.com/MINT-the-GAP/lia-marker/blob/80fe9b1e0b07ee18242f35003bff3660d37da707/src/quiz/eval.ts#L9-L14)).

Standardmäßig eine klare Farblegende im Aufgabenwortlaut und eine erklärende
Lösung direkt nach `</div>` einsetzen. Der durch gleich lange Sternzeilen
begrenzte Lösungsblock bleibt bei fehlgeschlagenem Check verborgen und erscheint
nach Erfolg oder Auflösen. Demonstrationsmarkierungen nicht als bereits gelöste
Quizziele behandeln. öffentliche Signaturen und Lösungssyntax:
[README.md:11–27, 104–212](https://github.com/MINT-the-GAP/lia-marker/blob/80fe9b1e0b07ee18242f35003bff3660d37da707/README.md#L104-L212).

```markdown
Markiere das Subjekt rot und das Prädikat blau.

<div class="markerquiz">
@markred(Die Lerngruppe) @markblue(untersucht) heute Wasserproben.
@TextmarkerQuiz
</div>
**************
„Die Lerngruppe“ bezeichnet, wer handelt. „untersucht“ ist die finite Verbform und bildet hier das Prädikat.
**************
```

Native `data-hint-button`- und `data-solution-button`-Gates werden unterstützt;
für Layoutfälle liest die Implementierung sie auch vom Marker-Wrapper. Ihr
Parser versteht `on`/`true`/`enable`/`enabled`, `off`/`false`/`disable`/`disabled`
sowie Ganzzahlen als Versuchsschwellen (intern Betrag; `0` bedeutet hier sofort
sichtbar). Nutze die eindeutigen Formen `on`, `off` oder positive Ganzzahlen.
Dies ist nicht derselbe `0`-Fallback wie in lia-orthography. Keine erfundene
Semikolonkonfiguration an `@TextmarkerQuiz` anhängen.
[src/quiz/metadata.ts:11–32, 72–115](https://github.com/MINT-the-GAP/lia-marker/blob/80fe9b1e0b07ee18242f35003bff3660d37da707/src/quiz/metadata.ts#L11-L115).

Der Quizkommentar darf vor der Aufgabenbeschriftung oder unmittelbar vor
`<div class="markerquiz">` stehen. Native Hinweise folgen **nach** `</div>`
und vor dem Lösungsblock; diese Bindung funktioniert auch in rohen
`dynFlex`-Hüllen. Verwendet der Kommentar Timerattribute oder enthält die
Lösung lia-loot-Makros, müssen `lia-timer` beziehungsweise `lia-loot` neben
`lia-marker` direkt importiert werden. Keine solche transitive Abhängigkeit
voraussetzen. Beleg: `README.md:145–203`.

Der Import bietet außerdem freie Textmarkierung und einen Worterklärmodus in
der Oberfläche; es sind keine zusätzlichen Makros. Der Worterklärmodus fragt
Wiktionary für das ausgewählte Wort ab. Deutsch, Englisch, Spanisch, Französisch,
Russisch und Latein sowie heuristisch Tschechisch/Polnisch sind im Snapshot
beschrieben. Kein öffentliches Sprachen- oder API-Key-Makro erfinden.
[README.md:59–102](https://github.com/MINT-the-GAP/lia-marker/blob/80fe9b1e0b07ee18242f35003bff3660d37da707/README.md#L59-L102).

## Speech-Recognition-Quiz: drei öffentliche Makros

| Makro | Parameter und Verhalten |
| --- | --- |
| `@SpeechRecognition.support` | Ohne Parameter; meldet einmalig, ob `SpeechRecognition` oder `webkitSpeechRecognition` im Browser vorhanden ist. |
| `@SpeechRecognition(Sprache,Phrase)` | Nach `[[!]]`; BCP-47-Sprachtag wie `de-DE`, `en-US`, `en-GB`, `fr-FR`, `es-ES`; erwartete Phrase als zweites Argument. Bei Abweichung Wiederholungsfeedback. |
| `@SpeechRecognition.withFeedback(Sprache,Phrase)` | Identische Parameter; gibt bei Abweichung zusätzlich das tatsächlich erkannte Transkript zurück. Als Erstellungsdefault bevorzugen. |

```markdown
@SpeechRecognition.support

Sprich den Satz „Wir prüfen unsere Ergebnisse“ deutlich aus.

<!-- data-solution-button="off" -->
[[!]]
@SpeechRecognition.withFeedback(de-DE,`Wir prüfen unsere Ergebnisse`)
```

Keine öffentlichen Optionen für Confidence, Fehlertoleranz, mehrere akzeptierte
Phrasen, Daueraufnahme, Mikrofonwahl oder Aussprachepunkte. `interimResults=false`
und `continuous=false` sind im Makro festgelegt. Der Solltext wird kleingeschrieben,
einige Satzzeichen werden durch Leerzeichen ersetzt und Leerzeichenfolgen
reduziert; beim Ist-Transkript werden nur Kleinschreibung und Randabstände
normalisiert. Die README-Aussage, Satzzeichen würden ignoriert, ist deshalb
nicht symmetrisch implementiert. Keine semantische Äquivalenz oder robuste
Satzzeichenunabhängigkeit versprechen. Kommaphrasen mit Backticks schützen.

Die README enthält zeitgebundene Browser- und Lokalitätsaussagen. Aus diesem
Snapshot folgt nur der implementierte Featuretest; er beweist weder eine
aktuelle Browsermatrix noch lokale/offline Spracherkennung. Bei solchen
Nutzerfragen aktuelle offizielle Browserdokumentation gesondert prüfen.
Belege: [README.md:10–86](https://github.com/LiaTemplates/Speech-Recognition-Quiz/blob/0edc1ecdd6688af34521133000a795986203cd46/README.md#L10-L86),
[README.md:118–203](https://github.com/LiaTemplates/Speech-Recognition-Quiz/blob/0edc1ecdd6688af34521133000a795986203cd46/README.md#L118-L203).
