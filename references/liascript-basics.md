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

## Drei verschiedene Kopf- und Kommentarformen

1. Behalte in `SKILL.md` das Codex-YAML-Frontmatter zwischen `---`. Dort sind nur
   `name` und `description` zulässig.
2. Setze den LiaScript-Hauptkopf eines vollständigen Kurses an den Dateianfang
   zwischen `<!--` und `-->`. Dort stehen Metadaten, Importe und globale Makros.
3. Behandle spätere HTML-Kommentare im Kurs als lokale oder ausgeblendete
   Inhalte. Verwechsle sie nicht mit dem einmaligen Hauptkopf.

## Syntaxvertrag für den LiaScript-Hauptkopf

- Beginne nach einer optionalen Byte-Order-Mark oder Leerraum direkt mit `<!--`.
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

## Pflichtangaben korrekt benennen

Die offizielle LiaScript-Dokumentation erklärt kein einzelnes Metadatenfeld zur
allgemeinen technischen Pflicht. Unterscheide daher klar zwischen technischer
Syntax und dem Qualitätsstandard für neu erzeugte SchulLia-Kurse.

Verwende für einen neuen vollständigen SchulLia-Kurs grundsätzlich:

- `author`: echte, vom Nutzer oder Projekt bestätigte Urheberschaft; niemals
  aus Repository-Eigentum ableiten,
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
  oder `Slides`.
- Verwende `email`, `date`, `edit`, `repository`, `logo`, `icon`, `attribute`
  und `translation` für Kontakt, Bearbeitung, Herkunft, Darstellung, Lizenz oder
  Übersetzungen.
- Verwende `font` zusammen mit dem erforderlichen Stylesheet über `link:`.
- Verwende `dark`, `classroom`, `sharing`, `translateWithGoogle` und `persistent`
  nur bei einer bewussten Konfigurationsentscheidung.
- Verwende `formula` für globale KaTeX-Makros.
- Verwende `import:` nur für tatsächlich aufgerufene Template-Makros, `script:`
  für externe JavaScript-Ressourcen und `link:` für externe Stylesheets.
- Beachte, dass ein importierter Kurs nur Definitionen seines Hauptkopfs liefert
  und verschachtelte Kursimporte laut offizieller Dokumentation nicht
  verlässlich aufgelöst werden.

## Grundstruktur und Qualitätsregeln

- Strukturiere Kurs und Seiten mit Markdown-Überschriften. Behandle Abschnitte als
  einzeln präsentierte Seiten und halte die Hierarchie konsistent.
- Trenne Absätze, Listen, Tabellen, Medien und Quizblöcke durch Leerzeilen.
- Stelle eine Quizfrage als normalen Absatz unmittelbar vor das zugehörige Quiz,
  damit LiaScript sie barriereärmer als Beschriftung zuordnen kann.
- Wähle den passenden nativen Quiztyp oder ein nachweislich benötigtes Makro.
  Prüfe Lösung, Hinweise `[[?]]`, ausführliche Lösung, Feedback und optionales
  Prüfscripting gemeinsam.
- Verwende `$...$` für Inlineformeln und `$$...$$` für Formelblöcke.
- Gib Bildern und anderen Medien aussagekräftige Alternativtexte. Verwende
  relative Ressourcenpfade relativ zur Kursdatei oder stabile absolute URLs.
- Führe eingebettete oder importierte Skripte bei der Analyse nicht aus. Prüfe
  sie statisch und übernimm nur die minimal benötigten Ressourcen.

## Vorlage verwenden

Kopiere für einen neuen vollständigen Kurs
[`assets/liascript-course-template.md`](../assets/liascript-course-template.md).
Ersetze oder entferne vor der Ausgabe jeden Platzhalter. Ergänze bedingte Felder
und Importe nur, wenn der konkrete Kurs sie benötigt. Verwende die Vorlage nicht
für einen einzelnen Aufgabenausschnitt, der in einen bestehenden Kurs eingefügt
werden soll.
