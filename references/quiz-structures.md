# LiaScript-Quizstrukturen

## Erkennungsstufen

1. Lies zuerst Originalsyntax und lokale Provenienz.
2. Unterscheide Live-Inhalte, Header-/Makrodefinitionen, Dokumentationsbeispiele
   und dynamisch erzeugte Zeichenketten.
3. Verwende die Parserklassifikation als Suchhilfe, nicht als Ersatz für das
   Lesen des belegten Quellausschnitts.

## Standardstrukturen

| Indexwert | Typische Syntax | Bedeutung |
|---|---|---|
| `text_input` | `[[ Lösung ]]` | Texteingabe oder Lücke |
| `text_input_placeholder` | `[[___]]` | leere Texteingabe |
| `inline_selection` | `[[(richtig)|falsch]]` | Auswahl innerhalb einer Zeile |
| `single_choice` | `[(X)]` / `[( )]` | Radioauswahl |
| `multiple_choice` | `[[X]]` / `[[ ]]` | Mehrfachauswahl |
| `drag_drop` | `[->[…]]` | Zuordnung, Sortierung oder Kachel |
| `matrix` | Quizmarker in Tabellenzeilen | Matrix aus Auswahlfeldern |
| `generic_script` | `[[!]]` | generisches, skriptvalidiertes Quiz |
| `hint` | `[[?]]` | Hinweisblock |

Bewahre Rohsyntax, mehrere Lücken pro Zeile, mehrere korrekte Optionen und
Unterstriche unverändert. Interpretiere ein `|` kontextabhängig; bei Kacheln
kann es Beschriftung und Antwort trennen.

## SchulLia-Makros und Erweiterungen

Prüfe bei der Aufgabenauswahl die vollständige Einsatzmatrix in
[template-options.md](template-options.md). Sie verteilt alle geprüften
Templates auf nach Bedarf zu lesende Detailreferenzen:

- [Sprache](template-language.md): `@LLMQuiz` einschließlich Kriterien,
  `coverage`, `Rechtschreibung`, `Satzbau` und Denkbudget; Orthographie,
  Diktat, Kacheln, Textmarker und `@SpeechRecognition`.
- [Mathematik](template-math.md): Canvas/OCR, Koordinaten und Konstruktionen,
  Bruchdarstellungen, Strichlisten, Rechenwege, Pentominos, Algebrite und JSXGraph.
- [Kurs](template-course.md): DynFlex, Annotation, Board-Mode, Navigation,
  GlobalQuiz, Resetter, Timer, Freeze/Abgabe, ABCjs und AVR8js.
- [Gamification](lia-loot.md): öffentliche lia-loot-Makros und ihr
  [Optionskatalog](lia-loot-options.json), nach der gesonderten Gamification-Route.

Setze passende Zusatzoptionen bereits in der ersten Fassung ausdrücklich.
Unterscheide technische Defaults und das reichhaltigere Autorenprofil des
Skills. Beachte insbesondere: Coverage benötigt ein LLM-Kriterienformat;
`@Kachelfolge` allein prüft keine Reihenfolge; globale DOM-Quizattribute
ersetzen nicht alle nativen Parserkommentare.

Zähle ein durch ein Makro intern erzeugtes verstecktes Standardquiz nicht
doppelt als authored Quiz. Lies bei komplexen Makroargumenten die vollständige
gepinnt gespeicherte README.

## Dynamische Aufgaben

Kennzeichne Dateien mit `Math.random`, generierten `LIASCRIPT:`-Strings oder
skriptbasierten Validatoren als dynamisch. Analysiere Quelltext statisch und
führe ihn niemals aus. Behaupte keine konkrete Lösung, wenn sie erst zur
Laufzeit entsteht.

## Bekannte Grenzen des MVP-Parsers

Der Index erkennt häufige Oberflächenformen. Verschachtelte Backticks,
JavaScript-Template-Strings, Makroexpansionen, Matrixköpfe und fehlerhafte
Header können zusätzliche manuelle Quellprüfung erfordern. Beachte dafür die
`parse_warnings` eines Dokuments.
