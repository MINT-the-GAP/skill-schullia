# Verbindlicher SchulLia-Ausgabevertrag

Diese Referenz ist das harte Ausgabegate für neu erstellte und fachlich
überarbeitete SchulLia-Inhalte. Sie ergänzt die Syntax- und Template-Referenzen.
Ein Entwurf wird nicht ausgeliefert, solange die passende Strukturprüfung noch
Fehler oder ungeklärte Warnungen meldet.

Für Aufgabenrhythmus, Sprache, Rückmeldung und gestalterische
Familienähnlichkeit lies zusätzlich den
[SchulLia-Hausstil](authoring-style.md); er ergänzt dieses technische Gate und
schwächt keine seiner Mussregeln ab.

## Profil zuerst festlegen

Wähle genau eines dieser Profile:

| Profil | Verwendung | Ausgangspunkt |
|---|---|---|
| `weekly` | vollständige Wochenaufgabe | [schullia-weekly-course-template.md](../assets/schullia-weekly-course-template.md) oder der ausdrücklich vorgegebene bestehende Kursrahmen |
| `course` | anderer vollständiger LiaScript-Kurs; Standard auch für eine einzelne eigenständig nutzbare Aufgabe | [liascript-course-template.md](../assets/liascript-course-template.md) |
| `task` | ausschließlich ein ausdrücklich verlangter Einfügeausschnitt | [schullia-task-fragment-template.md](../assets/schullia-task-fragment-template.md); kein eigener Hauptkopf |

Wähle `task` nur bei einer eindeutigen Vorgabe wie „Ausschnitt“, „Fragment“,
„zum Einfügen“ oder „ohne eigenen Header“. Eine feste Aufgabenzahl von eins
reicht dafür nicht. „Erstelle eine Mathematikaufgabe“ erzeugt daher
standardmäßig einen vollständigen Ein-Aufgaben-Kurs im Profil `course`.

Bei einem vorhandenen Zielkurs hat dessen ausdrücklich vorgegebener Rahmen
Vorrang. Bewahre dann Hauptkopf, Einleitung und Footer wort- und zeilengleich,
sofern die Anfrage nicht gerade deren Änderung verlangt. Ergänze fehlende
Direktimporte nur im vorhandenen Hauptkopf und verschiebe bestehende Importe
nicht ohne belegte Abhängigkeit. Ist der Kopf ausdrücklich unveränderlich und
fehlt ein notwendiger Import, benenne diesen Konflikt; erzeuge weder heimlich
einen zweiten Kopf noch eine technisch unvollständige Ausgabe.

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

## Hauptkopfvertrag für vollständige Kurse

Allgemeine LiaScript-Syntax, SchulLia-Qualitätsstandard und Importpolitik sind
verschiedene Ebenen:

| Ebene | Verbindliche Bedeutung |
|---|---|
| Technische LiaScript-Syntax | Ein Hauptkopf ist ein HTML-Kommentar `<!-- ... -->` am Dateianfang; Metadaten verwenden `schlüssel: Wert` und Ressourcen wiederholte `import:`-, `script:`- oder `link:`-Zeilen. YAML-Frontmatter ist kein Ersatz. |
| SchulLia-Qualitätsstandard | Jeder neue vollständige Kurs enthält mindestens `author`, `version`, `language`, `comment` und `tags`. |
| Profilabhängige Standardimporte | `course` und `weekly` erhalten die feste Basis aus der nachfolgenden Importmatrix. |
| Funktionsabhängige Importe | Weitere Templates und Ressourcen werden nur für tatsächlich verwendete Makros, Attribute oder importgesteuerte Wirkungen ergänzt. |

Für jeden neuen vollständigen `course`- oder `weekly`-Kurs gilt:

- Die Datei beginnt direkt mit `<!--` und enthält genau einen Hauptkopf, der
  vor der ersten Kursüberschrift mit `-->` endet.
- `author` nennt nur bestätigte Urheberschaft. Fehlt sie, behandle sie sichtbar
  als offene Angabe und erfinde weder eine Person noch einen Namen aus dem
  Repository-Eigentum.
- Alle benötigten `import:`-, `script:`- und `link:`-Ressourcen stehen im
  Hauptkopf. Jeder Direktimport erscheint genau einmal.
- Verlasse dich nicht auf verschachtelte oder transitive Imports. Ordne direkte
  Abhängigkeiten so, wie sie in der aktuellen Template-Dokumentation belegt
  sind.
- Entferne vor der Ausgabe sämtliche Vorlagenplatzhalter.
- Nach `-->` folgt genau eine Leerzeile und anschließend die erste H1.

Ein vorhandener vollständiger Kurs behält seinen einzigen Hauptkopf. Ergänze
darin fehlende Direktimporte, sofern der Auftrag Änderungen am Kopf erlaubt,
und bewahre bereits vorhandene Imports ohne unnötige Verschiebung oder
Duplizierung.

## Überschriften öffnen Seiten, Teilaufgaben nicht

Hash-Überschriften bilden in LiaScript die Dokumenthierarchie; jeder so
gebildete Abschnitt wird getrennt präsentiert. Verwende sie deshalb nur für
einen inhaltlich sinnvollen eigenen Abschnitt beziehungsweise eine sinnvolle
eigene Seite, nicht zur bloßen optischen Hervorhebung. Für neu erzeugte oder
strukturell überarbeitete Inhalte gilt:

- Setze nach den `#`-Zeichen ein Leerzeichen und verwende pro physischer Zeile
  genau eine Überschriftenebene.
- Verkette keine Marker wie `# Aufgabe 1 ## Teil a)`. Die zweite Markerfolge
  erzeugt dort keine saubere Unterseite, sondern verunreinigt den Titel.
- Erzeuge keine Überschrift nur für eine kurze Frage, ein Eingabefeld, einen
  Hinweis, eine Lösung, eine Punkteangabe oder eine kleine Teilaufgabe.
- Stelle die Quizfrage als normalen Absatz unmittelbar vor das Quiz. Strukturiere
  kleine Teilaufgaben mit Absätzen, Listen oder fett gesetzten Kennzeichnungen
  wie `**a)**`.
- Vermeide unbegründete Ebenensprünge, leere Strukturseiten und dekorative
  Überschriften.
- Verwende keine pauschale numerische Höchstzahl. Entscheidend ist, ob der
  Inhalt eine eigenständige LiaScript-Seite oder einen sinnvollen
  Navigationseintrag rechtfertigt.

Die Profile konkretisieren diese Regel:

| Profil | Verbindliche Überschriftenstruktur |
|---|---|
| `weekly` | Bewahre die H1-Kursüberschrift, fortlaufende H2-Aufgabenfolien, `## Letzte Station: Selbsteinschätzung` und `# Abgabe`. Kleine Teilaufgaben innerhalb einer H2-Aufgabenfolie erhalten keine eigene Überschrift. |
| `course` | Verwende H1 für tatsächliche Hauptbereiche beziehungsweise den vorgesehenen Kursrahmen, H2 für sinnvolle Seiten oder Aufgaben und H3 nur für eine eigenständige Unterseite mit substanziellem Inhalt. |
| `task` | Beginne mit dem vorgesehenen H2-Aufgabenblock. Kurze Teilaufgaben darin erhalten keine H3-Überschriften. |

Geeignet für mehrere kurze Teilaufgaben auf derselben Folie:

```markdown
## Aufgabe 1: Bewegungsdiagramm

**a)** Lies die Geschwindigkeit nach fünf Sekunden ab.

[[ 12 km/h ]]

**b)** Begründe deine Antwort in einem vollständigen Satz.

[[___]]
```

Ungeeignet ist eine bloße Kette aus Aufgaben- und Teilmarkern:

```markdown
# Aufgabe 1 ## Teil a)

### a) Geschwindigkeit ablesen

### b) Antwort begründen
```

Die erste Zeile bildet keine verschachtelte Hierarchie; die kurzen H3-Zeilen
zerlegen zusammengehörige Teilfragen ohne inhaltlichen Seitenbedarf.

Eine belegte technische Abschnittsgrenze hat Vorrang vor der sparsamen
Gliederung. Insbesondere benötigen Drop-/Kachelquizze und weitere von
`lia-resetter` unterstützte Quiztypen im unveränderten LiaScript-Core getrennte
`##`-Abschnitte für einen verlässlichen Einzelreset. Verwende diese Ausnahme
nur bei einer tatsächlich eingesetzten, entsprechend dokumentierten
Quizkombination und gib jeder erforderlichen Seite einen aussagekräftigen Titel
und echten Inhalt. Ein `flex-child` ersetzt eine solche Abschnittsgrenze nicht.
Siehe [lia-resetter in der Template-Referenz](template-course.md#lia-resetter-erneutes-üben-vollständig-vorbereiten).

Die offizielle Grundlage für Hierarchie und getrennte Darstellung steht in
LiaScript/docs, `README.md`, Zeilen
[628–658](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L628-L658),
Commit `62cef07c2be1a9e0563d237c157b35945278ed6d`. Die Absatzbindung von
Quizfragen ist dort in
[Zeilen 4844–4860](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L4844-L4860)
belegt.

## Profil- und Funktionsimportvertrag

„Standardimporte“ bedeutet eine kleine profilabhängige Basis plus unmittelbar
benötigte Funktionstemplates, nicht einen Sammelimport und nicht das Vertrauen
auf transitive Imports.

| Anlass | Direkte Imports in dieser Reihenfolge |
|---|---|
| vollständiger `course` | `lia-board-mode` |
| vollständiger `weekly` | `lia-board-mode`, `lia-freeze-v2`, danach `lia-mathpath` |
| ausdrückliches `task`-Fragment | kein eigener Hauptkopf und keine eingebetteten Imports |

Verwende dafür in auszuliefernden vollständigen Kursen diese dokumentierten
Branch-URLs:

```text
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-board-mode/main/README.md
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-freeze-v2/main/README.md
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-mathpath/refs/heads/master/README.md
```

`lia-board-mode` ist der einzige Template-Import, der für jeden vollständigen
SchulLia-Kurs gilt. Sein Import aktiviert Funktionen bereits ohne sichtbaren
Makroaufruf und hat laut aktueller README keine externe Importabhängigkeit.
Setze ihn in der SchulLia-Basis vor die profil- beziehungsweise
funktionsabhängigen Imports. Der Import allein ist kein Grund, `mode:` zu
setzen oder `@autoscrolling` einzufügen.

Ergänze funktionsabhängig und jeweils direkt sowie genau einmal:

| Verwendete Funktion | Benötigter Import oder Reihenfolge |
|---|---|
| `@resetter` | `lia-resetter` |
| `data-solution-timer*` oder `data-hint-timer*` | `lia-timer` |
| `@Abgabe`, `@Auswertung`, `@ADetails` oder `@Exam` | `lia-freeze-v2` |
| `@Explain` | `lia-mathpath`; bei parameterlosem `@Explain` steht `lia-freeze-v2` wegen `@ADetails` davor |
| `@canvas` oder `@BerechneOCR` | LiaTemplates/Algebrite vor `lia-canvas-ocr` |
| Makros aus `lia-coordinate` | LiaTemplates/JSXGraph vor `lia-coordinate` |
| Pentomino-Makros | LiaTemplates/JSXGraph, danach `lia-coordinate`, danach `lia-pentominos` |
| weitere Sprach-, Fach- oder Kurstemplates | jedes tatsächlich verwendete Template unmittelbar und genau einmal; belegte Abhängigkeiten zuerst |

`lia-navigation` bleibt vom Kursumfang und Navigationsbedarf abhängig,
`lia-annotation` von geplanter Tafel- oder Zeichenarbeit. `lia-globalquiz`,
`lia-DynFlex`, `lia-timer`, `lia-resetter` und Fachtemplates sind ebenfalls
nicht universell. `lia-loot` bleibt ausschließlich Teil der nachgelagerten
Gamificationroute.

Ein `task`-Fragment bleibt selbst headerlos. Liegt der Zielkurs nicht vor,
liefere außerhalb des reinen Fragment-Codeblocks eine kurze Liste mit der
Überschrift „Benötigte Ergänzungen im vorhandenen Hauptkopf“ und nenne darin
alle für den Ausschnitt fehlenden Direktimporte. Vermische diese Liste nicht
mit dem zu validierenden Fragment und erzeuge keinen zweiten Hauptkopf.

Verwende im auszuliefernden Kurs Branch-URLs. Nenne die synchronisierte
Commit-SHA und README-Prüfsumme nur im Prüf-Witness beziehungsweise als
Quellenbeleg.

## Verbindlicher Operator- und Lösungsvertrag

Jede neu erstellte bewertbare Aufgabe enthält einen sichtbaren, fachlich
passenden Arbeitsauftrag mit mindestens einem Operator im Imperativ. Jede
eigenständige Teilaufgabe mit eigener Lernhandlung benötigt einen eigenen
Operator. Eng zusammengehörige kurze Eingaben dürfen einen gemeinsamen
Operator verwenden, wenn Wörter wie „jeweils“, „alle“ oder „die folgenden
Teilaufgaben“ seinen Geltungsbereich eindeutig machen. Einleitungen,
Materialien, Hinweise, Feedback, Lösungen, Selbsteinschätzungen und
administrative Abgabeabschnitte unterliegen dieser Pflicht nicht.

Hebe den zentralen Operator im bevorzugten Autorenformat fett hervor, etwa
`**Berechne**`, `**Begründe**` oder `**Gib** … **an**`. Die Fettschrift selbst
ist kein Operatornachweis. Erkenne und normalisiere die Form ausschließlich mit
der [Operator-Taxonomie](operator-taxonomy.md) und ihren Mustern in
[`operator-taxonomy.json`](operator-taxonomy.json). Die Taxonomie klassifiziert
keinen Anforderungsbereich. Sichtbarer Operator, vorhandene Operatorangabe,
Lernhandlung, Antwortform, Quiz und Validator dürfen sich nicht widersprechen.

Jede solche Aufgabe erhält außerdem eine zum Operator und zur Antwortform
passende Musterlösung oder eine öffentlich belegte, technisch gleichwertige
Template-Lösung. Der notwendige Umfang ist nicht für alle Aufgaben gleich:

| Operatorgruppe | Verbindliche Lösungsform |
|---|---|
| `angeben`, `nennen`, `auswählen`, `zuordnen`, `markieren` | korrekte Antwort beziehungsweise Zuordnung; knappe fachliche Rückmeldung, wenn sie zum Verständnis beiträgt |
| `berechnen`, `ermitteln`, `bestimmen`, `lösen` | nachvollziehbarer Rechen- oder Lösungsweg, Ergebnis, Antwortsatz und alle verlangten Einheiten |
| `begründen`, `erklären`, `zeigen`, `nachweisen` | vollständige Musterbegründung mit den tragenden fachlichen Beziehungen, nicht nur Behauptung oder Endergebnis |
| `beschreiben`, `darstellen`, `skizzieren`, `zeichnen`, `konstruieren` | geeignete Referenzdarstellung oder eindeutig überprüfbare Merkmale, wenn keine Textdarstellung möglich ist |
| `vergleichen`, `interpretieren`, `untersuchen` | vollständige Musterantwort mit den geforderten Merkmalen, Beziehungen oder Deutungen |
| `beurteilen`, `bewerten`, `entscheiden` | begründetes Musterurteil anhand transparenter Kriterien |
| `formulieren`, `erstellen` und offene Schreibaufgaben | altersangemessene Musterlösung oder Kriterienraster für Inhalt, Fachsprache und gegebenenfalls Satzbau und Rechtschreibung |

Aufgabe, Antwortfeld, Validator, Hinweis und Lösung verwenden dasselbe
Zahlenmaterial, dieselben Größen, Größenzeichen, Einheiten und Fachbegriffe.
Der konkrete Hinweis unterstützt nur den nächsten Bearbeitungsschritt und
bleibt klar von der vollständigen Lösung getrennt.

Erzeugt ein dokumentiertes Template nachweislich eine vollständige, für
Lernende zugängliche Lösung oder fachlich gleichwertiges Feedback, ersetzt
diese Darstellung den manuellen Sternblock. Füge dann keine redundante zweite
Lösung hinzu. Das gilt bei `@BerechneOCR` nur für belegte Aufgabentypen mit
automatisch erzeugbarer Musterlösung; Prüfbarkeit allein genügt nicht. Bei
zufällig erzeugten Aufgaben wird keine feste Lösung erfunden: Sie muss aus
denselben Laufzeitwerten berechnet werden und bedarf einer manuellen
Laufzeitprüfung. Führe Templatecode dafür nicht aus.

Bei einer gezielten Überarbeitung bleiben vorhandene Nutzerinhalte und
Lösungen unverändert, soweit weder der Auftrag noch eine notwendige fachliche
Korrektur ihre Änderung verlangt. Statisch erkennbare Formfehler werden mit
dem Validator geprüft; die fachliche Angemessenheit von Operator und Lösung
bleibt zusätzlich manuell abzunehmen.

## Leerzeilen sind Syntax

Verwende LF oder CRLF konsistent und keine Leerzeichen am Zeilenende. Mehr als
eine aufeinanderfolgende Leerzeile ist außerhalb ausdrücklich dokumentierter
Templateketten unzulässig. Für neu erzeugte Blöcke
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

Die maschinenlesbare Zuordnung von Regel-ID, Anker, Bindung, Importen,
gültigem beziehungsweise ungültigem Beispiel und statischer oder manueller
Prüfbarkeit steht in
[`syntax-contract.json`](syntax-contract.json). Diese Datei konkretisiert die
vorliegenden Regeln, ersetzt aber weder diesen Ausgabevertrag noch die
Original-README eines gewählten Templates.

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

Bei einer Bearbeitung mit unverändertem `course`- oder
`weekly`-Kursrahmen ergänze:

```text
python scripts/validate_lia.py NEU.md --profile weekly --reference-shell ALT.md --strict
python scripts/validate_lia.py NEU.md --profile course --reference-shell ALT.md --strict
```

Beim Profil `weekly` schützt der Vergleich Einleitung, Selbsteinschätzung und
Footer. Beim Profil `course` schützt er den Hauptkopf und die
Überschriftenstruktur; unverlangte Änderungen am übrigen Inhalt müssen
zusätzlich im tatsächlichen Diff geprüft werden.

Korrigiere alle Fehler und kläre jede Warnung. Übergib danach knapp den
Prüf-Witness: Profil, verwendete Vorlage beziehungsweise Referenzdatei,
geprüfte Template-Revisionen, Importabhängigkeiten, `@Explain`-Abdeckung,
Einheitenprüfung und Validator-Ergebnis.
