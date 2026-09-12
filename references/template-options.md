# Template-Auswahl und vollständige Optionsprofile

## Standard: passende Funktionen sind bereits enthalten

Lies diese Einsatzmatrix bei jeder Kurserstellung einmal vollständig. Lade
danach nur die passenden Detailreferenzen und Originalquellen. Wähle aus dem
gesamten Spektrum, auch wenn der Prompt keine Makronamen nennt. Erstelle eine
fachlich sinnvolle, reichhaltige erste Fassung mit ausdrücklich konfigurierten
Zusatzoptionen: Der Nutzer soll passende Funktionen entfernen können, statt
sie erst nachfordern zu müssen.

Für jedes gewählte Template prüfe öffentliche Makros, Varianten, Argumente,
optionale Parameter, Defaults, native Quizattribute und Abhängigkeiten.
Berücksichtige zu einer Aufgabenfamilie auch Rückmeldung, Lösung, Wiederholung,
Darstellung und Eingabehilfen. Verwende dafür das belegte Autorenformat;
interne Helfer oder beliebige JavaScript-Konfiguration sind keine öffentliche
Makro-API. Ein fehlendes öffentliches Optionsargument wird nicht erfunden.

Schreibe geeignete Optionen im tatsächlichen Aufruf oder lokalen Kommentar
aus und gruppiere sie lesbar. Kennzeichne abgeleitete Schwellen und Zeiten als
didaktische Wahl, nicht als garantierte technische Defaults. Liefere
einsatzfähige Aufgaben, keine Sammlung auskommentierter Alternativen.
Entfernen darf andere Aufgaben nicht beschädigen: benötigte gemeinsame Importe
bleiben bestehen, bis ihr letzter Verbraucher entfernt ist.

Explizite Einschränkungen wie „nur native Quizze“, „ohne Sprachprüfung“,
„kurz“ oder eine feste Aufgabenzahl gehen vor. Aktiviere keine widersprüchlichen
Optionen: Ein statisches Koordinatenbild ist kein interaktives Quiz; ein
Satzbaucheck passt zu ganzen Sätzen, nicht zu einer gesuchten Einzelzahl.
Die nachgelagerte lia-loot-Route mit ihrem Klärungsgate bleibt separat.

## Einsatzmatrix aller geprüften Templates

Stand: 23 Templates im synchronisierten Quellenumfang, einschließlich der fünf
konfigurierten LiaTemplates. Das ist keine Behauptung über sämtliche weltweit
verfügbaren LiaTemplates. Revisionen und README-Prüfsummen stehen im
[Prüfkatalog](template-catalog.json). Die Detailreferenzen enthalten die
öffentlichen Makros und Optionsfamilien mit Quellenzeilen.

| Lernziel oder Kursbedarf | Template und mitzuprüfende Möglichkeiten | Details |
|---|---|---|
| Offene Antworten erklären, begründen, vergleichen | `lia-llm`: `@LLMQuiz`, Kriterien/Coverage, Inhalt, Rechtschreibung, Satzbau, Feedback, Lösung, Engine und Denkbudget | [Sprache](template-language.md) |
| Wörter korrigieren, Texte überarbeiten, Diktat | `lia-orthography`: Wort-/Textvarianten, Hilfen und native Quizoptionen; Groß-/Kleinschreibungsgrenze beachten | [Sprache](template-language.md) |
| Wörter, Sätze, Begriffe und Ergebnisse zuordnen | `lia-kachel`: native Drop-Ziele, Kachelbeschriftung/Antwort, `@Kachelfolge`; Reihenfolge ausdrücklich prüfen | [Sprache](template-language.md) |
| Textstellen untersuchen, Kategorien markieren | `lia-marker`: globaler Marker, `@TextmarkerQuiz`, alle sechs Farben, beliebige Farbe, Demonstrationsmarkierung, Lösung und native Gates | [Sprache](template-language.md) |
| Aussprache, Vorlesen, gesprochene Antworten | `Speech-Recognition-Quiz`: `@SpeechRecognition`, Sprache, Sollphrase und Transkriptfeedback | [Sprache](template-language.md) |
| Handschrift, Rechenwege, Skizzen und OCR | `lia-canvas-ocr`: Zeichenflächen, OCR, Rechenwegprüfung und Zeilenrückmeldung | [Mathematik](template-math.md) |
| Koordinaten, Punkte, Formen, Konstruktionen | `lia-coordinate`: System, Zeichenwerkzeuge, Quizvarianten, Toleranzen, Feedback und kombinierte Prüfungen | [Mathematik](template-math.md) |
| Brüche, Flächenanteile, Strichlisten | `lia-Mathe`: Kreis-/Rechteckquiz, Anzeigevarianten, `@Strichliste` und `@liaQuizC` | [Mathematik](template-math.md) |
| Erklärungen und Begriffsunterstützung | `lia-mathpath`: Explain-Themen, Glossar, Tooltips und Kontext aus `@ADetails` | [Mathematik](template-math.md) |
| Flächen legen, Polyominos, Hundertertafel | `lia-pentominos`: freie Darstellung und Quiz, Steintypen, Zahlen und Transformationen | [Mathematik](template-math.md) |
| Symbolische Mathematik und gleichwertige Terme | `Algebrite`: CAS-Auswertung, Gleichwertigkeitsprüfung, Toleranzen, Intervalle und Gleichungen | [Mathematik](template-math.md) |
| Dynamische Geometrie und mathematische Visualisierung | `JSXGraph`: `@JSX.*`, Board-Konfiguration und Einbettung | [Mathematik](template-math.md) |
| Nebeneinander angeordnete Material-/Aufgabenflächen | `lia-DynFlex`: Container, Größen und Interaktionsvarianten | [Kurs](template-course.md) |
| Schreiben und Markieren in Präsentationen | `lia-annotation`: importgesteuerte Zeichenleiste und Konfiguration | [Kurs](template-course.md) |
| Tafelansicht und Lesbarkeit | `lia-board-mode`: breite Ansicht, Schriftgröße und Anzeigeoptionen | [Kurs](template-course.md) |
| Navigation in längeren Kursen | `lia-navigation`: Inhaltsverzeichnis, Lesezeichen und aufgeklappte Ebenen | [Kurs](template-course.md) |
| Einheitliche Quizvorgaben | `lia-globalquiz`: `@global`, lokale Ausnahmen; Parserattribute weiterhin lokal schreiben | [Kurs](template-course.md) |
| Wiederholen und Rücksetzen einzelner Aufgaben | `lia-resetter`: Resetvarianten, Rekonstruktion und Grenzen pro Abschnitt | [Kurs](template-course.md) |
| Zeitgesteuerte Lösungsfreigabe | `lia-timer`: Dauer, Start und Freigabeverhalten | [Kurs](template-course.md) |
| Arbeitsstand sichern und abgeben | `lia-freeze-v2`: `@Abgabe`, Snapshot und Freeze-Einstellungen | [Kurs](template-course.md) |
| Noten und Musik hören | `ABCjs`: ABC-Notation, Darstellung und Wiedergabe | [Kurs](template-course.md) |
| Mikrocontroller und Schaltungen simulieren | `AVR8js`: Code-/Schaltungsblöcke, Simulator und Abhängigkeiten | [Kurs](template-course.md) |
| Kurs nachträglich gamifizieren | `lia-loot`: vollständiger vorhandener Optionskatalog; zunächst fertiger Basiskurs, dann Gamification-Route | [Loot](lia-loot.md), [Katalog](lia-loot-options.json) |

## Offene Antworten: LLMQuiz von Anfang an vollständig konfigurieren

Für eine in ganzen Sätzen zu beantwortende, mehrteilige Inhaltsaufgabe
verwende als bevorzugtes Autorenprofil Kriterienbewertung mit ausdrücklich
gesetztem `coverage`, `solution=1`, `feedback=1`, `assessmentengine=quality`,
`Rechtschreibung=1` und `Satzbau=1`. Plane eine semantische Schwelle sowie
`maxthinkingtime` und `maxthinkingtokens` passend zur Lerngruppe. Die
ausführliche geprüfte Syntax und ein vollständiges Beispiel stehen in
[template-language.md](template-language.md). Kopiere nicht bloß `@LLMQuiz`.

Lege unabhängige Inhaltskriterien an, damit Coverage tatsächlich einzelne
geforderte Aspekte abdeckt. Setze die Musterlösung hinter
`<!-- lia-llm:solution -->` und Kriterien jeweils hinter
`<!-- lia-llm:criterion -->`. Coverage ist nur in diesem Kriterienformat
wirksam; kombiniere es nicht mit `operator` oder alternativen Musterlösungen.
Für eine echte Operatorbewertung wähle das dort beschriebene Operatorprofil.

Die Sprachprüfungen sind zusätzliche Rückmeldungen nach einem separaten
Lernendenklick. Sie verändern die Inhaltsbewertung nicht. Versprich keine
automatische fachliche Korrektheit oder verbindliche Gesamtnote. Bei
Einzelwörtern oder Stichpunkten passe das Profil an die erwartete Antwortform
an; bei ganzen Sätzen sind Rechtschreibung und Satzbau bereits aktiviert.

## Import- und Kombinationsprüfung

Prüfe den einmaligen Hauptkopf jedes gewählten Templates: öffentliche Makros,
importgesteuerte Effekte sowie benötigte Bibliotheken und Styles. Füge
benötigte direkte Template-Imports hinzu; verlasse dich nicht auf transitive
Imports. Behalte vorhandene Importreihenfolge bei und verwende keine
Bibliotheken oder Varianten ohne passenden Aufruf bzw. benötigten Effekt.

Vergleiche native Attribute, lokale Optionen und globale Vorgaben nach der
jeweiligen Prioritätsregel. Kontrolliere insbesondere LLM-Kriterien gegenüber
Operatorprofil, Kachel-Reihenfolge, Coordinate-IDs und Static-Modus, globale
Quizattribute gegenüber Parserattributen sowie Reset-/Freeze-/Timer-Effekte.
Übertrage eine Quizoption nicht ohne Beleg auf alle Templates.

## Neue Templates und Änderungen bemerken

Der lesende Prüfer entdeckt alle synchronisierten `MINT-the-GAP/lia-*`-Repos
und die Quellen der Sammlung `template-reference`. Er meldet auch bisher
unkatalogisierte Templates. Er schreibt nichts in den Korpus:

```text
python scripts/template_inventory.py --check
python scripts/template_inventory.py --source lia-llm --json
```

Die Detailausgabe liefert README-Pfad, Commit, Definitionszeilen und
Dokumentationsabschnitte. Headerdefinitionen enthalten auch interne Helfer
und Onload-Konfiguration; sie sind keine öffentliche API-Liste. Autorensyntax
entscheidet sich anhand der kuratierten Referenz und der gelesenen README.

Führe `--check` nach einer Synchronisierung und vor Template-Generierung aus.
Bei neuer Revision, geänderter README oder fehlender Referenz lies die
betroffenen Originalquellen und berücksichtige ihre zusätzlichen Optionen.
Arbeite danach innerhalb der beauftragten Aufgabe weiter; ein Prüfhinweis
ist keine neue Zustimmungsfrage. Behaupte bis zur Nachprüfung keine aktuelle
Vollständigkeit. Bei Skillpflege aktualisiere die betroffene Detailreferenz
und erst anschließend ihren Eintrag in `template-catalog.json`.

Rückgabecode `1` bedeutet nachzuprüfende Abdeckung, `2` fehlende oder ungültige
Eingaben. Die Prüfung verifiziert Revisionen, README-Hashes und Referenzdateien;
sie ersetzt weder die semantische API-Prüfung noch einen Browserlauf.
