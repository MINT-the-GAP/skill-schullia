# SchulLia-Hausstil für neue Aufgaben und Kurse

Diese Referenz ist bei neuen Einzelaufgaben, vollständigen Ein-Aufgaben-Kursen,
anderen vollständigen Kursen und Wochenaufgaben sowie bei ihrer strukturellen
oder gestalterischen Überarbeitung zu lesen. Sie beschreibt den
nicht-gamifizierten SchulLia-Hausstil. Für technische Mussregeln gilt weiterhin
der [Ausgabevertrag](authoring-contract.md), für Syntax die
[LiaScript-Grundlage](liascript-basics.md) und für Makros, Optionen und Importe
die [Template-Auswahl](template-options.md). Gamification wird ausschließlich
über die gesonderte lia-loot-Route geplant.

Der Stilführer unterstützt Entscheidungen; er ist weder ein vollständiger
[Aufgabenarchetypen-Katalog](task-archetypes.md) noch ein starres Layoutschema.
Wähle bei vollständigen Wochen- und Mehr-Aufgaben-Kursen zuvor ein passendes
[Kurskompositionsprofil](course-composition-profiles.md) und dort anschließend
für jede Lernhandlung nach Antwortform die technische Grundstruktur. Eine
ausdrückliche Nutzervorgabe darf bevorzugte Standards und Varianten ändern,
aber keine technische Mussregel oder unbelegte Template-API außer Kraft setzen.

## Geltungsbereich

Lies diese Referenz, wenn du:

- eine neue eigenständig nutzbare Aufgabe oder einen Einfügeausschnitt
  erstellst,
- mehrere Aufgaben zu einem Kurs oder einer Wochenaufgabe verbindest,
- Überschriften, Aufgabenrhythmus, Hinweise, Lösungen, Feedback oder
  Template-Einsatz eines bestehenden Inhalts gestalterisch überarbeitest,
- aus Korpusbeispielen eine erkennbare SchulLia-Familienähnlichkeit ableitest.

Bei einer rein erklärenden, suchenden oder klassifizierenden Anfrage ohne neue
oder umgestaltete Lerninhalte ist diese Referenz nicht verpflichtend. Bei einer
nachgelagerten Gamification bleiben der fertige Fachtext und seine Reihenfolge
nach dem Hauptskill eingefroren; die vorliegende Referenz begründet dort keine
zusätzlichen Texte oder Seiten.

## Regelklassen und Vorrang

| Regelklasse | Bedeutung |
|---|---|
| **Verbindliche Regel** | Mussregel aus Hauptskill, Ausgabevertrag, offizieller LiaScript-Syntax oder belegter Template-API. Sie gilt unabhängig von ihrer Häufigkeit im Korpus. |
| **Bevorzugter Autorenstandard** | SchulLia-Standardfall, wenn Lernziel, Lerngruppe und Nutzerwunsch keine passendere Gestaltung verlangen. |
| **Akzeptable Variante** | Belegte oder didaktisch begründete Alternative, die dieselbe Lernhandlung verständlich und technisch vollständig unterstützt. |
| **Beobachtetes Bestandsmuster** | Commitgebundener Befund aus Aufgabensammlung oder Wochenaufgaben. Er liefert Evidenz, ist aber allein keine Vorschrift. |
| **Anti-Pattern** | Gestaltung, die technische Grenzen verletzt, den Lernweg unnötig zerteilt oder ein Bestandsmuster ohne fachlichen Grund kopiert. |

Bei Konflikten gilt: ausdrücklicher Nutzerauftrag innerhalb des technisch und
fachlich Zulässigen, dann verbindlicher Vertrag und aktuelle API, danach
bevorzugter Autorenstandard. Korpusbeispiele belegen Möglichkeiten; sie
überschreiben keine neuere kanonische Regel.

## Evidenzbasis und Grenzen

Die folgenden statistischen Befunde sind auf zwei lokale Snapshots gepinnt:

- `MINT-the-GAP/Aufgabensammlung`, Commit
  `c9ac1585a0545a54a185de885c272da3e4aacbef`;
- `MINT-the-GAP/Wochenaufgabe`, Commit
  `03e72a48a5ccfc46d91ea6770d54dfc9cec05efb`.

Der rohe Index enthält 1.272 aufgabentragende LiaScript-Dateien mit 2.813
erkannten Aufgabenblöcken in der Aufgabensammlung und 183 Dateien mit 3.029
Aufgabenblöcken in der Wochenaufgabe. Für die nachfolgende Stilauswertung wurden
Dateien mit `contains_dynamic_random_generation` ausgeschlossen. Bei den
Wochenaufgaben wurden außerdem nur regulär benannte Kurse nach dem Muster
`Klasse[/Fach]/LiaKlasse_Woche.md` beziehungsweise `Lia5_SK.md` berücksichtigt;
dadurch bleiben Tests, Demonstrationen, Arbeitsblätter und sonstige Sonderpfade
außen vor.

Die Auswertungsmenge umfasst damit:

| Quelle | LiaScript-Dateien | erkannte Aufgabenblöcke |
|---|---:|---:|
| Aufgabensammlung | 1.254 | 2.759 |
| regulär benannte Wochenkurse | 113 | 1.912 |

Beobachtete Näherungswerte in dieser Menge:

- In der Aufgabensammlung enthalten 97,3 Prozent der Aufgabenblöcke einen
  kurzen Fettdruck, der in den geprüften Originalen überwiegend den Operator
  hervorhebt; 71,9 Prozent enthalten kleine Buchstabenlabels und 59,6 Prozent
  DynFlex- beziehungsweise `flex-child`-Strukturen.
- In den regulären Wochenkursen betragen diese Anteile 89,2 Prozent,
  67,2 Prozent und 64,5 Prozent.
- Eine Aufgabendatei besitzt im Median eine H1 sowie keine H2, H3 oder H4. Bei
  90 Prozent der Dateien bleibt es ebenfalls bei höchstens einer H1 und ohne
  H2/H3. Ein regulärer Wochenkurs besitzt im Median zwei H1, sieben H2 und
  keine H3; auch das 90. Perzentil enthält keine H3.
- Beide Bestände importieren im Median 16 Templates pro aufgabentragender
  Datei. Das ist ein historisches Sammelimportmuster und ausdrücklich **kein**
  Sollwert für neue Kurse.

Der Parser meldet in der gefilterten Aufgabensammlung 499 mögliche
`operator_mismatch`-Vorkommen und in den Wochenkursen acht. Solche Meldungen
sind Prüfhinweise, keine automatisch bestätigten Autorenfehler. Die Prozentwerte
sind statische Näherungen; sie ersetzen weder die Originallektüre noch eine
fachlich-didaktische Beurteilung.

## Stil einer Einzelaufgabe

### Aufgabenfokus

Ein SchulLia-Aufgabenblock konzentriert sich auf eine erkennbare Lernhandlung.
Für jede neu erstellte bewertbare Aufgabe sind der sichtbare Imperativoperator
und die operatorgerechte Lösung nach dem
[verbindlichen Operator- und Lösungsvertrag](authoring-contract.md#verbindlicher-operator--und-lösungsvertrag)
Mussregeln. Für den gesamten Aufgabenrhythmus gilt als bevorzugter
Autorenstandard:

1. einen aussagekräftigen Titel auf der vom Ausgabeprofil vorgesehenen Seite,
2. nur das Material oder die kurze Einleitung, die zum Bearbeiten nötig ist,
3. einen fachlich präzisen Operator in einem direkten Arbeitsauftrag,
4. die Frage beziehungsweise Teilfrage unmittelbar vor ihrem Quiz,
5. eine zur erwarteten Antwort passende Eingabe und Prüfung,
6. konkrete Unterstützung und eine fachlich angemessene Rückmeldung oder
   Musterlösung,
7. BE und Themenangaben, wenn der Aufgabenblock bewertet wird.

Hebe den zentralen Operator bevorzugt fett hervor, etwa `**Berechne**` oder
`**Begründe**`. Bei getrennten Verbteilen darf die Hervorhebung dem natürlichen
Satz folgen, etwa `**Gib** … **an**`. Der sichtbare Arbeitsauftrag, ein
gegebenenfalls gesetzter Operator-Tag und das tatsächliche Anforderungsniveau
müssen zusammenpassen. Eine Fettschrift allein klassifiziert keinen Operator.

### Kleine Teilaufgaben und responsive Anordnung

Kurze zusammengehörige Teilaufgaben bleiben auf derselben sinnvollen Seite und
erhalten Kennzeichnungen wie `**a)**`, `**b)**` und `**c)**` statt eigener
Hash-Überschriften. Historische Originale verwenden auch unterstrichene
LaTeX-Labels wie `__$a)\;\;$__`; für neue gewöhnliche Labels ist die schlichte
Fettkennzeichnung aus dem Ausgabevertrag besser lesbar. Mathematische
Formatierung bleibt zulässig, wenn sie selbst Inhalt trägt.

Verwende DynFlex, wenn Material und Aufgaben oder mehrere kurze Teilaufgaben
auf unterschiedlichen Bildschirmgrößen sinnvoll nebeneinander beziehungsweise
untereinander arbeiten sollen. DynFlex ist kein Pflichtcontainer und kein
Ersatz für eine technisch erforderliche LiaScript-Abschnittsgrenze. Lange
Lesetexte, sequenzielle Erklärungen oder stark voneinander abhängige Schritte
dürfen linear bleiben.

### Quiz, Hinweis, Lösung und Wiederholung

Die Antwortform entscheidet über Quiz und Template. Eingabe, Validator und
zugehörige Hint-Zeilen bilden die im Ausgabevertrag definierte ungetrennte
Quizkette. Ein konkreter Hinweis unterstützt den nächsten sinnvollen
Bearbeitungsschritt, ohne die vollständige Lösung vorwegzunehmen.

Für neue bewertbare Aufgaben mit `@ADetails` bleibt `[[?]] @Explain` nach dem
Ausgabevertrag verbindlich. Das ist auch dann maßgeblich, wenn ältere
Wochenaufgaben nur einen konkreten Hint enthalten. Verwende eine erklärende
Musterlösung, wenn das Lernziel einen Rechenweg, eine Begründung, einen
Vergleich oder eine fachliche Deutung umfasst. Bei reinen Erkennungs- oder
Auswahlhandlungen kann eine präzise Rückmeldung genügen. Ergänze keine zweite
manuelle Lösung, wenn das eingesetzte Makro bereits eine vollständige Lösung
erzeugt. Nicht jede Aufgabe benötigt denselben Lösungsumfang; maßgeblich sind
Operator, Antwortform und die verbindliche Zuordnung im Ausgabevertrag.
Dynamische Aufgaben benötigen eine aus denselben Laufzeitwerten abgeleitete
Lösung und eine manuelle Prüfung statt eines erfundenen festen Ergebnisses.

Setze `@resetter` nur ein, wenn der konkrete Quiztyp und die gewünschte
Wiederholung dadurch zuverlässig unterstützt werden. Ein historisch häufiges
Reset-Makro ist keine Pflicht für jedes Quiz. Punkte und Themen in `@ADetails`
beziehen sich auf die tatsächlich bewertete Teilhandlung; mehrere unabhängige
Teilaufgaben dürfen eigene Angaben erhalten.

## Stil vollständiger Kurse und Wochenaufgaben

Ein vollständiger Kurs verbindet Aufgaben zu einem nachvollziehbaren
Arbeitsweg. H1 bezeichnet tatsächliche Hauptbereiche, H2 eigenständige Seiten
oder Aufgabenstationen und H3 nur substanzielle Unterseiten. Kleine Teilfragen,
Hinweise, Lösungen und Punkteangaben eröffnen keine zusätzliche Seite.

Wähle für den fach- und stufentypischen Kursaufbau das passende
[Kurskompositionsprofil](course-composition-profiles.md). Dessen beobachtete
Spannweiten sind Entscheidungshilfen und keine Quoten; Nutzerauftrag, Lernziel
und der feste Ausgabeprofilvertrag haben Vorrang.

Für eine Wochenaufgabe gilt der feste Rahmen des Ausgabevertrags. Der
bevorzugte Arbeitsrhythmus ist:

1. knapper Kursstart mit Zweck und Bedien- beziehungsweise Abgabehinweis,
2. fortlaufende, thematisch benannte H2-Aufgabenstationen,
3. innerhalb einer Station kompakte Teilaufgaben mit passenden Eingabeformen,
4. eine Selbsteinschätzung nach den fachlichen Stationen,
5. eine kurze, eindeutige Abgabeanweisung und der technische Footer.

Die Aufgabenzahl folgt dem Nutzerauftrag; sechs ist nur der Vorlagenstandard.
Wechsle Eingabe- und Darstellungsformen, wenn die Lernhandlungen dies tragen,
nicht um möglichst viele Templates vorzuführen. Prüfe die Gesamtfolge manuell
auf Lernprogression, Aufgabendichte, Schwierigkeit, Unterbrechungen und
kognitive Belastung. Diese Qualität lässt sich nicht aus einer Makrozahl
ableiten.

Die Selbsteinschätzung fragt mindestens die wahrgenommene Sicherheit und den
Anspruch ab. Bei einem längeren oder fachlich breiten Kurs dürfen zusätzlich
einzelne Aufgabenbereiche reflektiert werden. Das ist eine akzeptable Variante,
keine universelle Pflicht pro Station. Die Abgabeanweisung nennt knapp die
erforderliche Kontrolle und den tatsächlichen Übermittlungsweg; sie wiederholt
nicht den gesamten Kursstart.

Die belegten Wochenkurse enthalten Gamification. Für den hier beschriebenen
nicht-gamifizierten Basiskurs werden Loot-Makros, Geheimseiten und Spieltexte
nicht als Gestaltungsstandard übernommen. Sie bleiben Gegenstand der
nachgelagerten Gamificationroute.

## Sprache und Ton

- Formuliere Arbeitsaufträge direkt, altersangemessen und fachlich präzise.
- Verwende den Operator so, dass die erwartete Lernhandlung und Antwortform
  erkennbar sind. Ein allgemeines „Bearbeite“ ersetzt keinen fachlichen Auftrag.
- Halte Hinweise kurz und handlungsbezogen. Nenne beispielsweise den nächsten
  Rechenschritt oder ein zu prüfendes Sprachmerkmal statt nur „Denke noch
  einmal nach“.
- Gib bei erklärungsbedürftigen Lernzielen nicht nur das Endergebnis aus,
  sondern mache die tragende Beziehung oder Begründung sichtbar.
- Sprich Lernende respektvoll und motivierend an. Lange Einleitungen,
  moralischer Druck und wiederholte Bedienhinweise aus älteren Kursen sind
  beobachtete Varianten, keine Vorgabe für neue Texte.
- Halte mathematische Notation, Fachbegriffe, Größenzeichen und Einheiten über
  Aufgabe, Eingabe, Validator, Hinweis und Lösung konsistent. Es gelten die
  verbindlichen Fachsprachregeln des Hauptskills.

## Template-Auswahl als Gestaltungsentscheidung

Wähle ein Template nach der Lern- und Antwortform, nicht nach seiner bloßen
Verfügbarkeit:

| Lernhandlung | Geeignete Richtung |
|---|---|
| symbolisch gleichwertige Terme oder Gleichungen prüfen | Algebrite |
| Handschrift, Rechenweg oder Skizze erfassen | Canvas/OCR |
| offene Begründung, Erklärung oder Vergleich bewerten | vollständig konfiguriertes LLMQuiz |
| Schreibweisen untersuchen oder korrigieren | Orthography-Template |
| Textstellen finden und kategorisieren | Marker-Template |
| Koordinaten, Punkte oder Konstruktionen bearbeiten | Coordinate/DGS |
| Material oder kurze Teilaufgaben responsiv anordnen | DynFlex |

Lies für Syntax, Optionen, Abhängigkeiten und weitere Familien die vollständige
[Template-Auswahl](template-options.md) und nur die dort passend gerouteten
Detailreferenzen. Familienähnlichkeit entsteht durch den wiedererkennbaren
Aufgabenrhythmus und die passende Lernhandlung, nicht durch einen kopierten
Sammelheader. `lia-board-mode`, die Profilimporte und alle weiteren direkten
Imports folgen ausschließlich dem aktuellen Ausgabevertrag. Ein Template ohne
verwendete Funktion oder benötigten importgesteuerten Effekt wird nicht als
Dekoration importiert.

## Messbare Stilmerkmale

`Statisch` bezeichnet eine Prüfung von Syntax oder Indexdaten. `Manuell`
bezeichnet eine fachlich-didaktische Originalprüfung. Statistische Korpuswerte
bleiben Beobachtungen; die folgende Tabelle setzt keine unbegründete
Zahlenobergrenze.

| Merkmal | Regelklasse | Prüfmethode | zulässige Variation | Korpusbeleg |
|---|---|---|---|---|
| Überschriftenebenen | verbindlich | statisch: Ebenenfolge, Markerabstand und Seiteninhalt prüfen | zusätzliche Seite nur bei eigenständigem Inhalt oder belegter technischer Abschnittsgrenze | Median Aufgabensammlung: eine H1, keine H2/H3; Wochenkurse: zwei H1, sieben H2, keine H3 |
| Aufgabenstationen und Teilaufgaben | verbindlich / bevorzugt | statisch: H2-Stationen und kleine Labels getrennt zählen; manuell: Zusammengehörigkeit prüfen | Aufgabenzahl nach Nutzerauftrag; keine feste Teilaufgabenzahl | 71,9 Prozent beziehungsweise 67,2 Prozent der Aufgabenblöcke mit Buchstabenlabels |
| Operator | verbindlich für neue bewertbare Aufgaben | statisch: Imperativmuster und gegebenenfalls Operatorangabe; manuell: fachliche Passung von Auftrag und Lernhandlung | natürliche Satzstellung, getrennte Verbteile und eindeutig gemeinsam geltender Operator für eng verbundene Eingaben | 97,3 Prozent beziehungsweise 89,2 Prozent mit kurzem Fettdruck; Originale A1–A3 und W1–W3 |
| Frageposition | verbindlich | statisch: Aufgabenabsatz direkt vor Quizkette prüfen | Material darf unmittelbar davor stehen | A1–A3 und W1–W3 |
| Antwortform und Template | verbindlich / bevorzugt | statisch: Makro und Quiztyp inventarisieren; manuell: Lernhandlung abgleichen | natives Quiz oder anderes belegtes Template bei gleicher Eignung | Schätzen mit Toleranz A2, offene Begründung A3, Orthografie W2, CAS W1/W3 |
| Konkreter Hinweis | bevorzugt | statisch: Hint vorhanden; manuell: nächster Schritt ohne vollständige Lösung | bei selbsterklärender reiner Auswahl kann präzises Feedback genügen | W1–W3; A1/A2 zeigen zusätzlich den historischen `@Explain`-Weg |
| `@Explain` bei `@ADetails` | verbindlich für neue Inhalte | statisch: beide im selben Aufgabenblock und Thema belegt | entfällt nur, wenn kein bewertbarer `@ADetails`-Block entsteht | aktueller Ausgabevertrag; ältere W1/W2 sind keine Ausnahme |
| Operatorgerechte Lösung oder gleichwertiges Feedback | verbindlich für neue bewertbare Aufgaben | statisch: Lösungsblock oder belegte Makrolösung sowie eindeutig zu knappe Lösung erkennen; manuell: fachliche Vollständigkeit und exakte Aufgabenpassung prüfen | Umfang richtet sich nach Operator und Antwortform; vollständige Template-Lösung ersetzt den manuellen Block | Rechenwege W1/W3; Kriterien und Musterlösung A3 |
| BE und Themen | verbindlich bei bewerteten SchulLia-Aufgaben | statisch: `@ADetails` und Bezug zum Quizblock; manuell: Angemessenheit prüfen | unabhängige Teilaufgaben dürfen getrennte Angaben tragen | A1–A3 und W1–W3 |
| DynFlex | akzeptable Variante | statisch: Containergrenzen; manuell: responsiven Nutzen prüfen | lineare Folge bei Lesetext, Erklärung oder Abhängigkeit | 59,6 Prozent beziehungsweise 64,5 Prozent; A1/A2 und W1–W3 |
| direkte Imports | verbindlich | statisch: Verbraucher, Direktimport, Reihenfolge und Duplikate prüfen | nur Profilbasis plus tatsächlich benötigte Funktionen | Median 16 ist beobachteter Altbestand, ausdrücklich kein Sollwert |
| Selbsteinschätzung und Abgabe | verbindlich im Profil `weekly` | statisch: Reihenfolge und Footer; manuell: passende Reflexionsfragen | zusätzliche thematische Reflexion bei breiten Kursen | W1/W2 kurz, W3 stationsbezogen |
| Lernprogression und Belastung | bevorzugt | manuell: vollständigen Lernweg aus Lernendensicht durchlaufen | fach- und lerngruppenabhängig, keine universelle Quote | Vergleich der vollständigen Kurse W1–W3 |

## Anti-Patterns

- Verkettete Überschriftenmarker wie `# Aufgabe 1 ## Teil a)` oder fehlende
  Leerzeichen nach `#`.
- H3-Seiten für einzelne kurze Teilaufgaben, Hinweise, Lösungen oder
  Punkteangaben sowie dekorative oder leere Strukturseiten.
- Pauschale Sammelimporte oder das Vertrauen auf transitive Imports.
- Ein Template ohne passende Lernhandlung oder ein komplexeres Template nur
  zur optischen Abwechslung.
- Nur ein Endergebnis, obwohl der Operator eine Erklärung, Begründung,
  Herleitung oder Deutung verlangt.
- Generische Hinweise ohne konkreten nächsten Bearbeitungsschritt.
- Reset-, Timer- oder Feedbackmechanismen, deren Wirkung für den verwendeten
  Quiztyp nicht geprüft wurde.
- Blindes Kopieren einer Korpusaufgabe, ihrer langen Einleitung, ihrer
  Schwierigkeitsbilder, ihrer Gamification oder ihres gesamten Headers.
- Erhebung einer statistischen Häufigkeit zum Musswert ohne fachliche,
  technische oder nutzerseitige Begründung.
- Übernahme eines älteren Bestandsmusters entgegen einer aktuelleren
  kanonischen Regel, etwa fehlendes `@Explain` trotz neuem `@ADetails`.

## Kuratierte Belege

Die Belege zeigen Gestaltungsentscheidungen, keine kopierfertigen Archetypen.
Zeilenangaben gelten nur für den genannten Commit.

| ID | Original und Zeilen | Belegter Aspekt | Grenze der Übernahme |
|---|---|---|---|
| A1 | Aufgabensammlung, `01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0001.md`, [53–120](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0001.md#L53-L120) | Operator, kurze Rechenteilaufgaben, DynFlex, Eingabe, Explain, Reset und BE | Sammelimporte und historische Leerzeilen nicht übernehmen |
| A2 | Aufgabensammlung, `01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0057.md`, [55–104](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/01_Algebraische_Grundlagen/01_Grundrechenarten/Aufgabe_0057.md#L55-L104) | Bildmaterial, zwei Teilaufgaben, Canvas und Toleranzvalidator | keine allgemeine Pflicht zu Bildern, Timer oder DynFlex |
| A3 | Aufgabensammlung, `02_Geometrie/07_Kongruenz/Aufgabe_0028.md`, [38–68](https://github.com/MINT-the-GAP/Aufgabensammlung/blob/c9ac1585a0545a54a185de885c272da3e4aacbef/02_Geometrie/07_Kongruenz/Aufgabe_0028.md#L38-L68) | offene Begründung mit Kriterien, Coverage, Musterlösung und BE | konkrete Schwellen und Kriterien bleiben aufgabenspezifisch |
| W1 | Wochenaufgabe, `5/Mathematik/Lia5_09.md`, [111–200](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_09.md#L111-L200) und [1238–1257](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Mathematik/Lia5_09.md#L1238-L1257) | thematische H2-Station, Rechenteilaufgaben, konkrete Hinweise, Lösungen, Reflexion und Abgabe | Loot und fehlendes Explain in älteren Blöcken nicht als Basiskursstandard übernehmen |
| W2 | Wochenaufgabe, `5/Deutsch/Lia5_08.md`, [89–175](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_08.md#L89-L175) und [885–939](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/5/Deutsch/Lia5_08.md#L885-L939) | Orthografie-Template, kurze Teilaufgaben, fachliche Hints und bereichsbezogene Reflexion | Geheimseite und Gamification bleiben in der separaten Route |
| W3 | Wochenaufgabe, `11/Mathematik/Lia11_03.md`, [77–161](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_03.md#L77-L161) und [1601–1653](https://github.com/MINT-the-GAP/Wochenaufgabe/blob/03e72a48a5ccfc46d91ea6770d54dfc9cec05efb/11/Mathematik/Lia11_03.md#L1601-L1653) | dichtere Oberstufenaufgaben, vollständige Rechenwege und stationsbezogene Selbsteinschätzung | Umfang und Reflexionsdichte sind keine Vorgabe für jüngere oder kürzere Kurse |
