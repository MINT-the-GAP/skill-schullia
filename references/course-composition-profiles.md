# SchulLia-Kurskompositionsprofile

Diese Referenz unterstützt die Zusammenstellung vollständiger, nicht
gamifizierter SchulLia-Kurse. Sie liegt zwischen dem
[Hausstil](authoring-style.md) und den
[Aufgabenarchetypen](task-archetypes.md): Zuerst wird das Ausgabeprofil nach
dem [Ausgabevertrag](authoring-contract.md) festgelegt, dann ein passendes
Kompositionsprofil gewählt, anschließend wird für jede Lernhandlung ein
Archetyp bestimmt. Quizsyntax, Templates und Optionen folgen erst danach.

Die Profile sind Entscheidungshilfen, keine Stundenentwürfe und keine
Quotenvorgaben. Eine beobachtete Aufgabenzahl, Templatehäufigkeit oder
Timerangabe wird nicht allein durch ihr Vorkommen zum Autorenstandard. Der
Nutzerauftrag und Lernziel haben bei Umfang und Schwerpunkt Vorrang; technische
Mussregeln des Ausgabevertrags bleiben unverändert.

## Evidenzbasis, Filter und Lesart

Die Auswertung ist auf diese lokalen Quellrevisionen gepinnt:

- `MINT-the-GAP/Aufgabensammlung`, Commit
  `c9ac1585a0545a54a185de885c272da3e4aacbef`;
- `MINT-the-GAP/Wochenaufgabe`, Commit
  `03e72a48a5ccfc46d91ea6770d54dfc9cec05efb`.

Für Wochenkurse wurde das Pfadmuster
`Klasse/Fach/LiaKlasse_Woche.md` verwendet. Ein Kurs zählt nur, wenn er
mindestens eine reguläre H2-Aufgabenstation, die Selbsteinschätzung und die
H1-Abgabe besitzt sowie erkannte Aufgabeninhalte enthält. Dateien mit
`contains_dynamic_random_generation`, unvollständige Rahmen, Platzhalter ohne
Aufgabenblöcke und Sonderpfade wurden ausgeschlossen. Von den regulär benannten
Kandidaten blieben 93 vollständige Kurse: 45 Mathematikkurse der Klassen 5–6,
42 Deutschkurse der Klassen 5–6 und sechs Mathematikkurse der Klassen 9 und 11.
Weitere 19 Dateien hatten keinen vollständigen Wochenrahmen, 123 keine
erkannten Aufgabenblöcke.

Für vollständige Ein-Aufgaben-Kurse der Aufgabensammlung wurden reguläre
`.../Aufgabe_NNNN.md`-Pfade mit Hauptkopf, genau einer H1, keiner tieferen
Hash-Überschrift, mindestens einem Aufgabenblock und ohne dynamische Erzeugung
verwendet. Die Population umfasst 1.220 Kurse. Aus derselben Pfadfamilie wurden
zwölf dynamische Dateien, elf Dateien ohne Aufgabenblock und eine Datei mit
abweichender Seitenstruktur ausgeschlossen. `Aufgabe_9999.md`, README-,
Import-, Test-, Dummy- und Repetitoriumsdateien gehören nicht zur Population.

Gamification wurde nicht als fachliche Komposition ausgewertet. Gezählt wurden
bei Wochenkursen nur H2-Titel nach `Aufgabe N`; Loot-Makros, Spielressourcen,
Portale, Geheimfolien, spielbedingte Zusatzseiten und Spieltexte begründen
weder Stationen noch Progression oder Templatewahl. Parserzahlen zu
Aufgabenblöcken, Quizknoten und Makros bleiben statische Näherungen. Manuell
geprüfte Progression wird ausdrücklich davon getrennt.

Die Regelklassen bedeuten:

- **Beobachtete Korpuswerte:** commitgebundene statische Befunde; keine Norm.
- **Manuell geprüftes Gestaltungsmerkmal:** Befund aus den unten genannten
  Originalausschnitten.
- **Bevorzugter Autorenstandard:** Ausgangspunkt für neue Inhalte, sofern
  Nutzerauftrag, Lernziel und Lerngruppe keine passendere Variante verlangen.
- **Akzeptable Variante:** begründete Abweichung innerhalb des Vertrags.
- **Technische Mussregel:** unverändert aus dem Ausgabevertrag; sie kann durch
  ein Profil nicht gelockert werden.

Quartile wurden linear aus den geordneten Kurswerten bestimmt. Besonders bei
kleinen Populationen sind sie nur Orientierung. „Aufgabenblock“ bezeichnet
einen Parserbefund, „bewerteter Teilblock“ einen authored `@ADetails`-Aufruf;
beides ist nicht identisch mit einer H2-Station.

## Übersichtsmatrix

| Profil-ID | Ausgabeprofil | Fach / Stufe | typischer beobachteter Umfang | bevorzugte Progression | prägende Archetypen | Belegstärke | wichtigste Variationsgrenze |
|---|---|---|---|---|---|---|---|
| `CP-WEEKLY-MATH-5-6` | `weekly` | Mathematik, 5–6 | sechs H2-Stationen; beobachtet 6–7 | Routine und Darstellung → Anwendung → begründeter Transfer | `AR-MULTIPART-FLEX`, `AR-NATIVE-CHECK`, `AR-CAS-CALC` | stark, 45 Kurse | Aufgabenzahl und Teilblockdichte folgen dem Auftrag |
| `CP-WEEKLY-GERMAN-5-6` | `weekly` | Deutsch, 5–6 | sechs H2-Stationen | Wechsel aus Lesen, Untersuchen, Korrigieren, Schreiben und Reflexion | `AR-ORTHOGRAPHY`, `AR-TEXT-MARK`, `AR-NATIVE-CHECK` | stark, 42 Kurse | keine künstliche Pflicht zu jeder Sprachtemplatefamilie |
| `CP-WEEKLY-MATH-9-11` | `weekly` | Mathematik, belegt für 9 und 11 | median sieben H2-Stationen; beobachtet 6–7 | Verfahren → Vernetzung/Modellierung → Transfer/Beurteilung | `AR-CAS-CALC`, `AR-MULTIPART-FLEX`, `AR-NATIVE-CHECK` | mittel, sechs Kurse | Klasse 10 fehlt; Dichte nicht schematisch übertragen |
| `CP-COURSE-SINGLE-TASK` | `course` | fachübergreifend; Bestand überwiegend Mathematik | eine Inhaltsseite, median ein erkannter Aufgabenblock | Material → fokussierter Auftrag → Antwort → Rückmeldung | lernzielabhängig; häufig `AR-NATIVE-CHECK`, `AR-MULTIPART-FLEX`, `AR-CAS-CALC` | stark strukturell, 1.220 Kurse | keine Wochenstruktur und keine künstliche Kursverlängerung |
| `CP-FALLBACK-COURSE` | `weekly` oder `course` | ohne belastbares Fach-/Stufenprofil | allein aus Auftrag und Lernziel | manuell begründete Folge | einzeln auszuwählen | keine eigene Korpusnorm | keine unbelegte Fach- oder Stufennorm behaupten |

## `CP-WEEKLY-MATH-5-6` — Mathematikwochenkurs Klassen 5–6

**Ausgabeprofil:** `weekly`

**Fach-/Stufengeltung:** Mathematik, Klassen 5 und 6

**Belegstärke:** stark; 45 vollständige Vergleichskurse, davon 34 aus Klasse 5
und elf aus Klasse 6

Typische Situation ist eine Wochenaufgabe, die mehrere bereits eingeführte
Themen wiederholt und mindestens eine Darstellung, Anwendung oder offenere
Übertragung einschließt. Das Profil ist kein Lehrgang für ein einziges neues
Verfahren.

### Auswahl- und Ausschlussbedingungen

Wähle dieses Profil für einen vollständigen Mathematik-Wochenkurs der Klassen
5 oder 6. Verwende es nicht für ein `task`-Fragment, einen einzelnen
eigenständigen Auftrag ohne Wochenrahmen, höhere Klassenstufen oder eine
thematisch geschlossene Unterrichtssequenz, deren Aufbau ausdrücklich anders
vorgegeben ist. Bei nur einer Aufgabe gilt `CP-COURSE-SINGLE-TASK`.

### Evidenz und Regelklasse

**Beobachtete Korpuswerte:** Die 45 Kurse besitzen sechs fachliche
H2-Stationen im Median und in den Quartilen; die Spannweite beträgt 6–7. Kein
Kurs der Population verwendet eine H3. Erkannte Aufgabenblöcke liegen bei
4–77, mit Median 14 und Interquartilsbereich 5–36. Bewertete Teilblöcke liegen
bei 0–60, mit Median 21 und Interquartilsbereich 12–38. Diese breiten Spannen
zeigen, dass eine H2-Station mehrere kurze Teilhandlungen bündeln kann und der
Parserbefund keine Sollzahl ist.

In allen 45 Kursen treten native Antwortformen und mehrteilige Strukturen auf;
33 enthalten CAS-geprüfte Rechnungen, elf Toleranzaufgaben, zehn
Koordinatenhandlungen, zehn visuelle Mathematik und neun offene Begründungen.
Das belegt Möglichkeiten, keine Templatequote. Historische Timerwerte,
Sammelimporte und fehlende Explain-Hints sind keine Autorenstandards.

**Manuell geprüftes Gestaltungsmerkmal:** Die Originale wechseln zwischen
kurzen Routinen, Darstellungen, Größen- oder Geometrieaufgaben und einer
späteren Anwendung oder Erklärung. Die Reihenfolge ist häufig spiralförmig und
nicht stets ein linearer Schwierigkeitsanstieg über alle Themen hinweg.

**Bevorzugter Autorenstandard:** Plane sechs fachliche Stationen nur dann als
Ausgangspunkt, wenn der Nutzer keine Zahl nennt. Beginne zugänglich, erhöhe
innerhalb der Stationen die Selbstständigkeit und platziere mindestens eine
Anwendung, Darstellung oder Begründung nach vorbereitenden Routinen. Die
konkrete Aufgabenzahl des Nutzerauftrags hat Vorrang.

**Technische Mussregel:** Der vollständige Wochenrahmen, die
Selbsteinschätzung, die Abgabe und alle Header-, Import-, Explain- und
Leerzeilenregeln stammen aus dem Ausgabevertrag.

### Kursskelett

| Bestandteil | Status | Funktion |
|---|---|---|
| Kursstart und Abgabehinweis | erforderlich | knapper Zweck, Bedien- und tatsächlicher Übermittlungsweg |
| zugängliche Wiederholungsstation | empfohlen | Vorwissen aktivieren und Eingabeform etablieren |
| zwei bis vier Kernübungsstationen | empfohlen | Verfahren, Fachsprache, Darstellung oder Größenbezug sichern |
| Anwendung oder vernetzte Station | empfohlen | bekannte Verfahren in Material oder Sachzusammenhang nutzen |
| offene Erklärung oder Transfer | bedingt | nur bei passendem Lernziel, häufig eher gegen Ende |
| Selbsteinschätzung und Abgabe | erforderlich | fester Wochenabschluss |
| Spiel-, Geheim- oder Belohnungsseiten | normalerweise unnötig | ausschließlich nachgelagerte Gamificationroute |

Geeignete Grundfolge: Kursstart → zugängliche Routine → Darstellung oder
Größenbezug → weitere Kernübung → Anwendung/Vernetzung → Transfer oder offene
Erklärung → Selbsteinschätzung → Abgabe. Bei einer gemischten Wiederholungswoche
darf die Themenfolge spiralförmig sein; innerhalb jeder Station muss der
Lernweg dennoch nachvollziehbar ansteigen.

### Umfang und Dichte

- **Beobachtet:** meist sechs H2-Stationen, keine H3; mehrere kurze Teilblöcke
  innerhalb einer Station sind üblich.
- **Empfohlener Ausgangswert:** eine klar benannte H2-Seite pro fachlicher
  Station; zwei bis vier kurze, eng verwandte Teilhandlungen sind häufig gut
  handhabbar, aber keine Quote.
- **Kurz:** drei bis vier fachliche Stationen bei ausdrücklich kleinerem
  Umfang; fester Wochenabschluss bleibt erhalten.
- **Standard:** fünf bis sechs Stationen mit Wechsel aus Routine,
  Darstellung/Anwendung und einem anspruchsvolleren Abschluss.
- **Erweitert:** sechs bis sieben Stationen oder zusätzliche Teilblöcke nur bei
  entsprechendem Nutzerauftrag und tragfähiger Bearbeitungslast.

Schätze keine Bearbeitungszeit aus den historischen Timern. Trenne längere
Material- oder Transferaufgaben durch kürzere, fachlich sinnvolle
Bearbeitungsphasen. DynFlex ist für kompakte parallele Teilaufgaben geeignet;
abhängige Rechenschritte bleiben linear.

### Aufgabenarchetypen und Antwortformen

- **Prägend:** `AR-MULTIPART-FLEX` bündelt kurze verwandte Rechnungen;
  `AR-NATIVE-CHECK` prüft Auswahl, Zuordnung oder Diagnose;
  `AR-CAS-CALC` prüft mathematisch gleichwertige Ergebnisse.
- **Geeignet ergänzend:** `AR-UNIT` für bewertete Größenangaben,
  `AR-ESTIMATE-TOLERANCE` für fachlich begründete Näherungen,
  `AR-COORDINATE` und `AR-VISUAL-MATH` für Darstellungen sowie
  `AR-OPEN-REASON` für eine echte Erklärung oder Begründung.
- **Selten/bedingt:** `AR-ASSIGN-ORDER` nur bei einer sinnvollen Relation oder
  Reihenfolge; Sprach- und Markierarchetypen nur bei mathematisch relevanter
  Textarbeit, nicht zur Dekoration.

Wechsle Antwortformen wegen der Lernhandlung: beispielsweise native Diagnose
→ CAS-geprüfte Rechnung → visuelle/koordinative Darstellung → Anwendung →
Begründung. Eine technikärmere Alternative ist stets möglich: statische
Darstellung plus natives Quiz, lineare Teilaufgaben statt DynFlex oder
Freitext mit sichtbarer Rubrik statt LLMQuiz.

### Progression und Belastung

Trenne Rechenweg, Darstellung, Anwendung und Begründung. Eine richtige Zahl
weist keinen geforderten Rechenweg nach. Beginne eine Station mit einer
zugänglichen Teilhandlung und erhöhe dann Zahlraum, Abstraktion oder
Transfergrad. Stelle nicht mehrere lange CAS-Rechnungen, interaktive
Konstruktionen oder offene Texte ohne entlastenden Wechsel hintereinander.
Offene Aufgaben stehen bevorzugt nach den fachlichen Bausteinen, auf die sie
sich beziehen.

### Hinweise, Lösungen und Bewertung

Ein konkreter Hint nennt den nächsten fachlichen Schritt. Eine Musterlösung
zeigt bei Rechen-, Darstellungs- und Begründungszielen den tragenden Weg, nicht
nur das Ergebnis. BE und Themen folgen dem tatsächlich bewerteten Teilblock.
Jeder neue bewertbare Block mit `@ADetails` erfüllt den aktuellen
Explain-Vertrag; das historische Fehlen von `@Explain` ist keine Ausnahme.
Offene Antworten erhalten Erwartungshorizont oder Kriterien und eine
technikärmere Rubrikvariante.

### Layout und Seitengliederung

Fachliche Stationen sind H2-Seiten. Kurze Teilaufgaben bleiben als `**a)**`,
`**b)**` und `**c)**` auf derselben Seite. DynFlex eignet sich für
nebeneinander sinnvolle, kurze Aufgaben oder Material plus Auftrag; längere
Sachtexte, Herleitungen und voneinander abhängige Schritte bleiben linear.
Bilder, Diagramme und Boards erhalten zugängliche Alternativen und genügend
mobile Breite. H3 wird nicht allein für eine Teilfrage, Lösung oder BE gesetzt.

### Template- und Importfolgen

Der `weekly`-Header folgt dem Ausgabevertrag mit `lia-board-mode`,
`lia-freeze-v2` und danach `lia-mathpath`. Weitere direkte Imports entstehen
erst aus den gewählten Archetypen: etwa Algebrite, DynFlex, Coordinate/JSXGraph,
lia-Mathe, lia-pentominos oder lia-llm. Das Profil reproduziert keinen
historischen Sammelheader. Für den Basiskurs gilt ausdrücklich: kein
Gamification-Import und keine Loot-Makros.

### Varianten

- **Kurz:** drei bis vier Stationen, je eine zentrale Lernhandlung, native
  Antwortformen bevorzugt.
- **Standard:** fünf bis sechs Stationen mit Routine, Darstellung, Anwendung
  und begründetem Abschluss.
- **Erweitert:** zusätzliche Vernetzung oder Transferstation, nicht bloß mehr
  gleichartige Rechnungen.
- **Technikärmer:** native Eingaben/Auswahl, statische Grafiken, lineares Layout
  und sichtbare Rubrik statt komplexer Widgets oder LLM.
- **Schwächere Lerngruppe:** kleinere Zahlräume, stärker gestufte Hints,
  Beispiel vor Transfer und weniger gleichzeitige Darstellungen.
- **Stärkere Lerngruppe:** frühere Vernetzung, offenere Modellwahl und
  Begründung mehrerer Lösungswege bei unverändertem Vertrag.

### Grenzen und Anti-Patterns

Keine starre Übernahme von sechs Stationen, keine feste Archetypenquote, keine
künstliche Templatevielfalt und keine Ableitung einer Bearbeitungszeit aus
Timern. Vermeide mehrere nahezu identische Aufgaben ohne Progression,
aufeinanderfolgende technisch schwere Widgets, H3-Seiten für kurze Teilfragen,
Einheiten außerhalb der bewerteten Eingabe sowie Selbsteinschätzung ohne Bezug
zum tatsächlichen Kurs. Gamification ist kein fachliches Kursskelett.

### Kuratierte Vergleichskurse

Alle Links verwenden Commit
`03e72a48a5ccfc46d91ea6770d54dfc9cec05efb`.

| Original | Kursstart und Gliederung | ausgewählte Stationen | Selbsteinschätzung / Abschluss | Beleg und Grenze |
|---|---|---|---|---|
| [`5/Mathematik/Lia5_03.md`](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_03.md#L43-L60) | H1 Z. 43; sechs Aufgaben ab Z. 141 | Koordinaten Z. 141–190, visuelle Brüche/Polyominos und Einheiten in den folgenden Stationen | Z. 1298–1327 | belegt Darstellungswechsel und thematische Reflexion; Loot-Zeilen und historische Fachsprache nicht übernehmen; keine Parserwarnung |
| [`5/Mathematik/Lia5_09.md`](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_09.md#L40-L60) | H1 Z. 40; sechs Aufgaben Z. 111–1237 | Grundrechenarten Z. 111–155; offene Termerklärung Z. 1166–1210 | Z. 1238–1257 | belegt Routine → Anwendung/Erklärung; Timer, Loot und fehlende Explain-Hints älterer Blöcke nicht übernehmen; keine Parserwarnung |
| [`6/Mathematik/Lia6_06.md`](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/6/Mathematik/Lia6_06.md#L39-L55) | H1 Z. 39; sechs Aufgaben Z. 108–1229 | Bruchdarstellung Z. 108–150; Zahlenfolgen Z. 1087–1125 | Z. 1230–1249 | belegt visuelle und symbolische Lernhandlungen auf getrennten Stationen; Gamification ausblenden; keine Parserwarnung |

## `CP-WEEKLY-GERMAN-5-6` — Deutschwochenkurs Klassen 5–6

**Ausgabeprofil:** `weekly`

**Fach-/Stufengeltung:** Deutsch, Klassen 5 und 6

**Belegstärke:** stark; 42 vollständige Vergleichskurse, davon 33 aus Klasse 5
und neun aus Klasse 6

Typische Situation ist eine gemischte Wochenaufgabe mit mehreren sprachlichen
Lernhandlungen. Die Familienähnlichkeit entsteht durch den Wechsel aus
Aufnahme, Untersuchung, Veränderung und eigener Formulierung, nicht durch die
Pflicht, jedes Sprachtemplate zu verwenden.

### Auswahl- und Ausschlussbedingungen

Wähle dieses Profil für vollständige Deutsch-Wochenkurse der Klassen 5 oder 6.
Verwende es nicht für eine reine Lektüresequenz, einen einzelnen Diktat- oder
Grammatikauftrag, höhere Klassenstufen oder ein `task`-Fragment. Ist nur eine
eigenständige Aufgabe verlangt, gilt `CP-COURSE-SINGLE-TASK`.

### Evidenz und Regelklasse

**Beobachtete Korpuswerte:** Alle 42 Kurse besitzen sechs fachliche
H2-Stationen; H3 kommt nicht vor. Erkannte Aufgabenblöcke liegen bei 3–20, mit
Median 5 und Interquartilsbereich 5–10. Bewertete Teilblöcke liegen bei 0–60,
mit Median 25,5 und Interquartilsbereich 12,2–38,8. Diese unterschiedlichen
Parsergranularitäten sind keine Vorgabe für Teilaufgabenzahlen.

Native Antwortformen erscheinen in 41 Kursen, Orthografie in 33,
Textmarkierung in 26, Zuordnung/Ordnung in 15 und offene Begründung in sieben.
Die Häufigkeiten zeigen eine fachtypische Bandbreite, aber keine Pflichtquote.

**Manuell geprüftes Gestaltungsmerkmal:** Die Originale verbinden etwa
Leseverstehen mit Wahr/Falsch-Entscheidungen, Korrekturen direkt am Text,
Markierungen im sprachlichen Kontext, Diktat, Zuordnung sowie eine offene
Erklärungsfrage. Längere Lesetexte stehen linear; kurze Satz- oder
Wortübungen werden häufiger kompakt gruppiert.

**Bevorzugter Autorenstandard:** Plane einen Wechsel aus mindestens zwei
unterschiedlichen Lernhandlungen, wenn der Auftrag mehrere Aufgaben verlangt.
Eine plausible Folge ist Lesen/Aufnehmen → sprachliches Merkmal erkennen →
korrigieren oder verändern → anwenden/schreiben → erklären/reflektieren.
Wähle nur die Lernhandlungen, die Thema und Auftrag wirklich tragen.

**Technische Mussregel:** Wochenrahmen, Header, direkte Importe,
Selbsteinschätzung, Abgabe, Explain-Bindung und Überschriftenvertrag bleiben
unverändert verbindlich.

### Kursskelett

| Bestandteil | Status | Funktion |
|---|---|---|
| Kursstart und Abgabehinweis | erforderlich | Ziel und tatsächlicher Abgabeweg |
| kurze Aktivierung oder Diagnose | empfohlen | Vorwissen zu Wort, Satz oder Text sichtbar machen |
| Lese-/Hörmaterial | bedingt | nur wenn es die folgende Lernhandlung trägt |
| zwei bis vier Sprachübungsstationen | empfohlen | erkennen, markieren, zuordnen, korrigieren oder schreiben |
| Anwendung oder offene Erklärung | empfohlen | Regel oder Textbeleg in eigenen Worten nutzen |
| Selbsteinschätzung und Abgabe | erforderlich | fester Wochenabschluss |
| Spielseiten und Belohnungstexte | normalerweise unnötig | getrennte Gamificationroute |

Geeignete Grundfolge: Kursstart → Aufnahme/Diagnose → Untersuchen →
Korrigieren/Verändern → Anwenden/Schreiben → Erklären oder begründetes
Leseverstehen → Selbsteinschätzung → Abgabe. Die Folge darf thematisch
angepasst werden; ein Diktat muss beispielsweise nicht zwingend am Anfang
stehen.

### Umfang und Dichte

- **Beobachtet:** sechs H2-Stationen, keine H3; kurze Sätze und Einzelwörter
  häufig in mehreren Teilblöcken, Lesetexte als längere lineare Station.
- **Empfohlener Ausgangswert:** fünf bis sechs Stationen, wenn der Nutzer keine
  Zahl nennt; pro Station eine erkennbare Hauptlernhandlung.
- **Kurz:** drei bis vier Stationen mit einem Material und zwei bis drei klaren
  Bearbeitungsformen.
- **Standard:** fünf bis sechs Stationen mit Wechsel von rezeptiver,
  analytischer und produktiver Arbeit.
- **Erweitert:** zusätzlicher Transfer, Schreibauftrag oder Vergleich, nicht
  bloß mehr Sätze desselben Fehlertyps.

Teile lange Texte nicht künstlich auf mehrere Seiten, wenn dieselbe
Arbeitsgrundlage gebraucht wird. Bündele kurze Korrekturen oder Markierungen,
aber vermeide eine unübersichtliche Zahl gleichzeitig sichtbarer Sätze.

### Aufgabenarchetypen und Antwortformen

- **Prägend:** `AR-ORTHOGRAPHY` für Korrektur und Diktat,
  `AR-TEXT-MARK` für Textbelege und Kategorien sowie `AR-NATIVE-CHECK` für
  Auswahl, Matrix und kurze eindeutige Eingaben.
- **Geeignet ergänzend:** `AR-ASSIGN-ORDER` für grammatische Beziehungen,
  `AR-OPEN-REASON` für Erklärung, Vergleich oder Beurteilung und
  `AR-MULTIPART-FLEX` für kurze verwandte Satz- oder Wortübungen.
- **Selten/bedingt:** mathematische Archetypen nur bei einem echten
  fächerverbindenden Lernziel, nicht als technische Abwechslung.

Ein sinnvoller Antwortformwechsel folgt den Lernhandlungen: Text lesen →
native Entscheidung → Textstellen markieren → Schreibweise korrigieren →
eigene Erklärung. Technikärmer sind native Lücken, Auswahlmatrizen, sichtbare
Korrekturschlüssel und Freitext mit Rubrik. Eine Farbcodierung erhält immer
eine textliche Legende.

### Progression und Belastung

Unterscheide Lesen, Sprachuntersuchung, Korrektur, Markierung und freie
Textantwort. Eine Station soll nicht gleichzeitig mehrere unabhängige
Lernhandlungen in einen einzigen Quizstatus pressen. Stelle nach einem langen
Lesetext zunächst eine fokussierte Auswertung und nicht unmittelbar einen
zweiten langen Text. Offene Erklärungen folgen bevorzugt auf die Text- oder
Regelarbeit, die sie vorbereitet. Verteile Diktat, Markierwidget und längere
Freitextantwort so, dass technische und sprachliche Belastung wechseln.

### Hinweise, Lösungen und Bewertung

Hints verweisen auf ein konkretes Sprachmerkmal, eine Textstelle oder einen
Prüfschritt. Lösungen erklären bei Regelanwendung, warum eine Form korrekt
ist; reine Solltexte genügen nur bei einem engen Diktat- oder
Korrekturlernziel. BE folgen den tatsächlich geprüften Markierungen,
Korrekturen oder Inhaltsaspekten. Offene Antworten erhalten atomare
Inhaltskriterien und eine technikärmere Rubrik. Neue bewertbare Blöcke erfüllen
den aktuellen Explain-Vertrag auch dann, wenn historische Sprachaufgaben ihn
nicht enthalten.

### Layout und Seitengliederung

Jede H2-Station bezeichnet einen echten Aufgabenbereich. Kurze Sätze,
Wortlisten oder Teilfragen erhalten `**a)**` statt H3. Längere Lesetexte,
Gedichte und zusammenhängende Erklärungen bleiben linear. DynFlex ist bei
kurzen unabhängigen Sätzen oder Wortpaaren geeignet, nicht für breite
Lesetexte. Markerlegenden nennen Kategorie und Farbe textlich; Audioaufgaben
erhalten eine verständliche schriftliche Aufgabenbeschreibung.

### Template- und Importfolgen

Die feste `weekly`-Basis bleibt `lia-board-mode`, `lia-freeze-v2` und danach
`lia-mathpath`. Je nach gewählten Archetypen kommen lia-orthography,
lia-marker, lia-kachel, lia-DynFlex oder lia-llm direkt hinzu. Native Quizze
verlangen kein zusätzliches Funktionstemplate. Das Profil kopiert keinen
Sammelheader; im Basiskurs gilt kein Gamification-Import.

### Varianten

- **Kurz:** ein Material, drei bis vier Stationen und höchstens eine längere
  offene Antwort.
- **Standard:** fünf bis sechs Stationen mit Lesen/Hören, Untersuchung,
  Korrektur und Anwendung.
- **Erweitert:** zusätzlicher Transfer- oder Schreibauftrag mit klarer Rubrik.
- **Technikärmer:** native Lücken/Matrix, Textausschnitte statt Markerwidget,
  schriftlicher Diktat-Ersatz und Freitext mit Selbstprüfkriterien.
- **Schwächere Lerngruppe:** kürzere Materialien, ein Merkmal pro Teilblock,
  Beispielsatz und konkretere Hints.
- **Stärkere Lerngruppe:** mehrere Kategorien begründet unterscheiden,
  Textbelege vergleichen und eigene Regelanwendung reflektieren.

### Grenzen und Anti-Patterns

Keine Pflichtkombination aus Orthografie, Marker und LLM. Vermeide mehrere
lange Texte oder offene Antworten direkt hintereinander, Farbcodes ohne
Legende, eine freie Interpretation mit vermeintlich eindeutiger Markierspanne,
Groß-/Kleinschreibungsbewertung entgegen dokumentierter Templategrenzen,
H3-Seiten für einzelne Sätze und ein Quiz, das unabhängige Lernhandlungen
vermischt. Selbsteinschätzung und Abgabe beziehen sich auf den realen Kurs und
Übermittlungsweg; Gamification bleibt außerhalb des Basiskurses.

### Kuratierte Vergleichskurse

Alle Links verwenden Commit
`03e72a48a5ccfc46d91ea6770d54dfc9cec05efb`.

| Original | Kursstart und Gliederung | ausgewählte Stationen | Selbsteinschätzung / Abschluss | Beleg und Grenze |
|---|---|---|---|---|
| [`5/Deutsch/Lia5_02.md`](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_02.md#L41-L55) | H1 Z. 41; sechs Aufgaben Z. 102–841 | Leseverstehen Z. 102–159; Kommasetzung Z. 160–190; Wortmarkierung Z. 335–370 | Z. 842–868 | belegt Wechsel aus Lesen, Korrigieren und Markieren; Loot und historische Timer nicht übernehmen; keine Parserwarnung |
| [`5/Deutsch/Lia5_08.md`](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_08.md#L36-L50) | H1 Z. 36; sechs Aufgaben Z. 89–884 | Orthografie Z. 89–125; Satzglieder Z. 267–300; Lesetext Z. 830–860 | Z. 885–899 und 932–939 | belegt kurze Templateübungen plus längere Lesestation; Geheimfolie Z. 901–929 ausgeschlossen; keine Parserwarnung |
| [`6/Deutsch/Lia6_06.md`](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/6/Deutsch/Lia6_06.md#L36-L50) | H1 Z. 36; sechs Aufgaben Z. 86–949 | Diktat Z. 86–110; Lesen und offene Erklärung Z. 689–775; Gedichtanalyse Z. 779–810 | Z. 950–964 und 1018–1025 | belegt Wechsel rezeptiv/produktiv und offene Antwort; Geheimseiten Z. 966–1017 ausgeschlossen; `operator_mismatch` durch pauschale Tags verlangt manuelle Prüfung |

## `CP-WEEKLY-MATH-9-11` — Mathematikwochenkurs Klassen 9–11

**Ausgabeprofil:** `weekly`

**Fach-/Stufengeltung:** Mathematik, belegt für Klassen 9 und 11; Klasse 10
ist eine ausdrücklich gekennzeichnete Evidenzlücke

**Belegstärke:** mittel; drei vollständige Kurse der Klasse 9 und drei der
Klasse 11

Das Profil beschreibt dichte, gemischte Mathematikwochen mit mehreren
Teilhandlungen pro Station. Es darf für Klasse 10 nur als nächstliegende
Orientierung zusammen mit `CP-FALLBACK-COURSE` verwendet werden, nicht als
belegte Klassen-10-Norm.

### Auswahl- und Ausschlussbedingungen

Wähle das Profil für vollständige Mathematik-Wochenkurse der Klassen 9 oder 11
und vorsichtig als Vergleich für Klasse 10. Verwende es nicht für einen
einzelnen Prüfungsbogen, ein `task`-Fragment, einen reinen Grundkurs zu einem
neuen Verfahren oder jüngere Lerngruppen. Ein explizit verlangter kurzer Kurs
darf seine Dichte deutlich unterschreiten.

### Evidenz und Regelklasse

**Beobachtete Korpuswerte:** Die sechs Kurse besitzen 6–7 fachliche
H2-Stationen, Median 7; H3 kommt nicht vor. Erkannte Aufgabenblöcke liegen bei
46–77, Median 70 und Interquartilsbereich 68,2–71. Bewertete Teilblöcke liegen
bei 36–69, Median 56,5 und Interquartilsbereich 54,5–58,5. Diese Werte zeigen
die hohe Dichte des Bestands, sind aber wegen der kleinen Population keine
Sollzahlen.

Alle sechs Kurse enthalten native, mehrteilige und CAS-geprüfte Aufgaben; vier
verwenden Toleranz oder Koordinaten, drei offene Begründungen und drei
Zuordnungen. Klasse 9 zeigt im Bestand weniger Quiz-/Hintknoten als Klasse 11;
zugleich unterscheiden sich Explain-Abdeckung und Autorenstand. Deshalb wird
dies nicht sicher als Jahrgangseffekt interpretiert und kein getrenntes Profil
erzeugt.

**Manuell geprüftes Gestaltungsmerkmal:** Die Stationen beginnen häufig mit
Verfahren oder Diagnose und steigern sich zu vernetzten Rechnungen,
Modellierung, Rekonstruktion oder Beurteilung. Innerhalb einer Station werden
Rechnung, Darstellung und Deutung getrennt geprüft. Die Wochenfolge selbst
kann mehrere Themen wiederholen und ist nicht zwingend ein linearer Lehrgang.

**Bevorzugter Autorenstandard:** Verwende weniger Teilblöcke als im dichten
Bestand, wenn Nutzerauftrag oder Lerngruppe keine vergleichbare Übungsmenge
tragen. Plane pro Station eine erkennbare Binnenprogression und schließe den
Kurs mit Vernetzung, Modellierung oder begründetem Transfer statt einer bloßen
weiteren Routine ab.

**Technische Mussregel:** Der Wochenrahmen und alle aktuellen Header-, Import-,
Explain-, Einheiten-, Überschriften- und Footerregeln gelten unabhängig vom
historischen Kursstand.

### Kursskelett

| Bestandteil | Status | Funktion |
|---|---|---|
| Kursstart und Abgabehinweis | erforderlich | Zweck, Arbeitsweise und realer Übermittlungsweg |
| Diagnose oder Wiederholung zentraler Verfahren | empfohlen | Anschlusswissen aktivieren |
| mehrere fachliche Themenstationen | empfohlen | Verfahren, Darstellung und Anwendung verbinden |
| Modellierung, Rekonstruktion oder Vernetzung | empfohlen | Transfer zwischen Darstellungen und Beziehungen |
| offene Beurteilung/Begründung | bedingt | wenn das Lernziel eine längere fachliche Argumentation trägt |
| differenzierte Selbsteinschätzung | empfohlen | bei breitem Kurs stationsbezogen, sonst kompakt |
| Abgabe | erforderlich | fester Wochenabschluss |
| Gamificationseiten | normalerweise unnötig | nachgelagerte Route |

Geeignete Grundfolge: Kursstart → Verfahren/Diagnose → mehrschrittige
Anwendung → Darstellungswechsel → Modellierung oder Rekonstruktion →
Vernetzung/Transfer → Selbsteinschätzung → Abgabe. Bei mehreren unabhängigen
Themen liegt die Progression innerhalb jeder Station; die Reihenfolge der
Themen folgt Unterrichtsbezug und Auftrag.

### Umfang und Dichte

- **Beobachtet:** sechs bis sieben H2-Stationen, keine H3, sehr viele
  bewertete Teilblöcke pro Kurs.
- **Empfohlener Ausgangswert:** fünf bis sieben Stationen mit bewusst
  reduzierter Teilblockzahl; Qualität und Bearbeitbarkeit gehen vor Bestandsdichte.
- **Kurz:** drei bis vier Stationen mit je einer Kernhandlung und einer
  vernetzenden Schlussaufgabe.
- **Standard:** fünf bis sechs Stationen; pro Station Routine plus Anwendung
  oder Deutung.
- **Erweitert:** sechs bis sieben Stationen mit Modellierung oder Transfer,
  wenn Umfang ausdrücklich gewünscht ist.

Teile lange mathematische Entwicklungen in nachvollziehbare Schritte, aber
nicht in dekorative H3-Seiten. DynFlex dient unabhängigen parallelen
Teilaufgaben; Herleitungen, Beweise und abhängige Modellierungsschritte bleiben
linear.

### Aufgabenarchetypen und Antwortformen

- **Prägend:** `AR-CAS-CALC`, `AR-MULTIPART-FLEX` und
  `AR-NATIVE-CHECK` für Verfahren, gestufte Teilhandlungen und Diagnose.
- **Geeignet ergänzend:** `AR-ESTIMATE-TOLERANCE` bei begründeter Rundung,
  `AR-COORDINATE` für Konstruktion/Graphen, `AR-UNIT` für Größen,
  `AR-ASSIGN-ORDER` für Beziehungen und `AR-OPEN-REASON` für Beurteilung.
- **Selten/bedingt:** `AR-VISUAL-MATH` nur wenn die Manipulation selbst die
  mathematische Repräsentation trägt; Spracharchetypen nur bei echtem
  sprachlichem Lernanteil.

Ein geeigneter Wechsel lautet etwa: native Diagnose → exakte CAS-Rechnung →
Darstellung/Koordinatenhandlung → Toleranz-/Modellierungsaufgabe → offene
Deutung. Technikärmer sind statische Graphen mit nativer Eingabe, lineare
Teilaufgaben, Rechentabellen und Freitext mit fachlicher Rubrik.

### Progression und Belastung

Betrachte Rechenweg, Darstellung, Anwendung und Begründung getrennt. Erhöhe
nicht gleichzeitig Algebraumfang, neue Darstellung, Textmenge und technische
Interaktion. Nach einer dichten Rechenstation folgt sinnvoll eine kürzere
Diagnose oder Deutung. Offene Beurteilungen stehen nach den notwendigen
Verfahren und Materialien. Voraussetzungen für mehrschrittige Teilaufgaben
werden entweder zuvor geprüft oder in der Aufgabe zugänglich bereitgestellt.

### Hinweise, Lösungen und Bewertung

Hints benennen den nächsten mathematischen Ansatz, eine Gleichung, ein
Kriterium oder einen Darstellungswechsel. Musterlösungen zeigen bei
mehrschrittigen Aufgaben Umformung, Begründung, Rundung und Antwortsatz. BE
bilden die verlangten Teilleistungen ab. Bei Größen stehen Wert und Einheit in
Eingabe, Validator und Lösung. Neue `@ADetails`-Blöcke erfüllen den aktuellen
Explain-Vertrag; ältere Kurse ohne vollständige Explain-Abdeckung sind keine
Ausnahme. Offene Antworten erhalten Kriterien und eine technikärmere Rubrik.

### Layout und Seitengliederung

H2 bezeichnet eine fachliche Station. Kurze Rechenschritte und Teilaufgaben
bleiben mit `**a)**` usw. auf derselben Seite. Breite Tabellen, Boards und
Graphen werden mobil geprüft und nicht ohne Nutzen in DynFlex gezwängt.
Längere Herleitungen, Datenmaterial und Begründungen bleiben linear. H3 ist
nur für eine substanzielle eigenständige Unterseite zulässig, nicht für einen
einzelnen Rechenschritt.

### Template- und Importfolgen

Die `weekly`-Basis bleibt `lia-board-mode`, `lia-freeze-v2` und danach
`lia-mathpath`. Algebrite, Canvas/OCR, DynFlex, Coordinate/JSXGraph oder
lia-llm folgen ausschließlich den gewählten Archetypen und werden direkt
importiert. Native Quizze bleiben eine vollwertige Option. Der historische
Sammelheader ist kein Vorbild; der Basiskurs enthält kein Gamification-Import.

### Varianten

- **Kurz:** drei bis vier Stationen mit klarer Themenauswahl und einer
  vernetzenden Schlussaufgabe.
- **Standard:** fünf bis sechs Stationen, jeweils mit Verfahren plus Anwendung
  oder Deutung.
- **Erweitert:** sechs bis sieben Stationen einschließlich Modellierung,
  Rekonstruktion oder Beurteilung.
- **Technikärmer:** statische Diagramme, native Eingaben/Auswahl, lineares
  Layout und Rubrik statt LLM.
- **Schwächere Lerngruppe:** Voraussetzungen sichtbar aktivieren, weniger
  gleichzeitige Teilziele, gestufte Hints und kleinere Datenmengen.
- **Stärkere Lerngruppe:** alternative Lösungswege vergleichen, Parameter
  variieren und Modelle begründet beurteilen.

### Grenzen und Anti-Patterns

Die beobachteten 46–77 Parserblöcke sind keine Sollmenge. Vermeide dichte
Ketten gleichartiger CAS-Aufgaben, mehrere schwere Widgets hintereinander,
Rundung ohne Toleranzbegründung, Rechenwegforderung mit reiner Endwertprüfung,
H3-Inflation und stationsbezogene Reflexion, die nur Titel wiederholt. Klasse
10 darf nicht als direkt belegt ausgegeben werden. Timer, Sammelimporte und
Gamification bestimmen weder Zeitbedarf noch fachliche Komposition.

### Kuratierte Vergleichskurse

Alle Links verwenden Commit
`03e72a48a5ccfc46d91ea6770d54dfc9cec05efb`.

| Original | Kursstart und Gliederung | ausgewählte Stationen | Selbsteinschätzung / Abschluss | Beleg und Grenze |
|---|---|---|---|---|
| [`9/Mathematik/Lia9_01.md`](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/9/Mathematik/Lia9_01.md#L32-L45) | H1 Z. 32; sieben Aufgaben Z. 89–1950 | Einheiten Z. 89–135; Kreis/Körper Z. 1425–1480; Funktionen Z. 1644–1695 | Z. 1951–1970 | belegt Wechsel aus Verfahren, Toleranz, Geometrie und Funktion; Einheitenprüfung nach aktuellem Vertrag verbessern; keine Parserwarnung |
| [`9/Mathematik/Lia9_03.md`](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/9/Mathematik/Lia9_03.md#L32-L50) | H1 Z. 32; sechs Aufgaben Z. 103–1199 | Kreis Z. 103–150; themenübergreifende Geometrie Z. 1002–1050 | Z. 1200–1210 und 1268–1276 | belegt Routine → themenübergreifende Anwendung; Geheimseiten Z. 1214–1267 ausgeschlossen; keine Parserwarnung |
| [`11/Mathematik/Lia11_03.md`](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_03.md#L25-L43) | H1 Z. 25; sieben Aufgaben Z. 77–1600 | Ableitung/Deutung Z. 77–140; gemischte Differentialrechnung Z. 1375–1430 | Z. 1601–1653 | belegt gestufte Teilhandlungen, vollständige Rechenwege und stationsbezogene Reflexion; Gamificationfrage Z. 1639–1641 nicht in Basiskurs übernehmen; keine Parserwarnung |

## `CP-COURSE-SINGLE-TASK` — Vollständiger Ein-Aufgaben-Kurs

**Ausgabeprofil:** `course`

**Fach-/Stufengeltung:** fachübergreifende Struktur; die Korpusevidenz stammt
überwiegend aus Mathematik und trägt keine Klassenstufennorm

**Belegstärke:** stark für die Seitenstruktur; 1.220 vollständige Kurse, aber
keine einheitliche didaktische Fach- oder Stufenprogression

Dieses Profil gilt, wenn eine einzelne Aufgabe eigenständig nutzbar sein soll.
Eine Aufgabenzahl von eins macht daraus kein `task`-Fragment: Der Kurs erhält
einen vollständigen Hauptkopf und den Board-Mode-Basisimport.

### Auswahl- und Ausschlussbedingungen

Wähle das Profil für genau einen eigenständig nutzbaren Auftrag im Profil
`course`, gegebenenfalls mit mehreren eng zusammengehörigen Teilaufgaben.
Verwende es nicht für einen ausdrücklich verlangten Einfügeausschnitt, eine
Wochenaufgabe, mehrere eigenständige Lernstationen oder einen Kurs, dessen
Nutzerauftrag eine längere Progression verlangt. Mehrere unabhängige Aufgaben
verwenden ein belegtes Mehr-Aufgaben-Profil oder `CP-FALLBACK-COURSE`.

### Evidenz und Regelklasse

**Beobachtete Korpuswerte:** Alle 1.220 Kurse besitzen genau eine H1 und keine
H2/H3. Erkannte Aufgabenblöcke haben Median und Quartile 1; die Spannweite
reicht bis 18, weil ein Seitenauftrag mehrere Parserblöcke enthalten kann.
Bewertete Teilblöcke liegen im Median bei 4, Interquartilsbereich 2–6.
DynFlex-bezogene Aufgabenblöcke liegen im Median bei 1. Native Antwortformen
erscheinen in 1.126 Kursen, mehrteilige Strukturen in 1.115, CAS-Prüfung in
546, Koordinatenhandlungen in 85 und Toleranz in 28. Die alte Sammlung nutzt
Sammelheader; deren Importzahl ist ausdrücklich kein Sollwert.

**Manuell geprüftes Gestaltungsmerkmal:** Die kuratierten Originale beginnen
mit einem präzisen Titel, nennen Material und Operator knapp, bündeln kurze
Teilaufgaben auf derselben Seite und führen direkt zu Eingabe, Hint,
Rückmeldung und BE. Sie enthalten keinen Wochenfooter und keine
Selbsteinschätzung.

**Bevorzugter Autorenstandard:** Erzeuge eine fokussierte Inhaltsseite mit
einer Hauptlernhandlung. Mehrere Teilaufgaben teilen Material, Verfahren oder
Ziel und steigern sich nachvollziehbar. Ergänze keine zweite Station nur, um
den Kurs länger wirken zu lassen.

**Technische Mussregel:** Ein neuer Ein-Aufgaben-Kurs folgt dem aktuellen
`course`-Vertrag, nicht dem historischen Header: genau ein Hauptkopf,
`lia-board-mode`, nur benötigte Direktimporte, aktuelle Explain-/Einheiten- und
Leerzeilenregeln. Eine Selbsteinschätzung oder Abgabe ist im Profil `course`
nicht automatisch Pflicht.

### Kursskelett

| Bestandteil | Status | Funktion |
|---|---|---|
| vollständiger Hauptkopf | erforderlich | Metadaten, Board-Mode und benötigte direkte Ressourcen |
| eine aussagekräftige H1 | erforderlich | eigenständige Kurs-/Aufgabenseite |
| notwendiges Material | bedingt | Bild, Text, Diagramm oder Situation vor dem Auftrag |
| präziser Operator und Antwortform | erforderlich | Lernhandlung und erwartete Leistung klären |
| kurze zusammengehörige Teilaufgaben | bedingt | Übung oder gestufte Bearbeitung ohne neue Seite |
| Hint und angemessene Lösung/Rückmeldung | empfohlen | nächster Schritt und fachlicher Abschluss |
| Bewertung mit BE/Themen | bedingt | erforderlich, wenn der SchulLia-Block bewertet wird |
| Wochenfooter, Selbsteinschätzung, Gamification | normalerweise unnötig | gehören nicht automatisch zum Ein-Aufgaben-Kurs |

Grundfolge: Hauptkopf → H1 → Material/kurze Einleitung → Arbeitsauftrag →
Antwort/Prüfung → Hint → Lösung oder Feedback → gegebenenfalls BE. Bei
Teilaufgaben: gemeinsamer Auftrag → `**a)**`, `**b)**` … mit je passender
Prüfung → gemeinsamer oder getrennter fachlicher Abschluss.

### Umfang und Dichte

- **Beobachtet:** eine Inhaltsseite; median ein erkannter Aufgabenblock und
  vier bewertete Teilblöcke, jedoch große Spannweite.
- **Empfohlener Ausgangswert:** eine zentrale Lernhandlung mit einer bis vier
  kurzen Teilaufgaben, wenn das Lernziel davon profitiert.
- **Kurz:** eine Frage mit nativer Antwort und knapper Rückmeldung.
- **Standard:** ein gemeinsamer Auftrag mit zwei bis vier gestuften
  Teilaufgaben, Hint und erklärender Lösung.
- **Erweitert:** Material plus mehrere zusammengehörige Teilhandlungen; sobald
  eigenständige Stationen entstehen, ist ein Mehr-Aufgaben-Kurs zu planen.

Lange Materialien und abhängige Schritte bleiben linear. DynFlex wird nur für
echten responsiven Nutzen eingesetzt und ist keine Pflicht dieses Profils.

### Aufgabenarchetypen und Antwortformen

Es gibt keinen fachunabhängig prägenden Pflichtarchetyp. Häufig belegt sind
`AR-NATIVE-CHECK`, `AR-MULTIPART-FLEX` und `AR-CAS-CALC`; möglich sind je nach
Lernhandlung alle IDs des Archetypenkatalogs, insbesondere `AR-UNIT`,
`AR-ESTIMATE-TOLERANCE`, `AR-OPEN-REASON`, `AR-ORTHOGRAPHY`, `AR-TEXT-MARK`,
`AR-ASSIGN-ORDER`, `AR-COORDINATE` oder `AR-VISUAL-MATH`.

Wähle den kleinsten vollständigen Archetyp. Eine einzige feste Antwort bleibt
nativ. Technikärmer sind native Auswahl/Eingabe, statische Medien, lineare
Anordnung und eine sichtbare Rubrik. Verwende nicht mehrere Templates, wenn sie
dieselbe Lernhandlung doppelt prüfen.

### Progression und Belastung

Die Progression liegt innerhalb der einen Aufgabe: verstehen/erkennen →
anwenden → gegebenenfalls erklären oder übertragen. Teilaufgaben teilen einen
fachlichen Kern und erhöhen höchstens eine oder zwei Belastungsdimensionen
zugleich. Wenn Material, Verfahren und Antwortform zwischen Teilaufgaben
vollständig wechseln, sind es wahrscheinlich mehrere Aufgaben und nicht mehr
dieses Profil.

### Hinweise, Lösungen und Bewertung

Ein Hint führt zum nächsten sinnvollen Schritt. Die Lösungstiefe folgt dem
Operator: Ergebnis bei enger Erkennung, Rechenweg bei Berechnung,
Begründungskette bei Erklärung. Jede bewertete Teilhandlung erhält passende BE
und Themen; mehrere unabhängige Quizblöcke dürfen getrennte Angaben tragen.
Der aktuelle Explain-Vertrag gilt. Offene Antworten erhalten Kriterien und
eine technikärmere Rubrikvariante.

### Layout und Seitengliederung

Die eine H1 ist die Kursseite. Kurze Teilaufgaben verwenden `**a)**`, `**b)**`
usw. und keine H2/H3. Nur eine belegte technische Abschnittsgrenze oder eine
tatsächlich eigenständige Seite rechtfertigt eine tiefere Hash-Überschrift; in
diesem Fall ist zu prüfen, ob weiterhin ein Ein-Aufgaben-Kurs vorliegt.
Material steht unmittelbar vor dem Auftrag, die Frage unmittelbar vor dem Quiz.

### Template- und Importfolgen

Der vollständige `course` importiert `lia-board-mode` direkt und genau einmal.
Weitere Imports folgen ausschließlich dem gewählten Archetyp und dessen
Abhängigkeiten. Die 16 historischen Sammelimporte vieler Originale werden
nicht reproduziert. Native Quizze sind ausdrücklich zulässig. Der Basiskurs
enthält kein Gamification-Import.

### Varianten

- **Kurz:** eine native Diagnose oder Eingabe mit präzisem Feedback.
- **Standard:** zwei bis vier eng verwandte Teilaufgaben mit gestuftem Hint und
  erklärender Lösung.
- **Erweitert:** Material plus Anwendung und Begründung, solange ein
  gemeinsamer Lernkern erhalten bleibt.
- **Technikärmer:** lineare Absätze, natives Quiz, statisches Bild und Rubrik.
- **Schwächere Lerngruppe:** Beispiel, reduzierte Teilzahl und konkrete Hints.
- **Stärkere Lerngruppe:** offenere Begründung, alternative Strategie oder
  Transfer bei gleichem Kern.

### Grenzen und Anti-Patterns

Kein `task`-Fragment ohne ausdrücklichen Wunsch, kein zweiter Hauptkopf, keine
H2/H3 pro kurzer Teilfrage, kein Sammelheader, keine künstliche
Templatevielfalt und keine Vermischung unabhängiger Lernhandlungen in einem
Quiz. Ergänze weder Wochenfooter noch Gamification, nur weil historische
Kurse sie an anderer Stelle verwenden. Timerwerte liefern keine Zeitnorm.

### Kuratierte Vergleichskurse

Alle Links verwenden Commit
`c9ac1585a0545a54a185de885c272da3e4aacbef`.

| Original | Kursstart und Gliederung | ausgewählte Aufgabenstationen | Selbsteinschätzung / Abschluss | Beleg und Grenze |
|---|---|---|---|---|
| [`01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0001.md`](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0001.md#L53-L120) | eine H1 Z. 53 | gemeinsamer Operator und vier kurze Teilaufgaben Z. 56–120 | nicht vorhanden; `course` verlangt keinen Wochenabschluss | belegt kompakten Mehrteilauftrag; Sammelheader, Timer und historische Leerzeilen nicht übernehmen; keine Parserwarnung |
| [`01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0057.md`](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0057.md#L55-L104) | eine H1 Z. 55 | zwei Bildschätzungen mit Toleranz Z. 58–104 | nicht vorhanden | belegt Material plus passende Toleranzantwort; Alternativtext und Toleranz fachlich prüfen, Sammelheader nicht übernehmen; keine Parserwarnung |
| [`02_Geometrie/07_Kongruenz/Aufgabe_0028.md`](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/02_Geometrie/07_Kongruenz/Aufgabe_0028.md#L38-L68) | eine H1 Z. 38 | Material und offene Begründung Z. 41–68 | nicht vorhanden | belegt fokussierte offene Aufgabe mit Kriterien und Lösung; konkrete Schwellen bleiben aufgabenspezifisch; keine Parserwarnung |

## `CP-FALLBACK-COURSE` — Evidenzbewusster Rückfall

**Ausgabeprofil:** `weekly` oder `course`; niemals automatisch `task`

**Fach-/Stufengeltung:** jedes Fach oder jede Stufe ohne belastbares
Kompositionsprofil

**Belegstärke:** keine eigene Fach-/Stufenpopulation; bewusst manuell aus
Nutzerauftrag und Lernziel abzuleiten

Das Fallback verhindert, dass eine Datenlücke als universeller Wochenstandard
ausgegeben wird. Es übernimmt nur den technischen Vertrag, den Hausstil und
die für den konkreten Auftrag belegten Aufgabenarchetypen.

### Auswahl- und Ausschlussbedingungen

Wähle dieses Profil, wenn kein passendes Fach-/Stufenprofil existiert, wenn
eine Gruppe weniger als drei belastbare Vergleichskurse besitzt oder wenn der
Auftrag deutlich außerhalb des Geltungsbereichs eines Profils liegt. Verwende
es nicht, um vorhandene belastbare Evidenz zu ignorieren. Ein ausdrückliches
`task`-Fragment benötigt weiterhin kein Kompositionsprofil. Ein einzelner
eigenständiger Auftrag verwendet bevorzugt `CP-COURSE-SINGLE-TASK`.

### Evidenz und Regelklasse

**Beobachtete Korpuswerte:** Es gibt absichtlich keine eigene Population und
keine typische Stations-, Template- oder Teilaufgabenzahl. Zahlen aus einem
benachbarten Profil dürfen nur als Vergleich und klar gekennzeichnete
Orientierung dienen.

**Manuell geprüftes Gestaltungsmerkmal:** Für jeden konkreten Kurs werden
mindestens drei fachlich, stufenbezogen und im Umfang passende vollständige
Originalkurse gesucht, sofern vorhanden; andernfalls alle verfügbaren. Ihre
Progression wird gelesen, aber nicht schematisch kopiert.

**Bevorzugter Autorenstandard:** Leite zuerst aus Nutzerauftrag und Lernziel die
notwendigen Lernhandlungen ab. Ordne ihnen einzeln Archetypen zu und begründe
bei mehreren Aufgaben ihre Reihenfolge. Bei nur einer Aufgabe bleibt der Kurs
kompakt. Bei einem `weekly`-Kurs gilt der feste Wochenrahmen auch ohne
fachspezifische Korpusnorm.

**Technische Mussregel:** Ausgabeprofil, Hauptkopf, direkte Importe,
Überschriften, Explain, Einheiten, Selbsteinschätzung/Abgabe bei `weekly` und
Validierung folgen vollständig dem Ausgabevertrag.

### Kursskelett

| Bestandteil | Status | Funktion |
|---|---|---|
| Ausgabeprofil und Lernziel | erforderlich | `weekly` oder `course` und gewünschtes Ergebnis klären |
| notwendige Voraussetzungen | empfohlen | Anschlusswissen aktivieren oder bereitstellen |
| Kernlernhandlungen | erforderlich | jede Aufgabe hat einen erkennbaren didaktischen Zweck |
| manuell begründete Progression | erforderlich bei mehreren Aufgaben | Aufnahme/Routine → Anwendung → Transfer nur soweit fachlich passend |
| Reflexion und Abgabe | erforderlich nur bei `weekly` | fester Wochenvertrag |
| zusätzliche Stationen ohne Lernzweck | normalerweise unnötig | keine Füllaufgaben |

Für mehrere Aufgaben wird vor dem Schreiben eine kurze Folge begründet:
Voraussetzung → Kernhandlung → Anwendung → gegebenenfalls Transfer/Reflexion.
Diese Folge ist kein fachunabhängiges Muss; sie wird angepasst, wenn etwa eine
ästhetische, experimentelle oder produktorientierte Lernhandlung anders
verläuft.

### Umfang und Dichte

Es gibt keinen beobachteten Sollwert. Der Nutzerauftrag bestimmt die
Aufgabenzahl. Ohne Zahl wird der kleinste Umfang gewählt, der Lernziel,
Übung und Rückmeldung vollständig abdeckt. Ein `course` mit nur einem Auftrag
bleibt eine Seite nach `CP-COURSE-SINGLE-TASK`; ein `weekly` bewahrt unabhängig
vom Umfang den festen Abschluss.

- **Kurz:** ein eigenständiger Auftrag oder wenige Kernstationen.
- **Standard:** notwendige Aktivierung, Kernübung, Anwendung und Abschluss.
- **Erweitert:** zusätzlicher Transfer oder Differenzierung mit begründetem
  Lernzweck.

Materialmenge und Teilblockdichte werden manuell auf Lerngruppe und Medium
geprüft. Timerwerte oder fremde Kurslängen liefern keine Zeitvorgabe.

### Aufgabenarchetypen und Antwortformen

Wähle jede ID aus dem [Archetypenkatalog](task-archetypes.md) einzeln nach
Lernhandlung und Antwortform. Beginne mit `AR-NATIVE-CHECK`, wenn native
Syntax vollständig genügt; verwende etwa `AR-CAS-CALC`, `AR-OPEN-REASON`,
`AR-ORTHOGRAPHY`, `AR-TEXT-MARK`, `AR-ASSIGN-ORDER`, `AR-COORDINATE` oder
`AR-VISUAL-MATH` nur für ihren belegten Mehrwert. `AR-MULTIPART-FLEX` ist eine
Querschnittsstruktur, keine Pflicht.

Ein Wechsel der Antwortformen ist nur dann sinnvoll, wenn sich die
Lernhandlungen unterscheiden. Technikärmer bleiben native Quizze, statische
Medien, lineares Layout und sichtbare Bewertungsrubriken immer zulässig.

### Progression und Belastung

Begründe bei mehreren Aufgaben für jede Position: vorausgesetztes Wissen,
neue oder geübte Handlung, erwartete Antwortform und Anschluss an die nächste
Aufgabe. Vermeide mehrere lange, offene oder technisch anspruchsvolle Aufgaben
in Folge. Erhöhe nicht gleichzeitig Inhalt, Sprache, Darstellung und Technik,
wenn der fachliche Zweck dies nicht verlangt.

### Hinweise, Lösungen und Bewertung

Plane Hint, Lösung und Bewertung aus dem Operator und der Antwortform. Der
Hint nennt den nächsten Schritt; die Lösung zeigt die geforderte Tiefe; BE und
Themen entsprechen den bewerteten Leistungen. Offene Antworten erhalten
Erwartungshorizont und technikärmere Rubrik. Neue bewertbare Aufgaben erfüllen
den Explain-Vertrag; eine Datenlücke rechtfertigt keine technische Ausnahme.

### Layout und Seitengliederung

H2 wird nur für eine eigenständige Seite oder Station verwendet, H3 nur für
substanzielle Unterseiten. Kleine Teilaufgaben bleiben als Absatz, Liste oder
Fettkennzeichnung zusammen. DynFlex wird nur bei responsivem Nutzen eingesetzt.
Medien erhalten zugängliche Alternativen und werden unmittelbar bei der
zugehörigen Lernhandlung platziert.

### Template- und Importfolgen

Die Profilbasis folgt dem Ausgabevertrag: `lia-board-mode` für jeden
vollständigen Kurs, bei `weekly` zusätzlich `lia-freeze-v2` und danach
`lia-mathpath`. Alle weiteren direkten Imports entstehen aus den tatsächlich
gewählten Archetypen. Native Quizze benötigen kein Dekorationstemplate. Der
nicht-gamifizierte Basiskurs enthält kein Gamification-Import.

### Varianten

- **Kurz:** kleinstmöglicher vollständiger Kurs nach Auftrag.
- **Standard:** begründete Folge aus Voraussetzung, Kernhandlung, Anwendung
  und passendem Abschluss.
- **Erweitert:** Transfer oder Differenzierung mit eigenem Lernzweck.
- **Technikärmer:** native Quizze, statische Materialien, lineares Layout und
  Rubrik.
- **Schwächere Lerngruppe:** Voraussetzungen explizit, kleinere Schritte und
  konkrete Hints.
- **Stärkere Lerngruppe:** offenere Strategie, Transfer und Beurteilung, ohne
  zusätzliche Technikpflicht.

### Grenzen und Anti-Patterns

Behaupte keine Fach- oder Klassenstufennorm ohne Evidenz. Übernimm weder sechs
Stationen noch eine Archetypenquote aus einem fremden Profil. Vermeide
Füllaufgaben, künstliche Templatevielfalt, mehrere gleichartige Blöcke ohne
Progression, H3-Seiten für Teilfragen, Selbsteinschätzung ohne Kursbezug und
Abgabe ohne Übermittlungsweg. Gamification und Timer werden nicht zum
Kompositionsersatz.

### Kuratierte Vergleichskurse

Das Fallback besitzt bewusst keine feste Vergleichskursliste. Für den
konkreten Auftrag werden über die Korpusroute mindestens drei passende reale
vollständige Kurse gelesen, sofern verfügbar; andernfalls alle. Als
strukturielle Ausgangspunkte dürfen die kuratierten Kurse des nächstliegenden
Profils verwendet werden, aber Quelle, Commit, Pfad, relevante Zeilen,
Parserwarnungen und Übernahmegrenzen müssen im Arbeitsnachweis konkret genannt
werden. Für einen einzigen eigenständigen Auftrag gelten die drei Originale
unter `CP-COURSE-SINGLE-TASK` als strukturelle, nicht fachliche Beispiele.

## Beleglücke: kurzer thematischer Mehr-Aufgaben-Kurs

Nach Ausschluss von Repetitoriumsfragmenten, Tests und Dummys besitzt die
Aufgabensammlung nur einen vollständigen Kandidaten mit mehreren H2-Seiten:
[`BLF_0001.md`](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/BLF_0001.md#L52-L1009).
Er umfasst sieben prüfungsähnliche Aufgabenbereiche und ist weder kurz noch
eine breite Vergleichspopulation. Ein eigenes Profil würde daher
Scheinpräzision erzeugen.

Für einen kurzen thematischen Mehr-Aufgaben-Kurs gilt stattdessen
`CP-FALLBACK-COURSE`: Ausgabeprofil `course`, manuell begründete Progression,
gezielte Suche nach mindestens drei thematisch passenden vollständigen Kursen
oder allen verfügbaren Kandidaten und einzelne Archetypenwahl pro
Lernhandlung. Das BLF-Original darf als oberer Umfangsvergleich dienen, nicht
als Standardskelett. Es enthält keine Selbsteinschätzung oder Abgabe und belegt
keinen allgemeinen Abschlussstandard.

## Auswahl- und Abschlussprüfung

1. Bestimme `weekly`, `course` oder ausdrücklich `task` nach dem
   Ausgabevertrag.
2. Lies den Hausstil.
3. Wähle bei einem vollständigen `weekly`- oder Mehr-Aufgaben-`course`-Kurs
   genau ein passendes Kompositionsprofil; kombiniere das Profil bei einer
   ausgewiesenen Evidenzlücke mit `CP-FALLBACK-COURSE`.
4. Begründe Umfang und Reihenfolge aus Nutzerauftrag, Lernziel, Lerngruppe und
   Profil. Beobachtete Zahlen bleiben Orientierung.
5. Wähle für jede Lernhandlung einen Aufgabenarchetyp und prüfe eine native
   beziehungsweise technikärmere Alternative.
6. Lies erst danach die konkrete Quiz-, Template- und Optionssyntax.
7. Prüfe den fertigen Kurs gegen Vertrag, Fachsprache, Progression,
   Belastungswechsel, direkte Importe und das passende Validatorprofil.
