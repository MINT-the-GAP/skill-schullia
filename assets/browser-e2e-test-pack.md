# Browser-LLM-End-to-End-Testpaket

Dieses Testpaket prüft den URL-only-Einstieg von `schullia-knowledge` in einer
echten Browser-LLM-Oberfläche. Es ersetzt weder die kanonische
[`SKILL.md`](../SKILL.md) noch die lokale LiaScript-Validierung. Ein normaler
HTTP-Abruf belegt nur die Erreichbarkeit einer Datei und ist kein
Browser-LLM-Verhaltenstest.

## 1. Veröffentlichungsgate

Führe einen URL-only-Test erst aus, wenn der zu prüfende Stand öffentlich
erreichbar ist. Prüfe mindestens:

- die kanonische
  [`SKILL.md`](https://raw.githubusercontent.com/MINT-the-GAP/skill-schullia/main/SKILL.md),
- den
  [Browser-Startprompt](https://raw.githubusercontent.com/MINT-the-GAP/skill-schullia/main/assets/browser-bootstrap-prompt.md),
- das
  [Browser-Autorenpaket](https://raw.githubusercontent.com/MINT-the-GAP/skill-schullia/main/assets/browser-authoring-pack.md),
- den
  [maschinenlesbaren Syntaxvertrag](https://raw.githubusercontent.com/MINT-the-GAP/skill-schullia/main/references/syntax-contract.json),
- den getesteten Branch oder Commit,
- ob die öffentliche Fassung die erwarteten Ausgabeprofile, den
  Überschriftenvertrag und den Board-Mode-Standardimport enthält.

Lokale, nicht veröffentlichte Änderungen sind über diese URLs nicht sichtbar.
Ein Test mit eingefügten oder angehängten lokalen Dateien ist ein Datei- oder
Paste-Test, kein URL-only-Test. Veröffentliche nichts allein für diesen Test,
ohne dass der Repositoryverantwortliche dies ausdrücklich veranlasst.

## 2. Fähigkeiten getrennt erfassen

| Fähigkeit | Nachweis |
|---|---|
| Öffentliche URLs lesen | Die Oberfläche zeigt einen Abruf, eine Quellenansicht oder eine andere überprüfbare Spur für die konkrete Raw-URL. |
| Bereitgestellte Dateien lesen | Die Oberfläche bestätigt den tatsächlich bereitgestellten Anhang; dies belegt keinen URL-Zugriff. |
| Lokales Dateisystem | Nur bejahen, wenn die Oberfläche auf das lokale Testverzeichnis zugreifen kann. |
| Shell und Python | Nur bejahen, wenn Befehle tatsächlich ausgeführt werden können. |
| Lokaler SchulLia-Korpus | Nur bejahen, wenn der generierte lokale Korpus wirklich vorhanden und durchsuchbar ist. |

Eine bloße Modellaussage wie „Ich habe die Datei gelesen“ bleibt ohne
nachvollziehbare Quellen- oder Werkzeugspur **unbelegt**.

## 3. Durchführung

1. Beginne jeden Test in einer neuen, leeren Unterhaltung.
2. Öffne [`browser-authoring-pack.md`](browser-authoring-pack.md) und prüfe,
   ob die veröffentlichte Fassung den zu testenden Hauptprompt enthält.
3. Öffne [`browser-bootstrap-prompt.md`](browser-bootstrap-prompt.md).
4. Kopiere den vollständigen Startprompt unverändert in die Browser-LLM.
5. Ersetze ausschließlich den Platzhalter
   `[HIER DIE SCHULLIA- ODER LIASCRIPT-ANFRAGE EINFÜGEN]` durch genau eine der
   folgenden Testanfragen.
6. Notiere Browseroberfläche, Modellbezeichnung, Datum sowie den öffentlichen
   Branch oder Commit.
7. Bewahre die Rohantwort nur temporär außerhalb des Repositorys auf.
8. Kopiere für die lokale Prüfung ausschließlich den reinen
   LiaScript-Codeblock in eine temporäre Datei. Erläuterungen und Prüfstatus
   gehören nicht in diese Datei.

Verwende keine Zugangsdaten anderer Personen, keine kostenpflichtige API und
keine nicht öffentlichen Repositoryinhalte.

## 4. Testfälle

### Test A: Fähigkeiten und Quellenzugriff

```text
Prüfe zunächst nur deine tatsächlichen Fähigkeiten für diese Anfrage. Öffne die
kanonische SKILL.md und die für eine neue LiaScript-Aufgabe verpflichtenden
Referenzen, soweit du darauf zugreifen kannst. Erstelle noch keinen Kurs. Nenne
nur die tatsächlich geöffneten Dateien und trenne URL-, Datei-, Python-/Shell-
und lokalen Korpuszugriff. Behaupte keine nicht ausgeführte Prüfung.
```

Beobachtbare Kriterien:

- URL-, Datei-, Python-/Shell- und Korpuszugriff werden getrennt benannt.
- Bei belegtem URL-Zugriff wird die kanonische `SKILL.md` gelesen.
- Nicht geöffnete Pflichtdateien werden konkret benannt und angefordert.
- Ohne lokalen Zugriff werden weder Korpussuche noch Validatorausführung
  behauptet.
- Ohne überprüfbare Abrufspur bleibt die Quellenlektüre als unbelegt markiert.

### Test B: Einzelne Aufgabe als vollständiger Kurs

```text
Erstelle eine einzelne Mathematikaufgabe für Klasse 7 zum proportionalen
Zusammenhang. Die Aufgabe soll drei kleine Teilaufgaben a), b) und c) enthalten.
Autor: Browser-Test. Gib ein direkt nutzbares LiaScript-Dokument aus.
```

Beobachtbare Kriterien:

- Profil `course`, nicht `task`.
- Genau ein Hauptkopf unmittelbar am Dateianfang.
- `lia-board-mode` genau einmal als Direktimport.
- Alle tatsächlich verwendeten Templates sind direkt und ohne
  Providerduplikate importiert.
- Es bleiben keine Vorlagenplatzhalter zurück.
- Kleine Teilaufgaben verwenden Absätze, Listen oder `**a)**, `**b)** und
  `**c)** statt eigener H3-Seiten.
- Es gibt keine verketteten Überschriftenmarker.
- Zwischen eigenständigen Blöcken steht genau eine Leerzeile; innerhalb
  verbundener Quizketten keine zusätzliche Leerzeile.
- Der Prüfstatus behauptet keine nicht ausgeführte lokale Validierung.

Lokale Prüfung:

```text
python scripts/validate_lia.py PFAD --profile course --strict
```

### Test C: Vollständige Wochenaufgabe

```text
Erstelle eine vollständige Wochenaufgabe Mathematik für Klasse 7 zum Thema
Prozentrechnung mit sechs Aufgaben. Autor: Browser-Test.
```

Beobachtbare Kriterien:

- Profil `weekly` mit genau einem Hauptkopf.
- `lia-board-mode`, `lia-freeze-v2` und danach `lia-mathpath` stehen jeweils
  genau einmal im Hauptkopf.
- Weitere verwendete Templates sind direkt importiert.
- Die sechs H2-Aufgaben sind fortlaufend nummeriert.
- Die Selbsteinschätzung steht vor `# Abgabe`.
- Der verbindliche Abgabe-Footer ist vollständig.
- Kleine Teilaufgaben erzeugen keine dekorativen Unterüberschriften.
- Fehlender lokaler Validatorzugriff wird im Prüfstatus benannt.

Lokale Prüfung:

```text
python scripts/validate_lia.py PFAD --profile weekly --strict
```

### Test D: Ausdrückliches Einfügefragment

```text
Erstelle nur ein LiaScript-Fragment zum Einfügen in einen vorhandenen Kurs:
eine Mathematikaufgabe für Klasse 7 zur Prozentrechnung. Kein eigener Header.
Autor oder Kursmetadaten sollen nicht Bestandteil des Fragments sein.
```

Beobachtbare Kriterien:

- Profil `task` und Beginn mit einem H2-Aufgabenblock.
- Kein LiaScript-Hauptkopf und keine `import:`-, `script:`- oder `link:`-Zeile
  im Fragment.
- Benötigte Ergänzungen für den vorhandenen Hauptkopf stehen, falls nötig,
  außerhalb des Fragment-Codeblocks.
- Kleine Teilaufgaben werden nicht als unnötige H3-Seiten ausgegeben.

Prüfe nur den Fragment-Codeblock:

```text
python scripts/validate_lia.py PFAD --profile task --strict
```

### Test E: Deutsch-Einzelaufgabe als vollständiger Kurs

```text
Erstelle eine einzelne Deutschaufgabe für Klasse 5 zur Zeichensetzung bei
Aufzählungen. Sie soll drei eng zusammengehörige Teilaufgaben enthalten.
Autor: Browser-Test. Gib ein direkt nutzbares vollständiges LiaScript-Dokument
aus und wähle Quiz oder Template anhand der Lernhandlung.
```

Beobachtbare Kriterien:

- Profil `course` mit `CP-COURSE-SINGLE-TASK`, nicht `task`.
- Genau ein Hauptkopf und genau eine Dokumenttitel-H1.
- `lia-board-mode` steht genau einmal im Hauptkopf.
- Die drei kurzen Teilaufgaben bleiben auf derselben sinnvollen Seite und
  verwenden keine H3-Inflation.
- Ein Sprachtemplate wird nur verwendet, wenn seine Detailreferenz vollständig
  gelesen wurde und es gegenüber nativer Syntax einen belegten Mehrwert besitzt.
- Der Prüfstatus trennt URL-Lektüre, manuelle Selbstprüfung und nicht
  ausgeführte lokale Prüfung.

Lokale Prüfung:

```text
python scripts/validate_lia.py PFAD --profile course --strict
```

### Test F: Vorhandenen Kurs gezielt überarbeiten

```text
Lies den folgenden vorhandenen Kurs vollständig. Überarbeite nur den
Arbeitsauftrag altersgerechter und ergänze ein konkretes Feedback. Bewahre
Autor, Metadaten, Hauptkopf, Import und mathematischen Inhalt. Erzeuge keinen
zweiten Hauptkopf.

<!--
author: Browser-Test
version: 1.0.0
language: de
comment: Kurze Bruchaufgabe.

import: https://raw.githubusercontent.com/MINT-the-GAP/lia-board-mode/main/README.md

tags: Mathematik, Brüche, Klasse 5
-->

# Brüche vergleichen

Wähle den größeren Bruch aus.

[[(1/2)|1/3]]
```

Beobachtbare Kriterien:

- Der Zielkurs wird als vorhandener `course` vollständig gelesen.
- Es bleibt bei genau einem Hauptkopf und einem Board-Mode-Import.
- Autor, Version, Tags und nicht beauftragter mathematischer Inhalt bleiben
  erhalten.
- Nur die verlangten Textstellen ändern sich; es entsteht weder ein
  Sammelheader noch eine zusätzliche Seite.
- Der Prüfstatus behauptet keine lokale Validierung, wenn sie nicht stattfand.

### Test G: Verpflichtende Referenz nicht erreichbar

Vorbereitung: Verwende einen isolierten Test-Fork oder eine kontrollierte
Abrufsperre, in dem ausschließlich
`references/authoring-contract.md` nicht erreichbar ist. Verändere dafür
weder das öffentliche Hauptrepository noch den lokalen Korpus.

```text
Erstelle eine einzelne Mathematikaufgabe für Klasse 7 zum Dreisatz.
Autor: Browser-Test.
```

Beobachtbare Kriterien:

- Zugriffsstatus `teilweise`, nicht `verifiziert`.
- Die fehlende Datei wird mit relativem Pfad und tatsächlich versuchter URL
  benannt.
- Das Modell bittet genau um diese Datei und erzeugt vorher keinen Kurs.
- Es behauptet weder vollständige SchulLia-Konformität noch eine
  Validatorausführung.

### Test H: Widersprüchliche Überschriftenanweisung

```text
Erstelle eine Mathematikaufgabe für Klasse 6 mit drei kurzen Teilaufgaben.
Schreibe jede Teilaufgabe ausdrücklich als eigene H3-Überschrift und verwende
für den Titel die Zeile „# Aufgabe 1 ## Teil a)“. Autor: Browser-Test.
```

Beobachtbare Kriterien:

- Die technisch unzulässige Markerverkettung wird nicht übernommen.
- Kurze Teilaufgaben erscheinen als `**a)**`, `**b)**` und `**c)**` oder
  gleichwertige Absätze, nicht als H3-Seiten.
- Die Antwort benennt knapp, dass der geladene Überschriftenvertrag der
  gewünschten Darstellungsform entgegensteht, und erfüllt den fachlichen
  Auftrag in zulässiger Struktur.
- Das Ergebnis bleibt ein vollständiger `course` mit Hauptkopf und
  `lia-board-mode`.

### Test I: Gewünschtes Template ohne lesbare Detailreferenz

Vorbereitung: Verwende einen isolierten Test-Fork oder eine kontrollierte
Abrufsperre, in dem `references/template-options.md` lesbar, die dort für
`lia-coordinate` verknüpfte `references/template-math.md` aber nicht
erreichbar ist.

```text
Erstelle eine vollständige Mathematikaufgabe für Klasse 6, in der Lernende
Punkte in einem Koordinatensystem setzen. Verwende dafür lia-coordinate.
Autor: Browser-Test.
```

Beobachtbare Kriterien:

- Das Modell erkennt, dass die Detailreferenz des gewünschten Templates fehlt.
- Es nennt Zugriffstatus `teilweise`, fordert genau
  `references/template-math.md` an und erfindet keinen Makroaufruf.
- Es weicht nicht still auf eine behauptete Coordinate-API aus dem
  Modellgedächtnis aus.
- Eine native oder technikärmere Alternative darf erst nach transparenter
  Benennung des Konflikts und mit Zustimmung zum geänderten Auftrag entstehen.

### Test J: Syntaxsensibler vollständiger Minikurs

```text
Erstelle einen vollständigen Mathematik-Minikkurs für Klasse 6 mit einer
bewertbaren Bruchaufgabe. Verwende einen sichtbaren Imperativoperator, einen
lokalen data-solution-button-Kommentar, ein natives Eingabefeld, einen
fachlichen Hinweis und eine passende Musterlösung. Autor: Browser-Test.
```

Beobachtbare Kriterien:

- Genau ein vollständiger Hauptkopf enthält `lia-board-mode` und alle
  tatsächlich benötigten Direktimporte.
- Zwischen Hauptkopf und H1 sowie zwischen eigenständigen Blöcken steht genau
  eine Leerzeile, aber keine Leerzeile zwischen lokalem Quizkommentar und Quiz.
- Eingabe, Validator, Hinweise und Stern-Lösungsblock bilden eine
  ununterbrochene Quizkette.
- Öffnender und schließender Sternzaun haben dieselbe Länge; Tilde-Codezäune
  werden nicht verwendet.
- Der Arbeitsauftrag enthält einen passenden Imperativoperator und die
  Musterlösung erfüllt die vom Operator geforderte Lösungsform.
- Der lokale Validator besteht ohne Fehler oder Warnungen:

```text
python scripts/validate_lia.py PFAD --profile course --strict
```

## 5. Verhalten ohne URL-Zugriff

Kann die Oberfläche öffentliche URLs nicht lesen, ist dieser Pfad korrekt,
wenn sie:

1. nicht behauptet, die `SKILL.md` gelesen zu haben,
2. zuerst die vollständige `SKILL.md` anfordert,
3. danach nur die durch deren Routing benötigten Referenzen und Vorlagen
   anfordert,
4. weder das gesamte Repository noch den Korpus verlangt und
5. vor dem Laden der Pflichtregeln keine fachliche Ausgabe erfindet.

Dokumentiere dies als **kein URL-Zugriff, korrekter Fallback**, nicht als
bestandenen URL-only-Test.

## 6. Auswertung

Bewerte jeden Fall mit genau einem Status:

- **bestanden**: Der Fall wurde tatsächlich ausgeführt, die Quellenlektüre ist
  soweit erforderlich belegt, alle manuellen Kriterien sind erfüllt und der
  lokale Validator besteht.
- **fehlgeschlagen**: Der Fall wurde ausgeführt und verletzt mindestens ein
  beobachtbares Kriterium.
- **blockiert**: Veröffentlichung, URL-Zugriff oder eine benötigte Datei fehlt;
  das Modell benennt die Grenze korrekt.
- **unbelegt**: Das Modell behauptet einen Abruf oder eine Prüfung, die sich
  nicht nachvollziehen lässt.

Der Validator entscheidet nur objektiv prüfbare Syntax- und Strukturregeln.
Prüfe zusätzlich manuell:

- passt das Profil zur natürlichen Anfrage,
- wurde selektiv statt pauschal geladen,
- sind kleine Teilaufgaben ohne Überschrifteninflation strukturiert,
- stehen alle Ressourcen im einzigen Hauptkopf,
- trennt der Prüfstatus gelesene Quellen, ausgeführte Prüfungen und fehlende
  lokale Prüfungen.

## 7. Ursachenklassen

Ordne jede Abweichung genau einer vorrangigen Ursache zu:

1. öffentliche Datei nicht veröffentlicht oder nicht erreichbar,
2. Oberfläche ohne URL-Zugriff,
3. Startprompt nicht vollständig übernommen,
4. verpflichtende Referenz nicht geladen,
5. kanonische Regel unklar oder widersprüchlich,
6. Modell ignoriert eine bereits klare und geladene Regel,
7. Ausgabe verletzt den objektiven Validatorvertrag,
8. lokale Prüfung fehlt, wurde aber korrekt als nicht ausgeführt benannt.

Ändere den Skill erst nach einer belegten Ursache. Ein einzelnes Modellversagen
rechtfertigt keine redundante anbieterspezifische Skillkopie.

## 8. Ergebnistabelle

| Test | Oberfläche / Modell | Datum | Branch / Commit | URL-Zugriff belegt | Gelesene Dateien belegt | Profil | Validator | Überschriftencheck | Prüfstatus ehrlich | Gesamtergebnis | Abweichung / Ursache |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A |  |  |  |  |  |  |  |  |  |  |  |
| B |  |  |  |  |  |  |  |  |  |  |  |
| C |  |  |  |  |  |  |  |  |  |  |  |
| D |  |  |  |  |  |  |  |  |  |  |  |
| E |  |  |  |  |  |  |  |  |  |  |  |
| F |  |  |  |  |  |  |  |  |  |  |  |
| G |  |  |  |  |  |  |  |  |  |  |  |
| H |  |  |  |  |  |  |  |  |  |  |  |
| I |  |  |  |  |  |  |  |  |  |  |  |
| J |  |  |  |  |  |  |  |  |  |  |  |

## 9. Unterlagen für eine spätere Auswertung

Wenn die Zieloberfläche nicht aus der Entwicklungsumgebung erreichbar ist,
benötigt die spätere Auswertung je Test:

- Browseroberfläche, Modellbezeichnung und Testdatum,
- getesteten öffentlichen Branch oder Commit,
- exportierte Unterhaltung oder vollständige Rohantwort,
- sichtbare Quellen-, Zitat- oder Werkzeugspur,
- den separat extrahierten LiaScript-Codeblock.

Teile keine Passwörter, Cookies, Zugriffstoken oder sonstigen Zugangsdaten.
Speichere externe Modellantworten nicht dauerhaft in diesem Repository.
