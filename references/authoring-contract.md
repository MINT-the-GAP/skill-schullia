# Verbindlicher SchulLia-Ausgabevertrag

Diese Referenz ist das harte Ausgabegate für neu erstellte und fachlich
überarbeitete SchulLia-Inhalte. Sie ergänzt die Syntax- und Template-Referenzen.
Ein Entwurf wird nicht ausgeliefert, solange die passende Strukturprüfung noch
Fehler oder ungeklärte Warnungen meldet.

## Profil zuerst festlegen

Wähle genau eines dieser Profile:

| Profil | Verwendung | Ausgangspunkt |
|---|---|---|
| `weekly` | vollständige Wochenaufgabe | [schullia-weekly-course-template.md](../assets/schullia-weekly-course-template.md) oder der ausdrücklich vorgegebene bestehende Kursrahmen |
| `course` | anderer vollständiger LiaScript-Kurs | [liascript-course-template.md](../assets/liascript-course-template.md) |
| `task` | einzelne Aufgabe oder einzufügender Aufgabenausschnitt | [schullia-task-fragment-template.md](../assets/schullia-task-fragment-template.md); kein zweiter Hauptkopf |

Bei einem vorhandenen Zielkurs hat dessen ausdrücklich vorgegebener Rahmen
Vorrang. Bewahre dann Hauptkopf, Einleitung und Footer wort- und zeilengleich,
sofern die Anfrage nicht gerade deren Änderung verlangt. Ergänze fehlende
Direktimporte nur im vorhandenen Hauptkopf und verschiebe bestehende Importe
nicht ohne belegte Abhängigkeit.

Bei einer neuen Wochenaufgabe ist der Wochenaufgabenrahmen kein loses Beispiel,
sondern ein Strukturvertrag. Er enthält in dieser Reihenfolge:

1. genau einen LiaScript-Hauptkopf,
2. die H1-Überschrift `Wochenaufgabe … Klasse … – Fach`,
3. Einleitung und Abgabehinweis,
4. fortlaufende H2-Aufgabenfolien,
5. `## Letzte Station: Selbsteinschätzung`,
6. `# Abgabe`, Kontrollhinweis, `@Abgabe` und `@Auswertung(F12;Tab;Time)`.

Die Zahl der Aufgaben folgt der Nutzerangabe; ohne Vorgabe verwendet die
Vorlage sechs. Entferne niemals Selbsteinschätzung oder Abgabe-Footer, nur weil
der fachliche Aufgabentext bereits vollständig ist.

## Bereinigter Standardimportvertrag

„Standardimporte“ bedeutet eine feste Basis plus direkt verwendete
Fachtemplates, nicht einen zufälligen Sammelimport und nicht das Vertrauen auf
transitive Imports.

Jede neue Wochenaufgabe importiert direkt:

```text
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-freeze-v2/main/README.md
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-mathpath/refs/heads/master/README.md
```

Damit sind Footer, `@ADetails` und `[[?]] @Explain` abgesichert. Ergänze direkt:

- `lia-timer`, wenn `data-solution-timer*` verwendet wird,
- `lia-resetter`, wenn `@resetter` verwendet wird,
- LiaTemplates/Algebrite **vor** `lia-canvas-ocr`, wenn `@canvas` oder
  `@BerechneOCR` verwendet wird,
- LiaTemplates/JSXGraph **vor** `lia-coordinate`,
- JSXGraph, `lia-coordinate`, danach `lia-pentominos`, wenn Pentomino-Makros
  verwendet werden,
- jedes weitere tatsächlich verwendete Sprach-, Kurs- oder Fachtemplate
  unmittelbar und genau einmal.

Für den automatischen parameterlosen `@Explain`-Aufruf steht `lia-freeze-v2`
vor `lia-mathpath`. Die Reihenfolge wird nicht aus historisch gewachsenen
Korpus-Headern kopiert, sondern aus den aktuellen Template-Abhängigkeiten
gebildet. Verwende in auszuliefernden Kursen die dokumentierten Branch-URLs;
verwende die synchronisierte Commit-SHA für den Nachweis der geprüften API.

## Leerzeilen sind Syntax

Verwende LF oder CRLF konsistent und keine Leerzeichen am Zeilenende. Mehr als
zwei aufeinanderfolgende Leerzeilen sind unzulässig. Für neu erzeugte Blöcke
gilt:

- genau eine Leerzeile zwischen `-->` des Hauptkopfs und der ersten H1,
- genau eine Leerzeile vor und nach Überschriften, Absätzen, Listen, Tabellen,
  Medien und voneinander unabhängigen Quizblöcken,
- **keine** Leerzeile zwischen Quizkommentar und zugehörigem Quiz,
- **keine** Leerzeile innerhalb der zusammengehörigen Quizkette aus Eingabe,
  Validator und Hinweisen,
- genau eine Leerzeile vor `@resetter` und genau eine danach,
- genau eine Leerzeile vor `@ADetails`,
- keine leeren Platzhalterzeilen zur optischen Streckung.

Ein vollständiger mathematischer Aufgabenblock sieht beispielsweise so aus:

```markdown
Berechne die Länge und gib das Ergebnis mit Einheit an.

<!-- data-hint-button=1 data-solution-button=3 -->
$s=$ [[ 1.5km ]] @canvas
@Algebrite.check(`1.5km`, units=1)
[[?]] Rechne zuerst alle Längen in dieselbe Einheit um.
[[?]] @Explain
****************
$s=1500\,\mathrm{m}=1{,}5\,\mathrm{km}$.
****************

@resetter

@ADetails(2=BE; Größen, Einheiten, Umrechnen)
```

Bei Makros mit automatisch erzeugter Musterlösung, insbesondere
`@BerechneOCR`, wird kein zweiter manueller Lösungsblock ergänzt.

## `@Explain` verbindlich anbinden

Jede neu verfasste bewertbare SchulLia-Aufgabe mit `@ADetails` erhält einen
eigenen nativen Hint `[[?]] @Explain`. Ein konkreter fachlicher Hinweis darf als
zusätzliche `[[?]]`-Zeile davor stehen. Der parameterlose Aufruf benötigt:

1. den direkten Import von `lia-freeze-v2`,
2. danach den direkten Import von `lia-mathpath`,
3. `@ADetails` im selben Aufgabenblock,
4. mindestens ein tatsächlich in `Explain.md` belegtes Thema unter den
   `@ADetails`-Tags.

Erfinde kein Explain-Thema. Gibt es keinen passenden Eintrag, melde diese Lücke
statt einen falschen Link zu versprechen. Ein manuelles `@Explain(Thema)` ist
nur zulässig, wenn das Thema in der aktuellen `Explain.md` nachgewiesen wurde.

## Algebrite, Klammern und Einheiten

Schreibe Sollterme und Sollgleichungen in Algebrite-Makros als
Backtick-Argument, sobald sie Klammern, Kommata, Semikola oder verschachtelte
Funktionsaufrufe enthalten. Für neue symbolische Aufgaben ist die
Backtick-Schreibweise generell zu bevorzugen:

```markdown
@Algebrite.check(`-(K/2)*t^(-3/2)`)
@Algebrite.check_expression(`x^2-1-2x=0`)
```

Die aktuelle Algebrite-API behandelt Einheiten so:

- `@Algebrite.check` und `@Algebrite.check_expression`: Einheiten standardmäßig
  aus; bei Größenantworten `units=1` setzen,
- `@Algebrite.check2` und `@Algebrite.check_margin`: Einheiten standardmäßig an;
  nur bei echten dimensionslosen Aufgaben begründet mit `units=0` abschalten,
- falsche oder fehlende Einheiten müssen bei einer verlangten Größe zur falschen
  Antwort führen.

Steht eine Einheit im Aufgabentext oder ist sie fachlich Teil der gesuchten
Größe, dann muss sie konsistent vorkommen:

1. im Antwortfeld **innerhalb** von `[[ … ]]`,
2. im Sollwert und gegebenenfalls in der Toleranz des Validators,
3. in jeder numerischen Zeile der Musterrechnung,
4. im abschließenden Antwortsatz.

Eine außerhalb des Eingabefelds gedruckte Einheit prüft die Lernendenantwort
nicht. Schreibe daher nicht `[[ 1.5 ]] km`, wenn `1.5km` verlangt und geprüft
werden soll. Prüfe vor der Ausgabe außerdem Dimensionen und Umrechnungsfaktoren;
eine formal lauffähige CAS-Prüfung ersetzt keine fachliche Einheitenprüfung.

## Fachlicher Schlussdurchgang

Erstelle vor dem Schreiben eine kleine Größen- und Begriffsliste aus dem
Aufgabentext: Größe, Größenzeichen, Einheit, Fachbegriff, erwartete Beziehung.
Gleiche anschließend Aufgabenwortlaut, Eingaben, Validatoren, Hinweise,
Lösungen, Diagramme, Tabellen und `@ADetails` dagegen ab. Wende zusätzlich die
verbindliche Fachsprache des Hauptskills an. Ein bloßes Suchen nach verbotenen
Wörtern reicht nicht; kontrolliere auch Aussage, Dimension, Vorzeichen,
Definitionsbereich, Rundung und Eindeutigkeit der Lösung.

## Ausgabegate

Speichere den Entwurf in einer Datei und führe aus:

```text
python scripts/validate_lia.py PFAD --profile weekly --strict
python scripts/validate_lia.py PFAD --profile course --strict
python scripts/validate_lia.py PFAD --profile task --strict
```

Bei einer Bearbeitung mit unverändertem Wochenaufgabenrahmen ergänze:

```text
python scripts/validate_lia.py NEU.md --profile weekly --reference-shell ALT.md --strict
```

Korrigiere alle Fehler und kläre jede Warnung. Übergib danach knapp den
Prüf-Witness: Profil, verwendete Vorlage beziehungsweise Referenzdatei,
geprüfte Template-Revisionen, Importabhängigkeiten, `@Explain`-Abdeckung,
Einheitenprüfung und Validator-Ergebnis.
