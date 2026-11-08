# SchulLia-Aufgabenarchetypen

Diese Referenz ist die Entscheidungsschicht zwischen Lernhandlung und
technischer Umsetzung. Lies vor ihr den
[Ausgabevertrag](authoring-contract.md) und den
[SchulLia-Hausstil](authoring-style.md). Wähle bei einem vollständigen
`weekly`- oder Mehr-Aufgaben-`course`-Kurs zuvor ein passendes
[Kurskompositionsprofil](course-composition-profiles.md); ein ausdrückliches
`task`-Fragment benötigt keines. Verwende anschließend die
[LiaScript-Grundsyntax](liascript-basics.md), die
[Quizstrukturen](quiz-structures.md) und die
[Template-Auswahl](template-options.md) für Syntax, Optionen und aktuelle
Abhängigkeiten.

Ein Archetyp ist keine Kopiervorlage und keine Pflicht, ein Template
einzusetzen. Entscheidend sind Lernhandlung und erwartete Antwortform. Reicht
ein natives LiaScript-Quiz aus, ist „kein zusätzliches Funktionstemplate“ eine
vollwertige und häufig bevorzugte Entscheidung. Ausdrückliche Vorgaben wie
„nur native Quizze“, „ohne LLM“, „kurz“ oder ein vorhandener Kursrahmen haben
Vorrang. Gamification bleibt ein getrennter, nachgelagerter Arbeitsschritt.

## Evidenzbasis und Abdeckung

Die Bestandsanalyse ist auf diese lokalen Revisionen gepinnt:

- **A:** `MINT-the-GAP/Aufgabensammlung`, Commit
  `c9ac1585a0545a54a185de885c272da3e4aacbef`;
- **W:** `MINT-the-GAP/Wochenaufgabe`, Commit
  `03e72a48a5ccfc46d91ea6770d54dfc9cec05efb`.

Für die Archetypenzählung wurde die im Hausstil beschriebene Population
zusätzlich um README-, Import- und Dummy-Pfade bereinigt. Dokumente mit der
Parserwarnung `contains_dynamic_random_generation` sowie nicht regulär benannte
Wochenkurse blieben ausgeschlossen. Dadurch wurden 2.754 Aufgabenblöcke aus A
und 1.912 aus W ausgewertet. Die Kategorien überlappen: Eine mehrteilige
Koordinatenaufgabe kann beispielsweise zugleich als
`AR-MULTIPART-FLEX` und `AR-COORDINATE` zählen.

| Archetyp | A | W | Summe | Beleglage |
|---|---:|---:|---:|---|
| `AR-NATIVE-CHECK` | 263 | 192 | 455 | beidseitig |
| `AR-CAS-CALC` | 932 | 644 | 1.576 | beidseitig |
| `AR-UNIT` | 0 | 51 | 51 | nur W |
| `AR-ESTIMATE-TOLERANCE` | 141 | 81 | 222 | beidseitig |
| `AR-MULTIPART-FLEX` | 1.642 | 1.233 | 2.875 | beidseitig; querschnittlich |
| `AR-OPEN-REASON` | 8 | 40 | 48 | beidseitig, Schwerpunkt W |
| `AR-ORTHOGRAPHY` | 0 | 60 | 60 | nur W |
| `AR-TEXT-MARK` | 0 | 73 | 73 | nur W |
| `AR-ASSIGN-ORDER` | 26 | 44 | 70 | beidseitig; im Bestand nativ |
| `AR-COORDINATE` | 364 | 229 | 593 | beidseitig |
| `AR-VISUAL-MATH` | 8 | 55 | 63 | beidseitig, unterschiedliche Familien |

Die Zählung verwendet erkannte Quiztypen und Makros als Suchindikatoren und
danach geprüfte Originalausschnitte. Makrointern erzeugte Quizsyntax wurde
nicht als zweite Autorenentscheidung gezählt. `operator_mismatch` bleibt ein
Prüfhinweis: Die kuratierten A-Belege enthalten einzelne solche Warnungen,
obwohl die sichtbare Lernhandlung nachvollziehbar ist. Für neue Inhalte müssen
Operator, Metatag und Anforderungsniveau trotzdem zusammenpassen.

## Auswahl in vier Entscheidungen

1. Bestimme die konkrete Lernhandlung: auswählen, berechnen, schätzen,
   begründen, korrigieren, markieren, zuordnen, konstruieren oder darstellen.
2. Bestimme die Antwortform: feste Option, mathematischer Ausdruck, Größe mit
   Einheit, Freitext, Textänderung, Markierung, Drag-and-drop oder grafische
   Konstruktion.
3. Wähle den kleinsten technisch vollständigen Archetyp. Beginne nativ und
   ergänze nur Templates, die Prüfung, Eingabe, Darstellung oder Rückmeldung
   tatsächlich verbessern.
4. Lege erst danach Optionsprofil, Direktimporte, Hinweise, Lösung,
   Wiederholung und Bewertung fest. Jede bewertbare Lernhandlung erhält dabei
   den sichtbaren Imperativoperator und die operatorgerechte Lösungsform aus
   dem Ausgabevertrag. Profilbasis und Hauptkopf folgen immer dem
   Ausgabevertrag, nicht historischen Sammelheadern der Belege.

Für den Aufgabenrhythmus gelten vier Kennzeichnungen:

- **erforderlich:** Ohne diesen Baustein ist die Lernhandlung oder Prüfung
  unvollständig;
- **empfohlen:** SchulLia-Standardfall, sofern Aufgabe und Lerngruppe nichts
  anderes nahelegen;
- **bedingt:** Nur bei der genannten Funktion oder Unterrichtssituation;
- **normalerweise unnötig:** Kein Standardbestandteil dieses Archetyps.

## Übersichtsmatrix

| ID | Lernhandlung | Antwortform | Bevorzugte Umsetzung | Alternativen | Hauptrisiko |
|---|---|---|---|---|---|
| `AR-NATIVE-CHECK` | erkennen, auswählen, kurz diagnostizieren | Auswahl, Matrix, Inlineauswahl oder kurze Eingabe | natives LiaScript-Quiz | CAS oder Fachtemplate nur bei zusätzlichem Prüfbedarf | Template ohne Mehrwert |
| `AR-CAS-CALC` | exakt rechnen oder symbolisch umformen | Zahl, Term oder Gleichung | native Eingabe mit Algebrite | native feste Antwort; Canvas/OCR als Eingabehilfe | Zeichenfolge statt mathematischer Gleichwertigkeit prüfen |
| `AR-UNIT` | Größen berechnen oder umrechnen | Zahlenwert und Einheit gemeinsam | native Eingabe mit einheitenbewusstem Algebrite-Validator | native feste Eingabe nur bei völlig fester Schreibweise | Einheit nur anzeigen, aber nicht prüfen |
| `AR-ESTIMATE-TOLERANCE` | schätzen, runden, nähern | Wert im Intervall oder mit Toleranz | `check_margin` oder `check2` | exakter CAS-Check nach vorgegebener Rundung | unbegründete Toleranz |
| `AR-MULTIPART-FLEX` | mehrere kurze verwandte Teilhandlungen | mehrere unabhängige Quizblöcke | Teilkennzeichnungen; DynFlex nur bei responsivem Nutzen | lineare Folge | Flexlayout als fachliche Struktur missverstehen |
| `AR-OPEN-REASON` | erklären, begründen, vergleichen, beurteilen | freie Antwort in Sätzen | vollständig konfiguriertes LLMQuiz | unbewerteter Freitext, Rubrik oder feste Teilfragen | LLM für deterministische Antwort erzwingen |
| `AR-ORTHOGRAPHY` | schreiben, korrigieren, Diktat | überarbeiteter Text oder Hörschreibung | lia-orthography | native Lücken bei einzelnen eindeutigen Wörtern | ungeeignete Groß-/Kleinschreibungsbewertung |
| `AR-TEXT-MARK` | Textbelege oder Kategorien markieren | farbige Textauswahl | lia-marker | Auswahlmatrix bei sehr kurzen, getrennten Elementen | Farblegende oder Erklärung fehlt |
| `AR-ASSIGN-ORDER` | zuordnen, gruppieren, sortieren | Drag-and-drop | native Drops; lia-kachel bei begründetem Kachelnutzen | Matrix oder Auswahl | Zuordnung und Reihenfolge verwechseln |
| `AR-COORDINATE` | Punkte setzen, zeichnen, konstruieren | interaktives Board oder statische Darstellung | lia-coordinate mit JSXGraph | freies JSXGraph; statischer Coordinate-Import | Board-IDs, Toleranzen oder Werkzeuge nicht abstimmen |
| `AR-VISUAL-MATH` | Brüche legen, Flächen oder Steine manipulieren | visuelle Manipulation | lia-Mathe oder lia-pentominos | statische Grafik plus natives Quiz | Dekoration statt Lernhandlung |

## `AR-NATIVE-CHECK` — Native Auswahl, Kurzantwort und Diagnose

**Lernhandlung:** erkennen, unterscheiden, auswählen, zuordnen oder einen
kurzen eindeutigen Befund angeben.

**Antwortform:** Single-/Multiple-Choice, Inlineauswahl, Matrix oder kurze
native Texteingabe.

**Zweck:** schnelle, transparente Prüfung ohne zusätzliches Funktionstemplate.

### Auswahl

- **Wählen:** wenn richtige Antworten vollständig aufzählbar und mit nativer
  LiaScript-Syntax eindeutig prüfbar sind.
- **Nicht wählen:** wenn algebraische Gleichwertigkeit, Toleranz, freie
  Begründung, Textmarkierung oder eine Konstruktion bewertet werden muss.
- **Native Alternative:** ist hier der Regelfall; ein Template ist nur für
  einen nachweisbaren Zusatznutzen erforderlich.

### Umsetzung und Importe

Verwende den passenden nativen Quiztyp aus
[quiz-structures.md](quiz-structures.md). Außer der Profilbasis entsteht kein
funktionsbedingter Direktimport. `lia-resetter`, `lia-timer`, Freeze/MathPath
oder `lia-globalquiz` werden nur bei tatsächlich genutzter Wiederholung,
Zeitfreigabe, Bewertung/Explain oder kursweiter Steuerung ergänzt.

### Aufgabenrhythmus

- **Erforderlich:** direkter Auftrag → native Auswahl/Eingabe → eindeutige
  korrekte Optionen oder Sollantwort.
- **Empfohlen:** konkretes Feedback oder kurze Lösung; bei bewertetem
  `@ADetails` der vertraglich gebundene Explain-Hint.
- **Bedingt:** Randomisierung, Matrix, horizontaler Auswahlmodus oder
  Einzelreset.
- **Normalerweise unnötig:** LLMQuiz, Canvas/OCR und Fachtemplate.

### Varianten

- einfach: eine Erkennungsfrage mit wenigen plausiblen Optionen;
- anspruchsvoller: mehrere richtige Aussagen oder eine Matrix;
- technikarm: kurze Texteingabe mit exakt akzeptierter Antwort;
- mobil: kurze Optionen und keine breite Matrix, wenn sie horizontal scrollen
  müsste.

### Grenzen und Anti-Patterns

- Distraktoren dürfen keine unbeabsichtigten Mehrdeutigkeiten erzeugen.
- Eine Freitextbegründung ist keine Auswahlfrage; trenne die Lernhandlungen.
- Nutze kein LLM, wenn eine feste Option oder ein deterministischer Validator
  die Antwort vollständiger und nachvollziehbarer prüft.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| A | [`01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0009.md`, Z. 53–114](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0009.md#L53-L114) | native Matrix mit mehreren kurzen Teilaufgaben | ein `operator_mismatch`; nicht ungeprüft übernehmen |
| W | [`11/Mathematik/Lia11_01.md`, Z. 442–458](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_01.md#L442-L458) | Multiple-Choice mit Erklärung | keine Parserwarnung |

## `AR-CAS-CALC` — Exakte numerische und symbolische Berechnung

**Lernhandlung:** berechnen, bestimmen, umformen oder eine Gleichung angeben.

**Antwortform:** mathematischer Zahlenwert, Term, Termliste oder Gleichung.

**Zweck:** mathematisch gleichwertige Schreibweisen statt bloßer
Zeichenkettenvergleich.

### Auswahl

- **Wählen:** wenn mehrere äquivalente mathematische Schreibweisen korrekt
  sein sollen oder ein symbolischer Ausdruck geprüft wird.
- **Nicht wählen:** bei reiner Auswahl, offenem Begründungstext, Schätzung oder
  Größenantwort ohne geplante Einheitenprüfung.
- **Native Alternative:** eine native feste Texteingabe genügt nur, wenn genau
  eine Schreibweise zulässig sein soll und kein CAS-Mehrwert besteht.

### Umsetzung und Importe

Native Texteingabe mit dem passenden Algebrite-Validator. Importiere
Algebrite direkt. `@canvas` ist nur eine Eingabehilfe und verlangt zusätzlich
lia-canvas-ocr nach Algebrite; `@BerechneOCR` ist eine eigene
Rechenwegentscheidung. Syntax und Optionsgrenzen stehen in
[template-math.md](template-math.md).

### Aufgabenrhythmus

- **Erforderlich:** Rechenauftrag → Eingabefeld → direkt anschließender
  Validator.
- **Empfohlen:** nächster sinnvoller Rechenschritt als Hint und erklärende
  Musterrechnung bei prozessbezogenem Lernziel.
- **Bedingt:** Canvas, mehrere Eingaben, Explain, Resetter oder vollständiges
  OCR-Rechenwegquiz.
- **Normalerweise unnötig:** LLMQuiz und Toleranzvalidator bei exaktem Ziel.

### Varianten

- einfach: ein exakter Zahlenwert;
- anspruchsvoller: symbolisch äquivalenter Term oder mehrere Lücken;
- technikarm: native Eingabe bei genau einer akzeptierten Darstellung;
- eingabeunterstützt: Canvas zur Handschrifterkennung, ohne den CAS-Validator
  zu ersetzen.

### Grenzen und Anti-Patterns

- Verwende bei komplexen Solltermen Backticks nach dem Ausgabevertrag.
- CAS-Gleichwertigkeit beweist keinen geforderten Rechenweg.
- `@canvas` validiert nichts; ein fehlender Validator bleibt ein Prüfloch.
- Für Größen mit Einheit gilt stattdessen zusätzlich `AR-UNIT`.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| A | [`01_Algebraische_Grundlagen/02_Terme/Aufgabe_0017.md`, Z. 53–150](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/02_Terme/Aufgabe_0017.md#L53-L150) | mehrere CAS-geprüfte Rechenlücken | keine Parserwarnung |
| W | [`11/Mathematik/Lia11_01.md`, Z. 205–236](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_01.md#L205-L236) | symbolische Ableitung mit Backtick-Sollterm | keine Parserwarnung |
| W | [`5/Mathematik/Lia5_09.md`, Z. 111–200](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_09.md#L111-L200) | kurze Rechnungen mit CAS, Hint und Lösung | keine Parserwarnung |

## `AR-UNIT` — Größen und Einheiten

**Lernhandlung:** Größen berechnen, umrechnen und fachlich korrekt angeben.

**Antwortform:** Zahlenwert und Einheit gemeinsam im Antwortfeld.

**Zweck:** Dimension und Einheit sind Teil der bewerteten Antwort.

### Auswahl

- **Wählen:** sobald eine gesuchte physikalische oder geometrische Größe eine
  Einheit besitzt oder eine Einheitenumrechnung Lernziel ist.
- **Nicht wählen:** bei dimensionslosen Zahlen oder wenn nur die passende
  Einheit aus festen Optionen gewählt wird.
- **Native Alternative:** feste native Antwort nur bei bewusst exakt
  vorgegebener Schreibweise; gleichwertige Einheiten brauchen einen belegten
  einheitenbewussten Validator.

### Umsetzung und Importe

Verwende native Eingabe plus Algebrite. Bei `@Algebrite.check` und
`@Algebrite.check_expression` ist `units=1` erforderlich; `check2` und
`check_margin` folgen ihren dokumentierten Defaults. Einheit und Zahl stehen
gemeinsam in Eingabe, Sollwert, Rechnung und Antwortsatz. Direkter
Algebrite-Import; Canvas nur optional mit seiner direkten Abhängigkeit.

### Aufgabenrhythmus

- **Erforderlich:** Größe und Zieleinheit klären → gemeinsame Eingabe →
  einheitenbewusster Validator → konsistente Lösung.
- **Empfohlen:** Umrechnungs- oder Dimensionshinweis und Antwortsatz.
- **Bedingt:** Toleranz, Canvas, Explain und Resetter.
- **Normalerweise unnötig:** außerhalb des Felds vorgedruckte Einheit als
  vermeintliche Prüfung.

### Varianten

- einfach: Einheitenumrechnung mit natürlichem Zahlenwert;
- anspruchsvoller: abgeleitete Einheit wie Fläche oder Volumen;
- technikarm: Auswahl der Einheit plus getrennte feste Zahl, wenn genau diese
  Teilhandlungen geprüft werden sollen;
- mobil: ein gemeinsames kurzes Eingabefeld statt breiter Tabellen.

### Grenzen und Anti-Patterns

- `[[ 64 ]] cm³` prüft die Einheit nicht; verwende `[[ 64cm^3 ]]`.
- Gleiche Größenzeichen, Dimensionen und Umrechnungsfaktoren über alle
  Bausteine ab.
- Die Beleglage ist einseitig: In der gefilterten Aufgabensammlung wurde kein
  authored Aufgabenblock mit `units=1` gefunden. Der Archetyp folgt dennoch
  dem aktuellen Ausgabevertrag und der Algebrite-API.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| W | [`5/Mathematik/Lia5_10.md`, Z. 81–106](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_10.md#L81-L106) | Umrechnung mit gemeinsamer Zahl-Einheit-Eingabe | keine Parserwarnung |
| W | [`5/Mathematik/Lia5_11.md`, Z. 660–694](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_11.md#L660-L694) | Volumen mit abgeleiteter Einheit | keine Parserwarnung |
| W | [`11/Mathematik/Lia11_01.md`, Z. 1124–1143](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_01.md#L1124-L1143) | Länge aus einer Darstellung mit Einheit | keine Parserwarnung |

## `AR-ESTIMATE-TOLERANCE` — Schätzung, Näherung und Toleranz

**Lernhandlung:** schätzen, runden oder einen numerischen Näherungswert
bestimmen.

**Antwortform:** Wert in einem akzeptierten Intervall oder innerhalb einer
absoluten Toleranz.

**Zweck:** fachlich angemessene Wertebereiche statt eines einzigen exakten
Strings.

### Auswahl

- **Wählen:** wenn mehrere Näherungswerte fachlich akzeptabel sind oder eine
  Rundungsabweichung zugelassen werden muss.
- **Nicht wählen:** bei exakter Rechnung oder wenn die Streuung mit einem
  festen Sollwert nicht fachlich begründbar ist.
- **Native Alternative:** feste Eingabe nach ausdrücklich vorgegebener
  Rundungsstelle; dabei bleibt der genaue Rundungsvertrag sichtbar.

### Umsetzung und Importe

`@Algebrite.check_margin` prüft ein inklusives Intervall,
`@Algebrite.check2` eine absolute Toleranz. Importiere Algebrite direkt;
Canvas ist nur eine Eingabehilfe. Leite Grenzen aus Messgenauigkeit,
Rundungsauftrag oder fachlich vertretbarer Schätzspanne ab.

### Aufgabenrhythmus

- **Erforderlich:** Schätz-/Näherungsauftrag → Eingabe → begründeter
  Toleranzvalidator.
- **Empfohlen:** Strategiehint und transparente Angabe der akzeptierten Spanne
  in der Lösung.
- **Bedingt:** Bildmaterial, Einheit, Canvas und Explain.
- **Normalerweise unnötig:** exakter CAS-Check zusätzlich zum
  Toleranzvalidator.

### Varianten

- einfach: Menge auf einem Bild schätzen;
- anspruchsvoller: gerundete Größe aus einer mehrschrittigen Rechnung;
- technikarm: Intervallauswahl mit festen Optionen;
- barriereärmer: Bild mit aussagekräftigem Alternativtext und textlicher
  Beschreibung relevanter Merkmale.

### Grenzen und Anti-Patterns

- Keine willkürliche Prozenttoleranz als universellen Standard verwenden.
- Toleranz und Einheit müssen dieselbe Größe beschreiben.
- Ein Bild ohne zugängliche Alternative darf nicht die einzige
  Informationsquelle sein.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| A | [`01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0057.md`, Z. 55–104](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0057.md#L55-L104) | Bildschätzung mit Intervall | keine Parserwarnung |
| W | [`5/Mathematik/Lia5_02.md`, Z. 543–563](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_02.md#L543-L563) | Schätzspanne plus transparente Lösung | keine Parserwarnung |
| W | [`11/Mathematik/Lia11_01.md`, Z. 1419–1455](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_01.md#L1419-L1455) | gerundete Länge mit absoluter Toleranz und Einheit | keine Parserwarnung |

## `AR-MULTIPART-FLEX` — Mehrteilige Übung und responsives Layout

**Lernhandlung:** mehrere kurze, verwandte Teilhandlungen üben oder
vergleichen.

**Antwortform:** mehrere getrennte Quizblöcke, häufig mit `**a)**`, `**b)**`
und `**c)**`.

**Zweck:** kompakte Aufgabenfamilie ohne unnötige LiaScript-Unterseiten.

### Auswahl

- **Wählen:** wenn Teilaufgaben dasselbe Material, Verfahren oder Lernziel
  nutzen und auf einer Seite sinnvoll bleiben.
- **Nicht wählen:** bei langen Lesetexten, starker Schrittfolge oder
  eigenständigen Lernstationen; diese bleiben linear oder erhalten echte
  Seiten.
- **Native Alternative:** lineare Absätze und Quizblöcke. DynFlex wird nur bei
  echtem Nebeneinander-/Umbruchnutzen ergänzt.

### Umsetzung und Importe

Kleine Teilaufgaben erhalten Fettkennzeichnungen statt H3. DynFlex besteht aus
`dynFlex` und `flex-child` und verlangt einen direkten lia-DynFlex-Import.
Jede enthaltene Quizfamilie behält ihre eigenen Direktimporte. Ein
`flex-child` ersetzt keine für Resetter technisch nötige H2-Grenze.

### Aufgabenrhythmus

- **Erforderlich:** gemeinsamer Auftrag oder Material → klar getrennte
  Teilkennzeichnungen → je Teilhandlung eigener Quizblock.
- **Empfohlen:** einheitliche Schwierigkeit oder nachvollziehbarer Anstieg und
  mobil lesbarer Umbruch.
- **Bedingt:** DynFlex, eigene BE je Teil, getrennte Lösungen und Resetter.
- **Normalerweise unnötig:** Hash-Überschrift pro kurzer Teilaufgabe.

### Varianten

- einfach: zwei gleichartige Teilaufgaben;
- anspruchsvoller: gestufte Aufgaben mit wachsendem Transfer;
- technikarm: lineare Liste ohne DynFlex;
- mobil: wenige kurze Flex-Kinder, die unter 599 px Containerbreite sauber
  untereinander funktionieren.

### Grenzen und Anti-Patterns

- DynFlex ist ein Layoutwerkzeug, keine Lernhandlung und kein Pflichtcontainer.
- Vermische keine unabhängigen Prüfhandlungen in einem einzigen Quizstatus.
- Verkette keine Überschriftenmarker und erzeuge keine leeren Unterseiten.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| A | [`01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0001.md`, Z. 53–120](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0001.md#L53-L120) | vier kurze Flex-Teilaufgaben | keine Parserwarnung |
| A | [`02_Geometrie/02_Koordinatensystem/Aufgabe_0017.md`, Z. 57–112](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/02_Geometrie/02_Koordinatensystem/Aufgabe_0017.md#L57-L112) | gemeinsames Board, getrennte Punktaufgaben | sieben `operator_mismatch`-Hinweise im Gesamtdokument |
| W | [`5/Mathematik/Lia5_09.md`, Z. 111–200](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_09.md#L111-L200) | thematische Station mit parallelen Rechenaufgaben | keine Parserwarnung |

## `AR-OPEN-REASON` — Offene Erklärung, Begründung und Beurteilung

**Lernhandlung:** beschreiben, erklären, begründen, vergleichen oder
beurteilen.

**Antwortform:** zusammenhängender Freitext, bei Bedarf mit mehreren
inhaltlichen Kriterien.

**Zweck:** semantische Inhaltsprüfung und getrennte Sprachrückmeldung bei
offenen Antworten.

### Auswahl

- **Wählen:** wenn fachlich mehrere Formulierungen zulässig sind und Inhalt,
  Zusammenhang oder Argumentation bewertet werden sollen.
- **Nicht wählen:** bei Einzelzahl, festem Begriff, eindeutiger Auswahl oder
  symbolisch prüfbarer Mathematik.
- **Native Alternative:** unbewertetes Freitextfeld mit Musterlösung,
  Lehrkraft-Rubrik oder mehrere deterministische Teilfragen; bevorzugen, wenn
  LLM-Nutzung ausgeschlossen oder technisch ungeeignet ist.

### Umsetzung und Importe

Importiere lia-llm direkt. Wähle entweder Kriterien/Coverage oder das
ganzheitliche Operatorprofil und konfiguriere Lösung, Feedback, Engine,
Sprachoptionen und Denkbudget vollständig nach
[template-language.md](template-language.md). Wiederhole den vollständigen
Auftrag konsistent im Makroargument. Browser- und Modellverfügbarkeit bleiben
eine Laufzeitgrenze.

### Aufgabenrhythmus

- **Erforderlich:** offener Auftrag → Freitextfeld → passende LLM-Konfiguration
  mit Erwartungshorizont.
- **Empfohlen:** handlungsbezogener Hint, zusammenhängende Musterlösung und
  getrennte Inhalts-/Sprachsicht.
- **Bedingt:** `coverage`, Operatorprofil, Rechtschreibung und Satzbau passend
  zur erwarteten Antwortform.
- **Normalerweise unnötig:** CAS, Toleranz oder LLM-Sprachprüfung bei
  Stichwort-/Einwortantworten.

### Varianten

- einfach: zwei klar getrennte Kriterien;
- anspruchsvoller: Beurteilung mit Beleg und Gegenargument;
- technikarm: Freitext plus sichtbare Selbstprüfkriterien;
- geräteschonend: deterministische Teilfragen, wenn lokale Modellressourcen
  nicht realistisch verfügbar sind.

### Grenzen und Anti-Patterns

- Coverage wirkt nur im Kriterienformat und wird nicht mit Operatorprofilen
  vermischt.
- LLM-Rückmeldung ist keine garantierte fachliche Gesamtnote.
- Kriterien bleiben atomar; Sprachrichtigkeit wird nicht heimlich zum
  fachlichen Bestehenskriterium.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| A | [`02_Geometrie/07_Kongruenz/Aufgabe_0028.md`, Z. 38–68](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/02_Geometrie/07_Kongruenz/Aufgabe_0028.md#L38-L68) | Begründung mit Kriterien, Coverage und Lösung | keine Parserwarnung |
| W | [`5/Deutsch/Lia5_03.md`, Z. 179–200](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_03.md#L179-L200) | Leseverstehen mit mehreren Inhaltsaspekten | keine Parserwarnung |
| W | [`11/Mathematik/Lia11_01.md`, Z. 675–691](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_01.md#L675-L691) | mathematische Beurteilung mit vollständiger Coverage | keine Parserwarnung |

## `AR-ORTHOGRAPHY` — Rechtschreibung, Korrektur und Diktat

**Lernhandlung:** fehlerhaften Text verbessern, Zeichensetzung ergänzen oder
Gehörtes schreiben.

**Antwortform:** korrigierter Satz/Text oder mehrere Diktatlücken.

**Zweck:** sprachliche Änderung direkt am Ausgangstext statt losgelöster
Einzelwahl.

### Auswahl

- **Wählen:** wenn die Veränderung eines vorgegebenen Textes oder die genaue
  Hörschreibung selbst Lernziel ist.
- **Nicht wählen:** bei semantischer Freitextbewertung, bloßer Wortartauswahl
  oder ausschließlich strenger Groß-/Kleinschreibung.
- **Native Alternative:** eindeutige einzelne Wörter als native Lücken; bei
  längeren Korrekturen ist das Orthography-Template transparenter.

### Umsetzung und Importe

Importiere lia-orthography direkt. Verwende `@orthography` oder
`@orthographytext` mit Starttext und Lösung; `@diktat` nutzt die Kursstimme.
Setze Lösungsfreigabe und `doublespacehelp` bewusst. Beachte die dokumentierte
Normalisierung der Groß-/Kleinschreibung.

### Aufgabenrhythmus

- **Erforderlich:** präziser Korrektur-/Hörauftrag → editierbarer Text oder
  Diktatlücken → Solltext.
- **Empfohlen:** konkreter Sprachhinweis und erklärende Lösung.
- **Bedingt:** mehrzeiliges Feld, Diktat, Resetter und Bewertung.
- **Normalerweise unnötig:** LLMQuiz für eindeutig festgelegte Korrekturen.

### Varianten

- einfach: genau ein Fehler pro Satz;
- anspruchsvoller: zusammenhängender Text mit mehreren Fehlertypen;
- technikarm: native Einwortlücken;
- auditiv: Diktat mit kurzer Phrase und passender Narrator-Konfiguration.

### Grenzen und Anti-Patterns

- Der geprüfte Stand bewertet Groß-/Kleinschreibung nicht streng genug für
  eine ausschließlich darauf zielende Aufgabe.
- Teile den Starttext und die Lösung nicht in unbeabsichtigt verschiedene
  Inhalte auf.
- Die gefilterte Beleglage stammt nur aus W; A-Treffer lagen in
  Dokumentations-/Importpfaden und zählen nicht als reale Aufgabe.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| W | [`5/Deutsch/Lia5_00.md`, Z. 846–856](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_00.md#L846-L856) | Lückendiktat | keine Parserwarnung |
| W | [`5/Deutsch/Lia5_02.md`, Z. 160–225](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_02.md#L160-L225) | Kommasetzung am Ausgangssatz | keine Parserwarnung |
| W | [`5/Deutsch/Lia5_03.md`, Z. 327–365](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_03.md#L327-L365) | Rechtschreibkorrektur in kurzen Sätzen | keine Parserwarnung |

## `AR-TEXT-MARK` — Textanalyse und Markierung

**Lernhandlung:** Textstellen finden, Kategorien zuordnen oder sprachliche
Strukturen sichtbar machen.

**Antwortform:** farbige Markierung direkt im Text.

**Zweck:** Textbelege bleiben in ihrem sprachlichen Kontext.

### Auswahl

- **Wählen:** wenn Lernende konkrete Wörter oder Passagen im Ausgangstext
  identifizieren und gegebenenfalls kategorisieren sollen.
- **Nicht wählen:** bei freier Interpretation ohne eindeutige Textspanne oder
  bei sehr wenigen isolierten Begriffen, die eine Auswahlmatrix klarer prüft.
- **Native Alternative:** Multiple-Choice oder Matrix für kurze getrennte
  Elemente; sie verliert jedoch die Markierung im Textzusammenhang.

### Umsetzung und Importe

Importiere lia-marker direkt. Definiere eine fachlich eindeutige Farblegende,
verwende öffentliche `@mark...`-Ziele innerhalb von `markerquiz` und schließe
mit `@TextmarkerQuiz`. Hinweise stehen nach dem Wrapper. Timer, Resetter oder
weitere Templates werden nur bei ihrer tatsächlichen Funktion direkt ergänzt.

### Aufgabenrhythmus

- **Erforderlich:** Markierauftrag mit Legende → Zieltext → Markerquiz.
- **Empfohlen:** erklärende Lösung, warum die markierten Stellen zur Kategorie
  gehören.
- **Bedingt:** mehrere Farben, farbunabhängiges Ziel, Demonstrationsmarkierung
  oder Wiederholung.
- **Normalerweise unnötig:** LLMQuiz und frei erfundene Markerfarben.

### Varianten

- einfach: eine Kategorie und eine Farbe;
- anspruchsvoller: mehrere Kategorien mit eindeutiger Legende;
- technikarm: Auswahlmatrix mit Textausschnitten;
- barriereärmer: Farbnamen und Kategorien immer textlich nennen, nie nur über
  Farbe kommunizieren.

### Grenzen und Anti-Patterns

- Demonstrationsmakros `@marked...` sind keine Lernendenantworten.
- Ein Markerquiz braucht eine fachliche Auswertung, nicht nur farbige
  Dekoration.
- Die gefilterte Beleglage stammt nur aus W; A-Treffer lagen in README- oder
  Importdateien.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| W | [`5/Deutsch/Lia5_00.md`, Z. 702–740](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_00.md#L702-L740) | Satzglieder mit drei Farben | keine Parserwarnung |
| W | [`5/Deutsch/Lia5_02.md`, Z. 335–389](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_02.md#L335-L389) | Wortarten mit Farblegende | keine Parserwarnung |
| W | [`5/Deutsch/Lia5_04.md`, Z. 395–423](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_04.md#L395-L423) | kurze kategorienbezogene Markieraufgabe | keine Parserwarnung |

## `AR-ASSIGN-ORDER` — Zuordnung, Gruppierung und Reihenfolge

**Lernhandlung:** Elemente zuordnen, gruppieren oder in eine feste Reihenfolge
bringen.

**Antwortform:** native Drop-Ziele oder begründete Kachelstruktur.

**Zweck:** Beziehungen und Reihenfolgen handelnd sichtbar machen.

### Auswahl

- **Wählen:** wenn Ziehen/Zuordnen selbst zur verständlichen Lernhandlung
  beiträgt und die Zielidentitäten eindeutig sind.
- **Nicht wählen:** bei wenigen binären Entscheidungen, bei motorisch unnötig
  aufwendigem Dragging oder wenn eine feste Reihenfolge technisch nicht geprüft
  wird.
- **Native Alternative:** native Drops sind der belegte Standardbestand;
  Matrix oder Auswahl ist eine zugänglichere Alternative bei kleinen Mengen.

### Umsetzung und Importe

Native Drops benötigen kein Funktionstemplate. lia-kachel wird direkt
importiert, wenn austauschbare gleiche Kacheln, dynamische Gruppen oder seine
Bedienoberfläche einen konkreten Mehrwert bieten. `@Kachelfolge` akzeptiert
beliebige Reihenfolgen und darf nicht als feste Sortierprüfung verwendet
werden; dafür native zielweise Drops nutzen. Resetter-Grenzen beachten.

### Aufgabenrhythmus

- **Erforderlich:** klare Relation/Reihenfolge → sichtbare Quellen und Ziele →
  eindeutige Prüfung.
- **Empfohlen:** Randomisierung und erklärende Lösung.
- **Bedingt:** Kachelgruppen, unbekannte Anzahl, Resetter und getrennte
  H2-Seiten bei technisch erforderlichem Einzelreset.
- **Normalerweise unnötig:** Kacheltemplate für eine einfache native Zuordnung.

### Varianten

- einfach: Begriffe und Definitionen zuordnen;
- anspruchsvoller: vollständige mathematische oder sprachliche Reihenfolge;
- technikarm: nummerierte Auswahl oder Matrix;
- mobil: wenige kurze Kacheln und ausreichend große Zielbereiche.

### Grenzen und Anti-Patterns

- Zuordnung, Gruppierung und Reihenfolge besitzen verschiedene Semantik.
- Im gefilterten Bestand wurden reale native Drop-Aufgaben, aber keine
  authored `@Kachelfolge`-Aufgabe gefunden; Templateempfehlungen folgen daher
  der aktuellen API, nicht einer behaupteten Nutzungshäufigkeit.
- Literale Trennzeichen und gleiche sichtbare Quellen müssen nach der
  Kachel-API behandelt werden.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| A | [`01_Algebraische_Grundlagen/04_Bruchrechnung/Aufgabe_0161.md`, Z. 59–132](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/04_Bruchrechnung/Aufgabe_0161.md#L59-L132) | native feste Sortierreihenfolge | ein `operator_mismatch`; Auftrag manuell klar |
| A | [`01_Algebraische_Grundlagen/04_Bruchrechnung/Aufgabe_0165.md`, Z. 60–106](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/04_Bruchrechnung/Aufgabe_0165.md#L60-L106) | native Domino-Reihenfolge | ein `operator_mismatch` |
| W | [`11/Mathematik/Lia11_01.md`, Z. 1863–1886](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_01.md#L1863-L1886) | Funktions-Domänen zuordnen | keine Parserwarnung |

## `AR-COORDINATE` — Koordinaten, Konstruktion und dynamische Geometrie

**Lernhandlung:** Punkte setzen, Graphen zeichnen, Konstruktionen ausführen,
Messen oder geometrische Zusammenhänge erkunden.

**Antwortform:** interaktives Board, konstruierte Objekte oder statische
Darstellung plus separates Quiz.

**Zweck:** geometrisches Handeln und prüfbare Boardzustände verbinden.

### Auswahl

- **Wählen:** wenn Lage, Konstruktion oder dynamische Veränderung selbst
  Lerngegenstand ist.
- **Nicht wählen:** wenn eine statische Skizze nur Material für eine numerische
  Rechnung liefert; dann genügt gegebenenfalls die statische Variante plus
  `AR-CAS-CALC` oder `AR-UNIT`.
- **Native Alternative:** Bild/Diagramm plus natives Quiz; freies JSXGraph nur,
  wenn lia-coordinate die benötigte Darstellung nicht abdeckt.

### Umsetzung und Importe

Importiere JSXGraph vor lia-coordinate. Plane eindeutige Board-IDs, Board
zuerst, dann Objekte, Quiz und Hilfen. Verwende den statischen Coordinate-Import
nur für dessen belegtes Teilset und niemals gemeinsam mit dem interaktiven
Import. Bei Wiederholung gelten die Resetter-Grenzen pro Board-ID.

### Aufgabenrhythmus

- **Erforderlich:** geometrischer Auftrag → vorbereitetes Board/Werkzeuge →
  passendes Coordinate-Quiz oder getrennte Eingabeprüfung.
- **Empfohlen:** konkrete Bedienhilfe, mathematische Lösung oder
  Konstruktionsbegründung.
- **Bedingt:** DGS-Werkzeugprofil, Restriktionen, Toleranzen, statischer Modus,
  Resetter und DynFlex.
- **Normalerweise unnötig:** freies JavaScript oder beliebige JSXGraph-Optionen
  außerhalb der belegten API.

### Varianten

- einfach: Punkt an vorgegebene Koordinaten ziehen;
- anspruchsvoller: Konstruktion mit kombinierten Eigenschaften oder
  Funktionsrekonstruktion;
- technikarm: statische Zeichnung plus Rechen-/Auswahlfrage;
- mobil: begrenzte Werkzeugleiste und ausreichend großes Board ohne erzwungene
  Mehrspaltenbreite.

### Grenzen und Anti-Patterns

- Achsen, Koordinatenfachsprache und Einheiten folgen den Fachsprachregeln.
- Mehrere Kriterien für dasselbe Polygon gehören in ein kombiniertes Quiz.
- Toleranzen, Werkzeugfreigaben und Messanzeigen dürfen die Lösung weder
  verhindern noch ungewollt verraten.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| A | [`02_Geometrie/02_Koordinatensystem/Aufgabe_0017.md`, Z. 57–112](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/02_Geometrie/02_Koordinatensystem/Aufgabe_0017.md#L57-L112) | gemeinsames Board und Punktquizze | sieben `operator_mismatch`-Hinweise im Dokument |
| W | [`11/Mathematik/Lia11_01.md`, Z. 85–109](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_01.md#L85-L109) | DGS und Rekonstruktion einer Tangente | keine Parserwarnung |
| W | [`11/Mathematik/Lia11_01.md`, Z. 1115–1143](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_01.md#L1115-L1143) | statisches Board als Material für Größenrechnung | keine Parserwarnung |

## `AR-VISUAL-MATH` — Visuelle Mathematik und manipulierbare Darstellungen

**Lernhandlung:** Bruchteile darstellen, Flächen belegen, Strichlisten lesen
oder Zahlen-/Formsteine manipulieren.

**Antwortform:** visuell veränderter Zustand mit templateeigener Prüfung.

**Zweck:** mathematische Struktur handelnd und sichtbar erfassen.

### Auswahl

- **Wählen:** wenn Teilung, Fläche, Lage oder Form die eigentliche
  mathematische Repräsentation ist.
- **Nicht wählen:** wenn die Darstellung nur dekoriert oder eine einfache
  Zahleneingabe klarer prüft.
- **Native Alternative:** zugängliche statische Grafik plus natives Auswahl-
  oder Eingabequiz.

### Umsetzung und Importe

Für Brüche und Strichlisten lia-Mathe direkt importieren; Algebrite nur bei
zusätzlicher CAS-Prüfung. Für Polyominos gilt die direkte Reihenfolge JSXGraph,
lia-coordinate, lia-pentominos. Wähle Circle/Rectangle oder Pentomino nach der
tatsächlichen Repräsentation, nicht zur bloßen Abwechslung.

### Aufgabenrhythmus

- **Erforderlich:** visueller Handlungsauftrag → manipulierbare Darstellung →
  templateeigene Prüfung.
- **Empfohlen:** Erklärung der mathematischen Beziehung und zugängliche
  Aufgabenformulierung.
- **Bedingt:** Quizkommentar, Resetter, zusätzliche mathematische Eingabe oder
  Musterlage.
- **Normalerweise unnötig:** zweite manuelle Prüfung desselben Widgetzustands.

### Varianten

- einfach: vorgegebenen Bruch im Kreis oder Rechteck darstellen;
- anspruchsvoller: geeignete Form auswählen und Zielsumme legen;
- technikarm: statische Abbildung mit Auswahl oder Zahleneingabe;
- mobil: responsive Widgetbreite ohne starre DynFlex-Zweispalte.

### Grenzen und Anti-Patterns

- Übernimm keine internen Widgetantworten oder versteckten Quizwerte.
- Eine visuelle Aufgabe braucht Alternativtext beziehungsweise eine
  gleichwertige textliche Lernhandlung.
- Pentomino-Dock, einzelner Stein und Zielsumme besitzen unterschiedliche
  Prüfsemantik; Steinsummen werden nicht beliebig addiert.

### Belege

| Quelle | Original | Belegter Aspekt | Parserhinweis |
|---|---|---|---|
| A | [`01_Algebraische_Grundlagen/04_Bruchrechnung/Aufgabe_0171.md`, Z. 51–155](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/04_Bruchrechnung/Aufgabe_0171.md#L51-L155) | Brüche als Kreissektoren | ein `operator_mismatch` |
| A | [`01_Algebraische_Grundlagen/04_Bruchrechnung/Aufgabe_0173.md`, Z. 53–103](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/04_Bruchrechnung/Aufgabe_0173.md#L53-L103) | Brüche als Rechteckzellen | ein `operator_mismatch` |
| W | [`5/Mathematik/Lia5_03.md`, Z. 345–398](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_03.md#L345-L398) | Polyomino-Zielsummen mit verschiedenen Formen | keine Parserwarnung |

## Abschlussprüfung der Archetypenwahl

Vor dem Schreiben muss die Auswahl diese Fragen beantworten:

1. Welche Lernhandlung und Antwortform werden tatsächlich geprüft?
2. Genügt native LiaScript-Syntax? Wenn nein: Welchen konkreten Mehrwert bringt
   jedes zusätzliche Template?
3. Stimmen sichtbarer Imperativoperator, erwartete Lernhandlung, Antwortform,
   Quiz, Validator, Hinweis, operatorgerechte Lösung, BE und Themenangaben
   überein?
4. Sind alle direkten Abhängigkeiten im einzigen Hauptkopf vorhanden, ohne
   historischen Sammelimport?
5. Bleiben kleine Teilaufgaben auf derselben sinnvollen Seite und frei von
   unnötigen Hash-Überschriften?
6. Sind Beleggrenzen, Laufzeitgrenzen und Nutzerbeschränkungen berücksichtigt?
7. Wurde der fertige Entwurf mit dem passenden Profil aus dem Ausgabevertrag
   validiert?
