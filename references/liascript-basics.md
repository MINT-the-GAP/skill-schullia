# LiaScript-Grundlagen und Dokumentkopf

## Quellenrang

Verwende die synchronisierte
[offizielle LiaScript-Dokumentation](https://raw.githubusercontent.com/liaScript/docs/master/README.md)
als maßgebliche Quelle für die LiaScript-Grundsyntax. Verwende anschließend:

1. MINT-the-GAP-Originaldateien für projektspezifische SchulLia-Konventionen,
2. die README des konkret verwendeten LiaTemplates für dessen Makro-API,
3. die Operator-Taxonomie für sprachliche Operatorerkennung.

Löse einen Widerspruch nicht durch Mehrheitsentscheidung im Korpus. Bevorzuge
bei Grundsyntax die aktuelle offizielle Dokumentation, bei Template-Aufrufen die
zugehörige Template-Dokumentation und bei lokalen Metadatenregeln die
ausdrückliche Vorgabe des Ziel-Repositories.

## Grundsyntax auf einen Blick

Die folgende Autorenreferenz beschränkt sich auf die Grundformen, die in
SchulLia-Kursen regelmäßig benötigt werden. Überschriften und Leerzeilen haben
dabei strukturelle Bedeutung; sie sind keine bloße Darstellungskonvention.

| Zweck | Autorenform | SchulLia-Regel |
|---|---|---|
| Überschrift | `# Hauptbereich`, `## Seite`, `### Unterseite` | Nach den `#`-Zeichen steht ein Leerzeichen. Jede Hash-Überschrift eröffnet eine Hierarchieebene und in LiaScript einen getrennt präsentierten Abschnitt. Kleine Teilaufgaben erhalten keine eigene Überschrift. |
| Absatz und Blocktrennung | Text, Leerzeile, nächster Text | Trenne Absätze, Listen, Tabellen, Medien und andere unabhängige Blöcke durch genau die Leerzeilen aus dem [Ausgabevertrag](authoring-contract.md#leerzeilen-sind-syntax). |
| Hervorhebung | `**fett**`, `*kursiv*` | Verwende `**a)**` oder `**Teil a)**` als knappe Teilkennzeichnung innerhalb derselben Aufgabenfolie. |
| Ungeordnete Liste | `- Eintrag` | Verwende pro Ebene einheitliche Marker und rücke Unterlisten mit Leerzeichen ein. |
| Geordnete Liste | `1. Eintrag` | LiaScript bewahrt die ausdrücklich geschriebenen Nummern; nummeriere deshalb bewusst und konsistent. |
| Link | `[Linktext](https://example.org)` | Verwende aussagekräftigen Linktext und stabile relative oder absolute Ziele. |
| Bild | `![Alternativtext](pfad/bild.png)` | Der Alternativtext bleibt nie leer. Relative Pfade beziehen sich auf die Kursdatei. |
| Blockzitat | `> Zitierter oder hervorgehobener Text` | Verwende Blockzitate für tatsächlich zitierte oder klar abgesetzte Inhalte, nicht als Ersatz für jede Teilüberschrift. |
| Tabelle | Kopfzeile, Trennzeile aus Bindestrichen, Datenzeilen | Halte die Spaltenzahl konsistent; Doppelpunkte in der Trennzeile steuern die Ausrichtung. |
| Inlinecode | einfache Backticks, etwa `@resetter` | Kennzeichne technische Namen, Makros und kurze Codeausdrücke, nicht gewöhnliche Fachbegriffe. |
| Codeblock | mindestens drei Backticks mit optionaler Sprache | Schließe den Block mit derselben Zahl von Backticks. Tilden-Fences gehören nicht zum belegten LiaScript-Format. |
| Mathematik | `$...$` inline, `$$...$$` als Block | Innerhalb einer Mathematikumgebung wird kein weiteres Markdown oder HTML verschachtelt. |
| Lokaler LiaScript-Kommentar | etwa `<!-- style=... -->` | Ein gewöhnlicher HTML-Kommentar nach dem Hauptkopf kann Parameter für den folgenden Block tragen und ist kein zweiter Dokumentkopf. |
| Ignorierte Autorennotiz | `<!--- Notiz --->` | Mindestens drei Bindestriche kennzeichnen einen vom LiaScript-Parser ignorierten Kommentar. Verwende diese Form nicht für Metadaten oder lokale Parameter. |

Eine minimale Tabelle enthält immer Kopf-, Trenn- und Datenzeile:

```markdown
| Begriff | Bedeutung |
|---|---|
| Masse | physikalische Größe in Kilogramm |
```

Die Frage eines Quiz steht als normaler Absatz unmittelbar vor der Eingabe,
damit LiaScript beide barriereärmer verknüpfen kann. Die nativen Quizformen und
Makrofamilien stehen in [quiz-structures.md](quiz-structures.md); kopiere sie
nicht aus allgemeinen Markdown-Beispielen.

Geprüfter Stand der offiziellen Quelle:
LiaScript/docs, `README.md`, Commit
`62cef07c2be1a9e0563d237c157b35945278ed6d`:

- [Zeilen 569–606](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L569-L606)
  (Dokumentkopf und mehrzeilige Metadaten),
- [Zeilen 628–658](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L628-L658)
  (Hash-Hierarchie und getrennte Abschnitte),
- [Zeilen 742–776](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L742-L776)
  (Blocktrennung und Hervorhebung),
- [Zeilen 911–937](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L911-L937)
  und [1099–1129](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L1099-L1129)
  (Links, Bilder und Alternativtexte),
- [Zeilen 1347–1471](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L1347-L1471),
  [1592–1615](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L1592-L1615)
  und [1799–1817](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L1799-L1817)
  (Listen, Blockzitate und Tabellen),
- [Zeilen 2174–2222](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L2174-L2222)
  (Codeblöcke) sowie
  [2978–3049](https://github.com/LiaScript/docs/blob/62cef07c2be1a9e0563d237c157b35945278ed6d/README.md#L2978-L3049)
  (ignorierte Kommentare und Mathematik).

## Drei verschiedene Kopf- und Kommentarformen

1. Behalte in `SKILL.md` das Agent-Skills-YAML-Frontmatter zwischen `---`. Dort sind nur
   `name` und `description` zulässig.
2. Setze den LiaScript-Hauptkopf eines vollständigen Kurses an den Dateianfang
   zwischen `<!--` und `-->`. Dort stehen Metadaten, Importe und globale Makros.
3. Behandle spätere HTML-Kommentare im Kurs als lokale oder ausgeblendete
   Inhalte. Verwechsle sie nicht mit dem einmaligen Hauptkopf.

## Syntaxvertrag für den LiaScript-Hauptkopf

- Beginne ein neues vollständiges Dokument direkt am Dateianfang mit `<!--`.
- Verwende genau einen LiaScript-Hauptkopf.
- Schließe den Hauptkopf mit `-->`, bevor die erste Kursüberschrift beginnt.
- Schreibe einzeilige Angaben als `schlüssel: Wert`.
- Rücke jede Fortsetzungszeile eines mehrzeiligen Werts ein.
- Wiederhole `import:`, `script:` und `link:` für mehrere Ressourcen.
- Trenne mehrere Namen in `author:` gemäß offizieller Dokumentation mit
  Semikolons.
- Definiere globale Blockmakros wie `@onload` oder `@style` vollständig innerhalb
  des Hauptkopfs und schließe sie jeweils mit `@end`.
- Verwende kein YAML-Frontmatter `---` als Ersatz für den LiaScript-Hauptkopf.
- Erzeuge beim Ergänzen einer Aufgabe in einen vorhandenen Kurs keinen zweiten
  Hauptkopf.
- Setze alle benötigten Ressourcen in den Hauptkopf, importiere jedes verwendete
  Template direkt und genau einmal und verlasse dich nicht auf transitive
  Template-Imports.
- Lasse nach `-->` genau eine Leerzeile und beginne danach mit der ersten H1.

## Pflichtangaben korrekt benennen

Die offizielle LiaScript-Dokumentation erklärt kein einzelnes Metadatenfeld zur
allgemeinen technischen Pflicht. Unterscheide daher klar zwischen technischer
Syntax und dem Qualitätsstandard für neu erzeugte SchulLia-Kurse.

Verwende für einen neuen vollständigen SchulLia-Kurs grundsätzlich:

- `author`: echte, vom Nutzer oder Projekt bestätigte Urheberschaft; niemals
  aus Repository-Eigentum ableiten; fehlende Urheberschaft als offene Angabe
  behandeln und keinen Namen erfinden,
- `comment`: kurze und präzise Kursbeschreibung,
- `language`: Sprache der Oberfläche und typografischer Regeln, gewöhnlich `de`,
- `version`: semantische Version `major.minor.patch`,
- `tags`: SchulLia-Projektkonvention für Auffindbarkeit und Einordnung, nicht als
  allgemeine LiaScript-Pflicht darstellen.

Setze `version: 0.0.1` für einen neuen Entwurf. Verwende für einen veröffentlichten
Kurs mit Quizzes oder ausführbarem Code, dessen Zustand dauerhaft gespeichert
werden soll, eine Major-Version ab `1`. Erhöhe:

- `patch` bei Korrekturen und kleinen statischen Änderungen,
- `minor` bei inhaltlichen Ergänzungen ohne Umordnung vorhandener Zustände,
- `major` bei Strukturänderungen, insbesondere beim Verschieben von Quizzes oder
  Code, weil gespeicherte Zustände an der Dokumentstruktur hängen.

## Optionale und bedingte Angaben

- Verwende `narrator` nur bei geplanter Sprachausgabe; ohne Angabe existiert ein
  englischer Fallback.
- Verwende `mode` nur bei gewünschtem Startmodus: `Textbook`, `Presentation`
  oder `Slides`. Der Standardimport von `lia-board-mode` allein verlangt keine
  Änderung dieses Felds.
- Verwende `email`, `date`, `edit`, `repository`, `logo`, `icon`, `attribute`
  und `translation` für Kontakt, Bearbeitung, Herkunft, Darstellung, Lizenz oder
  Übersetzungen.
- Verwende `font` zusammen mit dem erforderlichen Stylesheet über `link:`.
- Verwende `dark`, `classroom`, `sharing`, `translateWithGoogle` und `persistent`
  nur bei einer bewussten Konfigurationsentscheidung.
- Verwende `formula` für globale KaTeX-Makros.
- Verwende `import:` für aufgerufene Template-Makros oder benötigte
  importgesteuerte Funktionen wie Navigation und Annotation, `script:`
  für externe JavaScript-Ressourcen und `link:` für externe Stylesheets.
- Beachte, dass ein importierter Kurs nur Definitionen seines Hauptkopfs liefert
  und verschachtelte Kursimporte laut offizieller Dokumentation nicht
  verlässlich aufgelöst werden.

## Grundstruktur und Qualitätsregeln

- Beachte in allen Fächern die [Fachsprachregeln des Hauptskills](../SKILL.md#verbindliche-fachsprache)
  zu Energieumwandlung, Masse/Gewichtskraft und „Kilometer pro Stunde“.
- Strukturiere Kurs und Seiten mit Markdown-Überschriften. Behandle Abschnitte als
  einzeln präsentierte Seiten und halte die Hierarchie konsistent.
- Behandle Leerzeilen als Syntax und wende den exakten
  [SchulLia-Ausgabevertrag](authoring-contract.md#leerzeilen-sind-syntax) an:
  genau eine Leerzeile zwischen unabhängigen Blöcken, keine innerhalb der
  zusammengehörigen Kette aus Quiz, Validator und `[[?]]`-Hinweisen sowie je
  eine vor und nach `@resetter` und eine vor `@ADetails`.
- Stelle eine Quizfrage als normalen Absatz unmittelbar vor das zugehörige Quiz,
  damit LiaScript sie barriereärmer als Beschriftung zuordnen kann.
- Wähle den passenden nativen Quiztyp oder ein nachweislich benötigtes Makro.
  Prüfe Lösung, Hinweise `[[?]]`, ausführliche Lösung, Feedback und optionales
  Prüfscripting gemeinsam. Nutze [template-options.md](template-options.md)
  für die vollständige Template-Auswahl und ihre passenden Optionsprofile.
- Verwende `$...$` für mathematische Ausdrücke im Fließtext und `$$...$$` für
  abgesetzte mathematische Blöcke. Die Darstellung unterscheidet nicht zwischen
  Term und Gleichung; benenne den Inhalt gemäß der
  [verbindlichen Fachsprache](../SKILL.md#verbindliche-fachsprache).
- Gib Bildern und anderen Medien aussagekräftige Alternativtexte. Verwende
  relative Ressourcenpfade relativ zur Kursdatei oder stabile absolute URLs.
- Führe eingebettete oder importierte Skripte bei der Analyse nicht aus. Prüfe
  sie statisch und übernimm nur die minimal benötigten Ressourcen.

## Vorlage und Ausgabeprofil verwenden

Wähle das Profil vor dem Schreiben und kopiere den passenden Ausgangspunkt:

- `weekly`: [`schullia-weekly-course-template.md`](../assets/schullia-weekly-course-template.md),
- `course`: [`liascript-course-template.md`](../assets/liascript-course-template.md);
  dieses Profil gilt auch für eine einzelne eigenständig nutzbare Aufgabe,
- `task`: [`schullia-task-fragment-template.md`](../assets/schullia-task-fragment-template.md);
  dieses Profil gilt ausschließlich für einen ausdrücklich verlangten
  Einfügeausschnitt.

Ohne eine eindeutige Formulierung wie „Fragment“, „zum Einfügen“ oder „ohne
eigenen Header“ entsteht ein vollständiges Dokument; eine bloße Aufgabenzahl
von eins ändert das nicht. `course` und `weekly` enthalten genau einen
Hauptkopf, den Standardimport von `lia-board-mode` sowie alle weiteren
profil- und funktionsabhängigen Direktimporte aus dem
[Importvertrag](authoring-contract.md#profil--und-funktionsimportvertrag).
Ersetze oder entferne vor der Ausgabe jeden Platzhalter. Ein bestehender
Kursrahmen hat Vorrang und behält seinen einzigen Kopf; ein ausdrückliches
`task`-Fragment bleibt headerlos. Prüfe das Ergebnis mit dem zum Profil
gehörenden Aufruf aus dem [Ausgabegate](authoring-contract.md#ausgabegate).
