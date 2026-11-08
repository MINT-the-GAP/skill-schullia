# Verhaltensabnahme und Autoren-Freigabegate

Diese Referenz prüft, ob ein Agent mit dem kanonischen Skill technisch korrekte
und stiltreue SchulLia-Inhalte erzeugen kann. Sie ist ein Pflege- und
Freigabeverfahren, keine zusätzliche Laufzeitanweisung für gewöhnliche
Autorenanfragen und kein zweiter Stilführer. Die zu prüfenden Regeln bleiben im
[Ausgabevertrag](authoring-contract.md), im
[SchulLia-Hausstil](authoring-style.md), in den
[Kurskompositionsprofilen](course-composition-profiles.md), im
[Aufgabenarchetypen-Katalog](task-archetypes.md), in der
[LiaScript-Grundlage](liascript-basics.md), in den
[Quizstrukturen](quiz-structures.md) und in der
[Template-Auswahl](template-options.md) kanonisch.

Die Abnahme bewertet den installierten Skill und den URL-only-Browserpfad
getrennt. Sie bildet keine Gesamtpunktzahl und keinen summierten Score. Ein
Status darf nur aus beobachtbaren Belegen folgen.

## Statusvokabular

Für jede geprüfte Dimension und jeden Testfall ist genau einer dieser Statuswerte
zulässig:

| Status | Bedeutung |
|---|---|
| `bestanden` | Der Fall wurde tatsächlich ausgeführt; alle einschlägigen harten Gates und manuellen Kriterien sind mit nachvollziehbaren Belegen erfüllt. |
| `Warnung` | Alle harten Gates sind erfüllt, aber eine nicht freigabekritische manuelle Abweichung oder begrenzte Zusatzbeobachtung bleibt dokumentiert. |
| `fehlgeschlagen` | Der Fall wurde ausgeführt und verletzt mindestens ein hartes Gate oder ein wesentliches manuelles Kriterium. |
| `blockiert` | Eine benötigte Fähigkeit, Veröffentlichung, Datei oder ausführbare Prüfung fehlt; es liegt kein belastbares Ergebnis vor. |
| `unbelegt` | Eine behauptete Lektüre, Ausführung oder Eigenschaft lässt sich mit den vorhandenen Spuren nicht nachweisen. |

`Warnung` darf niemals ein verletztes hartes Gate verdecken. `blockiert` und
`unbelegt` sind keine Erfolge. Abweichungen werden einzeln ausgewiesen; sie
werden nicht durch andere gute Merkmale verrechnet.

## Belege und Ablagegrenze

Eine wiederholbare Abnahme bewahrt für jeden Lauf außerhalb des Repositorys in
einem temporären Verzeichnis auf:

1. die unveränderte Testanfrage und die Rollenbeschreibung,
2. die rohe Autorenausgabe sowie den extrahierten LiaScript-Inhalt,
3. Profil und vollständigen Befehl jeder tatsächlich ausgeführten Prüfung,
4. unveränderte Validatorausgaben samt Rückgabecode,
5. die unabhängige Bewertung mit Datei- und Zeilenangaben,
6. bei einem echten Browsertest Oberfläche, Modell, Datum, öffentlicher Branch
   oder Commit und sichtbare URL-/Werkzeugspuren.

Kanonische Regeln werden mit relativem Pfad und möglichst Abschnitt benannt.
Ein bloßer Modelltext „gelesen“ oder „geprüft“ ist kein Beleg. Rohantworten,
generierte Kurse, Screenshots und laufbezogene Ergebnisberichte werden nicht
als Fixtures oder dauerhafte Testdaten in dieses Repository übernommen.

## Harte Gates

Die folgende Matrix nennt Prüfdimensionen; ihre fachlichen Einzelregeln werden
nicht hier dupliziert.

| Gate | Prüffrage und maßgebliche Quelle | Mindestbeleg |
|---|---|---|
| Ausgabeprofil | Wurde `weekly`, `course` oder das ausdrücklich verlangte headerlose `task` nach dem [Ausgabevertrag](authoring-contract.md) gewählt? Bleibt bei einer gezielten Überarbeitung der vorhandene Rahmen erhalten? | Anfrage, Ausgabe und Validatorprofil |
| Hauptkopf und Metadaten | Besitzt ein vollständiges Dokument genau einen Kopf am Dateianfang und ein Fragment keinen? Sind bestätigte Metadaten bewahrt und erfundene Urheberschaft vermieden? | Datei-/Zeilenbefund und strikter Validator |
| Direktimporte | Ist `lia-board-mode` bei vollständigen Dokumenten genau einmal direkt importiert? Sind die festen `weekly`-Importe und alle verwendeten Funktionen nach dem Importvertrag direkt, geordnet und ohne Providerduplikat eingebunden? | Kopfzeilen, Verbraucherstellen und strikter Validator |
| Überschriften | Gibt es genau eine Dokumenttitel-H1; im Profil `weekly` zusätzlich den vertraglichen Hauptabschnitt `# Abgabe`? Öffnen nur echte Seiten oder substanzielle Abschnitte eine Hash-Überschrift, während kurze Teilaufgaben keine Überschrifteninflation erzeugen? | Überschriftenliste, Datei-/Zeilenbefund und Validator |
| Quizkette und Abstände | Stehen Frage, Quiz, Validator und Hinweise in der zusammengehörigen Kette und entsprechen die Leerzeilen dem Vertrag? | Datei-/Zeilenbefund und strikter Validator |
| Operator und Musterlösung | Besitzt jede neue bewertbare Aufgabe und eigenständige Teilaufgabe den sichtbaren passenden Imperativoperator und die nach dem Ausgabevertrag erforderliche Lösungsform? Bleiben ausgenommene Abschnitte, belegte Template-Lösungen und dynamische Laufzeitlösungen korrekt behandelt? | `operator.missing`, `operator.mismatch`, `solution.missing`, `solution.insufficient`, betroffene Zeilen und manuelle Fachprüfung |
| Bewertung und Fachsyntax | Sind bei bewertbaren Aufgaben `@ADetails` und `[[?]] @Explain` vollständig? Werden Einheiten im Antwortfeld, Sollwert und Lösungsweg geprüft, Algebrite-Aufrufe korrekt geschrieben und verbindliche Fachbegriffe eingehalten? | betroffene Zeilen, Validator und manuelle Fachprüfung |
| Template-API | Entspricht jedes verwendete Makro einer gelesenen öffentlichen API, ist didaktisch begründet und mit seinen direkten Abhängigkeiten eingebunden? | Auswahl-Witness, Detailreferenz/Originalquelle und Aufrufzeilen |
| Einsatzfähigkeit | Sind alle Vorlagenplatzhalter entfernt und besteht die Ausgabe den strikten Validator im passenden Profil? Bei Überarbeitung bleibt die Referenzhülle erhalten. | Validatoraufruf, Rückgabecode; gegebenenfalls `--reference-shell` |
| Prüfehrlichkeit | Behauptet die Ausgabe nur tatsächlich gelesene Quellen und ausgeführte Prüfungen? Trennt sie lokale, Browser- und manuelle Fähigkeiten? | rohe Antwort und Werkzeug-/Quellenspur |

Ein einschlägiges verletztes Gate führt zu `fehlgeschlagen`. Kann das Gate nicht
ausgeführt werden, lautet sein Status `blockiert`; wird seine Erfüllung nur
behauptet, lautet er `unbelegt`.

## Manuelle Qualitätsprüfung

Nach den harten Gates liest eine unabhängige Person oder ein unabhängiger Agent
die vollständige Ausgabe aus Lernendensicht. Sie oder er prüft mit Verweisen auf
die kanonischen Quellen:

- **Lernhandlung und Antwortform:** Operator, erwartete Leistung, Quiztyp,
  Validator, Hinweis und Lösung passen zueinander. Die manuelle Prüfung
  bestätigt insbesondere die fachliche Passung, Vollständigkeit und
  Altersangemessenheit; ein statischer Verbbefund ist keine
  Anforderungsbereichsklassifikation.
- **Aufgabenrhythmus:** Material, direkter Arbeitsauftrag, Eingabe,
  Unterstützung und Rückmeldung bilden einen verständlichen Ablauf; kurze
  Teilaufgaben bleiben zusammen.
- **Kurskomposition:** Das ausgewählte Profil, Progression, Umfang,
  Seitengliederung, Selbsteinschätzung und Abgabe entsprechen Auftrag und
  Lerngruppe.
- **SchulLia-Familienähnlichkeit:** Der Entwurf folgt Hausstil und geeigneten
  Archetypen, ohne historische Sammelimporte, Gamification oder einzelne
  Korpusbeispiele blind zu kopieren.
- **Sprache und Barrierearmut:** Arbeitsaufträge sind präzise,
  altersangemessen und respektvoll; Quizfragen stehen zugänglich vor der
  Eingabe, Medien besitzen sinnvolle Alternativtexte und Fachsprache sowie
  Einheiten bleiben konsistent.

Jede Abweichung nennt Datei und Zeile, das betroffene Kriterium, den Status und
eine Ursachenklasse. Eine bloße Geschmackspräferenz ohne kanonischen oder
didaktischen Bezug ist kein Fehler.

## Unabhängige Rollen

Ein Verhaltenslauf verwendet zwei voneinander getrennte Agenten. Beide schreiben
nur in das temporäre Laufverzeichnis und verändern keine Repositorydatei.

### Autoren-Agent

Der Autoren-Agent erhält:

- den absoluten Pfad zur kanonischen `SKILL.md`,
- die fünf unveränderten Anfragen aus dem folgenden Abschnitt,
- den Zielpfad für `L1.md` bis `L5.md`, die unveränderte
  `L5-reference.md` und einen knappen Auswahl-Witness.

Er erhält weder Sollantworten noch erwartete Fehler, Bewertungsbefunde,
Ursachenklassen oder Reparaturhinweise. Er soll der kanonischen Route selbst
folgen und darf keine Repositorydatei bearbeiten. Vor Abschluss seiner
Ausgaben liest er diese maintenance-only Abnahmereferenz nicht; der
Orchestrator stellt sie ausschließlich dem späteren Bewertungs-Agenten bereit.

### Bewertungs-Agent

Der Bewertungs-Agent beginnt erst mit abgeschlossener Autorenausgabe. Er erhält:

- die ursprünglichen fünf Anfragen und alle Autorendateien,
- diese Abnahmereferenz,
- die von ihr verknüpften kanonischen Verträge, Stil-, Profil-, Archetypen-,
  Syntax- und Template-Referenzen,
- die unveränderten lokalen Validatorprotokolle.

Er erhält weder eine beabsichtigte Bewertung noch eine Liste vermuteter Fehler
oder gewünschter Korrekturen. Er bewertet jedes Gate und jede manuelle
Dimension mit dem festen Statusvokabular, nennt Befunde als `Datei:Zeile`,
ordnet Abweichungen einer Ursachenklasse zu und schlägt keine Änderungen vor.
Sein Bericht bleibt ebenfalls außerhalb des Repositorys.

## Lokale Vorwärtsfälle L1 bis L5

Die Anfragen werden wörtlich und ohne zusätzliche Lenkung an den Autoren-Agenten
gegeben. Der angegebene Sollpfad dient erst der späteren Abnahme.

### L1 – Mathematik-Einzelaufgabe

```text
Erstelle eine eigenständig nutzbare Mathematikaufgabe für Klasse 7 zum
proportionalen Zusammenhang mit drei kurzen Teilaufgaben. Autor: Forward-Test.
```

Spätere Prüfung: Profil `course`, Kompositionsprofil
`CP-COURSE-SINGLE-TASK`; passende Archetypen werden aus der Lernhandlung
bestimmt. Validator:

```text
python scripts/validate_lia.py L1.md --profile course --strict
```

### L2 – Deutsch-Wochenaufgabe

```text
Erstelle eine vollständige Deutsch-Wochenaufgabe für Klasse 6 zu Satzgliedern
und Zeichensetzung. Autor: Forward-Test.
```

Spätere Prüfung: Profil `weekly`, Kompositionsprofil
`CP-WEEKLY-GERMAN-5-6`; die Aufgaben dürfen verschiedene geeignete
Archetypen kombinieren. Validator:

```text
python scripts/validate_lia.py L2.md --profile weekly --strict
```

### L3 – Physik-Mehr-Aufgaben-Kurs

```text
Erstelle einen mehrteiligen Physikkurs für Klasse 8 zu Masse, Gewichtskraft
und Energieumwandlung. Autor: Forward-Test.
```

Spätere Prüfung: Profil `course`; mangels eines fach- und stufenspezifischen
Profils ist `CP-FALLBACK-COURSE` zu verwenden. Fachsprache, Größen und
Einheiten werden ausdrücklich manuell geprüft. Validator:

```text
python scripts/validate_lia.py L3.md --profile course --strict
```

### L4 – ausdrücklich headerloses Fragment

```text
Erstelle ausdrücklich nur einen headerlosen LiaScript-Einfügeausschnitt für
eine Mathematikaufgabe zur Prozentrechnung. Kein eigener Header.
```

Spätere Prüfung: Profil `task`, kein Kompositionsprofil und keine Ressourcen
im Fragment. Validator:

```text
python scripts/validate_lia.py L4.md --profile task --strict
```

### L5 – gezielte Überarbeitung

```text
Lies den nachfolgend bereitgestellten kleinen Kurs vollständig. Überarbeite nur
den Arbeitsauftrag altersgerechter und ergänze einen konkreten Hinweis sowie
ein konkretes Feedback. Bewahre Hauptkopf, Autor, Version, Tags, Import,
Überschrift, Quizlösung und mathematischen Inhalt. Erzeuge keinen zweiten
Hauptkopf.

<!--
author: Forward-Test
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

Der Originaltext wird zusätzlich unverändert als `L5-reference.md` gesichert.
Spätere Prüfung: vorhandenes Profil `course`; unverlangte Änderungen werden
mit der Referenzhülle erkannt. Validator:

```text
python scripts/validate_lia.py L5.md --profile course --strict --reference-shell L5-reference.md
```

Ein Fall ist erst `bestanden`, wenn sowohl der strikte Lauf als auch die
unabhängige manuelle Prüfung bestanden sind. Der Validator ersetzt keine
Stil-, Fach- oder Lernwegprüfung.

## Browser-LLM-End-to-End-Abnahme

Für den URL-only-Pfad gilt das bestehende
[Browser-End-to-End-Testpaket](../assets/browser-e2e-test-pack.md). Ein echter
Browserlauf ist nur zulässig, wenn genau der zu prüfende Branch oder Commit
öffentlich erreichbar ist und die Browseroberfläche URL-Lektüre mit
nachvollziehbarer Spur unterstützt.

Ist der lokale Stand nicht veröffentlicht oder die Oberfläche nicht verfügbar,
lautet die Browserabnahme `blockiert`. Die Ergebnistabelle des Testpakets bleibt
in diesem Fall leer. Ein freiwilliger Paste- oder Dateitest wird ausdrücklich
als solcher beschriftet; er ist weder ein URL-only-Test noch ein Ersatz dafür
und darf kein Browser-`bestanden` begründen. Für einen Test wird nichts ohne
gesonderten Auftrag veröffentlicht.

## Ursachenklassen und Korrekturgrenze

Jede Abweichung erhält genau eine vorrangige Ursachenklasse:

1. **Veröffentlichung:** Die benötigte öffentliche Datei oder der zu prüfende
   Stand ist nicht veröffentlicht beziehungsweise nicht erreichbar.
2. **Umgebungsfähigkeit:** Die Oberfläche besitzt keinen benötigten URL-,
   Datei-, Shell-, Python- oder lokalen Korpuszugriff.
3. **Transport:** Startprompt, Anfrage oder bereitgestellte Datei wurde nicht
   vollständig übertragen.
4. **Routing/Lektüre:** Eine verpflichtende kanonische Referenz wurde trotz
   möglicher Verfügbarkeit nicht geladen.
5. **Kanonische Regel:** Eine geladene Regel ist unklar, widersprüchlich oder
   für den beobachteten Fall unvollständig.
6. **Agentenverhalten:** Der Agent ignoriert eine klare, geladene Regel oder
   trifft eine fachlich beziehungsweise didaktisch unbegründete Wahl.
7. **Technische Durchsetzung:** Die Ausgabe verletzt einen objektiven
   Validatorvertrag oder eine belegte Template-API.
8. **Prüfgrenze:** Eine lokale oder manuelle Prüfung fehlt, wurde aber korrekt
   als nicht ausgeführt ausgewiesen.

Eine Skilländerung erfolgt nur bei belegter Ursache 3, 4, 5 oder 7 und nur an
der zuständigen kanonischen Transport-, Routing-, API-, Validator- oder
Teststelle. Ursache 1 oder 2 wird durch Veröffentlichung beziehungsweise die
Umgebung gelöst. Ursache 6 wird als Modellabweichung dokumentiert und nicht
durch redundante Regeln oder Anbieterkopien kaschiert. Ursache 8 verlangt die
fehlende Prüfung, keine neue Fachregel. Korpusdateien und laufbezogene
Autorenausgaben werden dabei nicht bearbeitet.

## Getrennte Freigabeentscheidungen

### Installierter Skill

Die lokale Autorenfreigabe ist nur `freigegeben`, wenn L1 bis L5 tatsächlich
mit zwei unabhängigen Rollen ausgeführt wurden, alle einschlägigen harten Gates
`bestanden` sind, keine wesentliche manuelle Dimension `fehlgeschlagen`,
`blockiert` oder `unbelegt` ist und die vollständige Repository-Testsuite keine
durch diese Änderung verursachte Regression zeigt. Nicht freigabekritische
`Warnung`-Befunde werden einzeln genannt. Bekannte, nachweislich vorbestehende
Synchronisations- oder Umgebungsabweichungen stehen getrennt von
Verhaltensfehlern.

Andernfalls lautet die Entscheidung `nicht freigegeben`; der Bericht nennt die
konkreten Gates und Ursachen. Ein erfolgreicher Validatorlauf allein reicht
nicht.

### Browser-/URL-only-Pfad

Die Browserfreigabe ist nur `freigegeben`, wenn der exakte öffentliche Stand das
Veröffentlichungsgate erfüllt und die einschlägigen Fälle des
Browser-End-to-End-Testpakets in einer echten URL-fähigen Oberfläche mit
sichtbaren Abrufspuren ausgeführt wurden. Alle freigabekritischen Fälle müssen
`bestanden` sein; `Warnung` darf kein hartes Gate betreffen.

Ohne diese Ausführung lautet die Entscheidung `nicht freigegeben` mit
Abnahmestatus `blockiert` oder `unbelegt`. Die lokale Autorenfreigabe überträgt
sich nicht automatisch auf den Browserpfad und umgekehrt.

## Laufbericht

Der temporäre Abschlussbericht enthält:

1. getesteten Stand und Laufumgebung,
2. unveränderte Anfragen und Rollentrennung,
3. Ausgabeprofil, Kompositionsprofil, Aufgabenarchetypen und Templates je Fall,
4. Validatorbefehle, Rückgabecodes und unveränderte Befunde,
5. harte Gates und manuelle Dimensionen mit dem festen Statusvokabular,
6. Datei-/Zeilenbefunde des Bewertungs-Agenten,
7. Ursachenklassen und nur belegte kanonische Korrekturen,
8. Browserstatus samt Ausführungs- oder Blockierungsbeleg,
9. bekannte vorbestehende und neue Abweichungen getrennt,
10. die separate Freigabeentscheidung für installierten Skill und Browserpfad.

Der Bericht nennt keine Gesamtpunktzahl und wird nach der Auswertung nicht in
das Repository übernommen.
