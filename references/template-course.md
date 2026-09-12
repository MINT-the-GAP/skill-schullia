# Kurs-, Layout-, Abgabe- und Fachmedien-Templates

Diese Referenz erfasst die öffentlichen Makros und Optionsfamilien der unten genannten commit-gepinnten Templates. Bei Kurserstellung passende Familien von Anfang an mitdenken: konsistente Quizbedienung, Wiederholung, Abgabe, Tafelbedienung, flexible Darstellung und fachliche Medien. Einen reichhaltigen Entwurf anhand des Lernziels ausarbeiten; nicht erst auf Nachfrage die dokumentierten Varianten suchen. Unvereinbare Varianten sind konkrete Alternativen und werden nicht gleichzeitig aktiviert.

Die Importform lautet `import: https://raw.githubusercontent.com/<Organisation>/<Repo>/<Revision>/README.md`. Die Tabelle nennt überprüfte Revisionen; `main` bezeichnet dagegen einen veränderlichen Stand. Die Original-READMEs wurden vollständig gelesen. Sie sind Dokumentation beziehungsweise Definitionen, keine realen Vergleichskurse. Bei einem neueren Korpus dessen README prüfen und Belege aktualisieren. Tatsächlich verwendete Templates direkt in den Kurskopf importieren; verschachtelte Demo-Imports ersetzen keine direkten Abhängigkeiten.

| Organisation / Repository | Geprüfte Revision | Öffentliche Oberfläche |
| --- | --- | --- |
| MINT-the-GAP/lia-globalquiz | `ea2e0b5608e8d0c08ddde859900474174e3e02e5` | `@global`, `@globalforced`, `@Global.version` |
| MINT-the-GAP/lia-timer | `4fde4c52cab2e1ea49e36b22d50d1cf4844e249b` | Quiz-Kommentarattribute, keine Kursmakros |
| MINT-the-GAP/lia-resetter | `dddf761f80c4f287b3652477f4dfab8e5a505589` | `@resetter`, `@ResetterRekonstruktion`, `@ResetterReconstruction`, `@Resetter.version` |
| MINT-the-GAP/lia-freeze-v2 | `e7088bd6ab0a9508658b02aca4081867f505fce3` | `@Abgabe`, `@Auswertung`, `@ADetails`, `@Exam` |
| MINT-the-GAP/lia-board-mode | `5c473bd8c99a1bc052b39c073bb06c747bb932ee` | `@autoscrolling`, Modusattribute, `horizontal-quiz` |
| MINT-the-GAP/lia-DynFlex | `d91ae5c4445070b96f03b5438241ae9cfebc8817` | HTML-Klassen und Containerattribute, keine Kursmakros |
| MINT-the-GAP/lia-annotation | `d7be96c56ff84e50df4341632b448db3396d226e` | Toolbar und Integrations-API, keine Kursmakros |
| MINT-the-GAP/lia-navigation | `065c05a7180318d5c9056a4033596b5de8f85fd7` | automatisches Inhaltsverzeichnis, keine Kursmakros |
| LiaTemplates/ABCjs | `385c4c55d2a2858aea6c78d199ecebeb99457719` | `@ABCJS.render`, `@ABCJS.renderWith`, `@ABCJS.eval`, `@ABCJS.evalWith` |
| LiaTemplates/AVR8js | `68dd1a3bf5544ff85ddef8c172aa63441ff76e75` | `@AVR8js.sketch`, `@AVR8js.project`, `@AVR8js.asm` |

## lia-globalquiz: vollständige Standards mit lokalen Ausnahmen

| Makro / Option | Bedeutung und Priorität |
| --- | --- |
| `@global(data-solution-button=3 data-hint-button=2)` | Standards ab dieser Position für alle folgenden Quizze. Lokale Attribute gewinnen. |
| `@globalforced(data-hint-button=4)` | Erzwungene Werte ab dieser Position überschreiben auch lokale Quizattribute. |
| Weitere Aufrufe | Ändern nur genannte Schlüssel; normale Standards heben erzwungene Werte nicht auf. Ein späteres `@globalforced` ersetzt den erzwungenen Wert desselben Schlüssels. |
| Beliebige `data-*` | Attribute, Flags und zitierte Werte sind möglich, etwa `data-randomize` und `data-text-solved="Gut begründet"`. Das bedeutet zunächst DOM-Weitergabe an Laufzeit-Templates. |
| `data-solution-button`, `data-hint-button` | Zusätzlich nachgebildete native Bedienung: Zahlen für Fehlprüfungen; `false`, `off`, `disabled` für dauerhaft verborgen. |
| `@Global.version` | Diagnose des geladenen Bundles; kein Lerninhalt. |

Vorrang: `@global < lokaler Quizkommentar < @globalforced`. Makros als eigene Körperzeilen platzieren. Beim Kursentwurf gemeinsame Hinweis- und Lösungsregeln vorbereiten und lokale Differenzierung mitplanen.

**Parsergrenze:** `data-randomize`, `data-score` und `data-max-trials` müssen weiterhin lokal im Quizkommentar stehen, damit LiaScript selbst sie auswertet. Ein global ergänztes Attribut ändert den internen Parserzustand nicht. Auch ein vom Core aufgrund eines höheren lokalen Buttonwerts noch nicht erzeugter Button lässt sich nicht durch einen niedrigeren globalen Wert vorzeitig zeigen. Allgemeine `data-*`-Weitergabe ist keine Garantie beliebiger nativer Wirkung.

Belege: MINT-the-GAP/lia-globalquiz, [README.md, Zeilen 11–27](https://github.com/MINT-the-GAP/lia-globalquiz/blob/ea2e0b5608e8d0c08ddde859900474174e3e02e5/README.md#L11-L27) (Makros), [Zeilen 32–59](https://github.com/MINT-the-GAP/lia-globalquiz/blob/ea2e0b5608e8d0c08ddde859900474174e3e02e5/README.md#L32-L59) (Position) und [Zeilen 104–140](https://github.com/MINT-the-GAP/lia-globalquiz/blob/ea2e0b5608e8d0c08ddde859900474174e3e02e5/README.md#L104-L140) (Priorität, Werte, Grenzen).

## lia-timer: Hinweise und Lösungen zeitlich freigeben

Keine `@timer`-Makros erfinden. Die vollständige öffentliche Oberfläche besteht aus diesen Attributen im Kommentar unmittelbar vor dem Quiz:

| Attribut | Werte / Vorgabe |
| --- | --- |
| `data-solution-timer` | Dauer bis zur Lösung; ohne Attribut kein Lösungstimer |
| `data-solution-timer-start` | `immediate` (Vorgabe), `oncheck`, `onclick` |
| `data-solution-timer-badge` | `on` (Vorgabe), `off` |
| `data-solution-timer-start-label` | Freier Buttontext; Vorgabe `Start timer` |
| `data-hint-timer` | Dauer bis zum Hinweis; unabhängig vom Lösungstimer |
| `data-hint-timer-start` | `immediate` (Vorgabe), `oncheck`, `onclick` |
| `data-hint-badge` | `on` (Vorgabe), `off`; genau diese Schreibweise |
| `data-hint-timer-start-label` | Freier Buttontext; Vorgabe `Start timer` |

Zeitformate: Sekunden als `90`, `30s`, `30sec`; Minuten als `2min`, `2m`; Stunden als `1h`, `1hr`; kombiniert `1min 30s`; `m:ss` wie `1:30`; Millisekunden als `500ms`. `immediate` beginnt beim Laden der Folie, `oncheck` beim ersten Prüfen. `onclick` bietet einen Startbutton und verbirgt den Prüfbutton bis zum Start. Hinweistimer mit vorhandenen `[[?]]`-Hinweisen kombinieren. Bei selbstständigen Übungsphasen beide Timer und unterschiedliche Freigabezeiten mitdenken; ein Freigabetimer ist kein hartes Bearbeitungszeitlimit.

Bei Kombination mit globalen Buttonregeln die tatsächliche Erreichbarkeit von Hinweis und Lösung prüfen. Die Timer-Dokumentation belegt keine pauschale Prioritätsregel gegenüber Freeze-Send oder weiteren Button-Plugins.

Belege: MINT-the-GAP/lia-timer, [README.md, Zeilen 36–52](https://github.com/MINT-the-GAP/lia-timer/blob/4fde4c52cab2e1ea49e36b22d50d1cf4844e249b/README.md#L36-L52), [Zeilen 54–153](https://github.com/MINT-the-GAP/lia-timer/blob/4fde4c52cab2e1ea49e36b22d50d1cf4844e249b/README.md#L54-L153) und [Zeilen 162–175](https://github.com/MINT-the-GAP/lia-timer/blob/4fde4c52cab2e1ea49e36b22d50d1cf4844e249b/README.md#L162-L175).

## lia-resetter: erneutes Üben vollständig vorbereiten

| Makro | Syntax und Wirkung |
| --- | --- |
| `@resetter` | Genau einmal als eigene Zeile direkt nach jedem zurücksetzbaren Quiz. Setzt nativen Status und unterstützten Widgetzustand zurück. |
| `@ResetterRekonstruktion` | Beispielsweise ``@ResetterRekonstruktion(`board-id;2x-1;0.1`)``: Board-ID, Zielterm, Toleranz; benötigt Coordinate-Board und passende Funktionsschar. Danach ebenfalls `@resetter`. |
| `@ResetterReconstruction` | Englischer Alias desselben Rekonstruktionsmakros mit identischen Argumenten. |
| `@Resetter.version` | Bundleversion für Diagnose. |

Für Übungskurse den Einzelreset bei passenden Quizfamilien von Anfang an vorsehen: native Auswahl-, Matrix-, Text-, Lückentext- und Generic-Quizze; Kachel-, Kachelfolge- und KachelfolgeN-Quizze; Orthographie, Orthographietext, Diktat; alle vier Bruchquizvarianten; beide Textmarker-Quizvarianten sowie die in der README belegten Coordinate-Quizfamilien. Aus dieser Liste keine ungeprüfte Zusage für andere interaktive Templates ableiten.

Bei Coordinate stellt der Reset auch Boardausschnitt, Größe, Makroobjekte, DGS-Konstruktionen, Schar- und Reglerwerte sowie Register wieder her. Pro Abschnitt darf nur **ein zurücksetzbares Coordinate-Quiz dieselbe Board-ID** verwenden. Drop-/Kachelquizze und andere Quiztypen benötigen im unveränderten LiaScript-Core getrennte `##`-Abschnitte für verlässlichen Einzelreset. Der in der README genannte Core-Patch ist nicht im Template-Bundle enthalten.

Die eigenen Rekonstruktionsnamen brauchen das Präfix `Resetter`; `@Rekonstruktion` / `@Reconstruction` gehören zu lia-coordinate. Der alte Resetter-Tag `1.0.0` enthält noch kollidierende Namen; für diese API den oben geprüften Commit verwenden. Kachel und Coordinate jeweils aus genau **einer** Variante importieren, nicht gleichzeitig aus `main` und `Proposal`. Die README beschreibt Geometriequizze auf `Proposal`; vor Branchwahl den tatsächlich gepinnten Coordinate-Stand anhand seiner eigenen Referenz prüfen. Benötigte Fachtemplates und JSXGraph direkt importieren. Interne Makros mit abschließendem `_` nicht von Hand aufrufen.

Belege: MINT-the-GAP/lia-resetter, [README.md, Zeilen 21–104](https://github.com/MINT-the-GAP/lia-resetter/blob/dddf761f80c4f287b3652477f4dfab8e5a505589/README.md#L21-L104) (Definitionen), [Zeilen 126–253](https://github.com/MINT-the-GAP/lia-resetter/blob/dddf761f80c4f287b3652477f4dfab8e5a505589/README.md#L126-L253) (Migration, Importe, Grenzen), [Zeilen 539–558](https://github.com/MINT-the-GAP/lia-resetter/blob/dddf761f80c4f287b3652477f4dfab8e5a505589/README.md#L539-L558) (Rekonstruktion) und [Zeilen 610–634](https://github.com/MINT-the-GAP/lia-resetter/blob/dddf761f80c4f287b3652477f4dfab8e5a505589/README.md#L610-L634) (Platzierung).

## lia-freeze-v2: Punkte, Abgabe, Auswertung und Prüfung

| Makro / Option | Bedeutung und Vorgabe |
| --- | --- |
| `@Abgabe` | Auf der Abschlussfolie: Name, Linkerstellung, Kopieren; nach Freeze außerdem PDF-Druck. |
| `@Auswertung` | Auswertung des eingefrorenen Bearbeitungsstands am Kursende. Ohne Zusatzflags keine dadurch angeforderte Zusatzprotokollierung. |
| `@Auswertung(F12;Tab;Time;Send)` | Vier Optionen einzeln und mit Semikolon kombinierbar; nach Bedarf auswählen. |
| `F12` | Technische Tastatur-/Viewportsignale. Keine sichere Feststellung geöffneter Entwicklertools, kein Punkteabzug. |
| `Tab` | Technische Fokus-/Sichtbarkeitssignale; bestätigte eigene MathPath-Explain-Overlays werden eng begrenzt ausgenommen. |
| `Time` | Bearbeitungsminuten je Folie in der Auswertung. |
| `Send` | Live-Prüfen protokolliert neutral, verbirgt Korrektheitsfeedback und Auflösen; Bewertung beim Erzeugen des Freeze-Links. Lernenden-Prüfklicks werden je Aufgabe gezählt. |
| `@ADetails(2;Grammatik,Rechtschreibung)` | Nach dem Quiz: Punktwert, dann optionale kommaseparierte Tags. README-Vorgabe für Punkte: `1`; explizite Werte für bewertete Aufgaben bevorzugen. |
| `@Exam(60)` | Dauer in Minuten auf eigener Einstiegsfolie. Erst Startbutton beginnt Countdown und Vollbildanfrage; bei Ablauf automatische Abgabe und Navigationssperre zur Abgabefolie. |

Bei bewerteten Kursen das komplette Paket aus Aufgabenpunkten, Tags, Abgabe und Auswertung mitdenken. `Send` passt zu einer verzögerten Prüfungsauswertung; für laufendes formatives Feedback die normale Variante verwenden. `@Exam` gehört zu einer gewählten Prüfungssituation und wirkt nur im Live-Modus. Eine abgelehnte Vollbildanfrage blockiert den Prüfungsstart nicht. F12-, Tab- und Vollbildsignale sind technische Hinweise, keine Schuldnachweise und ändern keine Quizpunkte. Die Benutzeroberfläche folgt der Kursangabe `language: de` (einschließlich regionaler Varianten); sonst Englisch.

Zusätzliche, im Quellparser belegte ADetails-Schreibweisen: Punkteschlüssel `point`, `points`, `be`, `punkt`, `punkte` mit `:` oder `=`; Tagschlüssel `tag` / `tags` mit `:` oder `=`; Punktwerte mit Dezimalpunkt oder Dezimalkomma; Teilwerte mit `|`, deren Summe den Punktwert bildet. Beispielsweise ``@ADetails(`points=1|2;tags=Begründen,Transfer`)``. Zahlen mit Einheit wie `1=BE` sind ebenfalls belegt. Nichtnegative endliche Werte werden erwartet; der erste gültige Punktwert gewinnt. Dies sind Parseroptionen, keine Zusage einer automatischen fachlichen Teilbewertung; Teilpunkte nicht unbesehen aus einem beliebigen Quiz ableiten. Die Kurzform mit explizitem Gesamtwert bleibt für gewöhnliche Aufgaben gut lesbar.

Der PDF-Export besucht und rendert alle Folien, wandelt Canvas-Inhalte für den Druck um und hängt die Auswertung mit aktuellen Lehrkraftkorrekturen an. Abgabe- und Bewertungsmarker gehören nach ihren Quizzen, nicht in die generierte native Buttonzeile. Die Demo-Imports sind kein allgemeines Kompatibilitätsversprechen für jede Kombination; alle tatsächlich verwendeten Fachtemplates direkt importieren und ihre Zustandsrestauration berücksichtigen.

Belege: MINT-the-GAP/lia-freeze-v2, [README.md, Zeilen 103–249](https://github.com/MINT-the-GAP/lia-freeze-v2/blob/e7088bd6ab0a9508658b02aca4081867f505fce3/README.md#L103-L249) (öffentliche Makros), [Zeilen 251–274](https://github.com/MINT-the-GAP/lia-freeze-v2/blob/e7088bd6ab0a9508658b02aca4081867f505fce3/README.md#L251-L274) (DOM- und Resetter-Wechselwirkung), [Zeilen 370–374](https://github.com/MINT-the-GAP/lia-freeze-v2/blob/e7088bd6ab0a9508658b02aca4081867f505fce3/README.md#L370-L374) (`1=BE`) und [src/adetails-dom.ts, Zeilen 133–204](https://github.com/MINT-the-GAP/lia-freeze-v2/blob/e7088bd6ab0a9508658b02aca4081867f505fce3/src/adetails-dom.ts#L133-L204) (erweiterte Punkt- und Tagoptionen, statisch geprüft).

## lia-board-mode: Tafelbedienung und modusspezifischer Inhalt

| Oberfläche | Optionen / Verhalten |
| --- | --- |
| `@autoscrolling(off)` / `@autoscrolling(on)` | Auf dieser und folgenden Folien gültig bis zum nächsten Schalter. Vor dem ersten Aufruf `on`; jeder andere Wert als `off` gilt als `on`. |
| `<div data-lia-only="…">` | `slides`, `presentation`, `textbook` für modusspezifische Blöcke. |
| `<!-- horizontal-quiz -->` | Unmittelbar vor Single-/Multiple-Choice. Horizontal bei ausreichender Breite, bis 760 px Standardlayout. |
| AA-Schriftsteuerung | Präsentationsmodus: 14–48 px, gespeichert; automatische Ausgangsanhebung auf 18/24/32 px gemäß Basisfont. |
| Breite / Werkzeugleisten | Rund 98,5 % Breite in Presentation und Slides; Header und TTS-Fußbereich einklappbar. |
| Presenter | `PageDown` vor, `PageUp` zurück, `.` / `B` Schwarzbild, `Escape` hebt Schwarzbild auf; automatisch aktiv. |

Bei projizierten Kursen Schrift, Platzangebot, horizontale Auswahl und Autoscrolling zusammen berücksichtigen. Übersprungene, noch nie gerenderte Folien liefern keine Körpermakros für vererbtes Autoscrolling; falls direkte Sprünge solche Schalter erben müssen, dokumentiert die README `persistent: true`. Rückwärtsnavigation öffnet die vorige Folie bei ihrem letzten Animationsschritt; dadurch können an Schritte gebundene Skripte, Medien oder Narration erneut laufen. Inhaltsverzeichnissprünge behalten den normalen Einstieg bei Schritt null. Bei modusgebundenen Pflichtinhalten muss der benötigte Modus zugänglich sein.

Belege: MINT-the-GAP/lia-board-mode, [README.md, Zeilen 43–77](https://github.com/MINT-the-GAP/lia-board-mode/blob/5c473bd8c99a1bc052b39c073bb06c747bb932ee/README.md#L43-L77), [Zeilen 93–141](https://github.com/MINT-the-GAP/lia-board-mode/blob/5c473bd8c99a1bc052b39c073bb06c747bb932ee/README.md#L93-L141) und [Zeilen 154–180](https://github.com/MINT-the-GAP/lia-board-mode/blob/5c473bd8c99a1bc052b39c073bb06c747bb932ee/README.md#L154-L180).

## lia-DynFlex: flexible Mehrspaltenlayouts

Ein `<section class="dynFlex">` oder `<div class="dynFlex">` enthält `<div class="flex-child">`-Elemente. Es gibt keine öffentlichen DynFlex-Makros.

| Containerattribut | Vorgabe / Zweck |
| --- | --- |
| `data-gap` | `20px`, Abstand; bloße Zahl wird als Pixelwert behandelt |
| `data-hit` | `22px`, Trefferfläche des Größenreglers |
| `data-basis` | `25%`, Ausgangsbreite |
| `data-min` | `10%`, minimale Breite |
| `data-max` | `100%`, maximale Breite |
| `data-store` | Optionaler eigener Schlüssel für gespeicherte Spaltenbreiten |

Vergleichsdarstellungen, Material neben Aufgaben und parallele Teilaufgaben als konkrete Layoutoptionen vorbereiten. Leerzeilen zwischen Quizblöcken erhalten getrennte Prüfbuttons; die Spaltenhülle erzeugt keine zusätzliche fachliche Quizart. Unter 420 px wechselt das Layout auf eine Spalte. Mit Resetter gelten dessen Abschnittsgrenzen weiterhin; ein `flex-child` ersetzt keine erforderliche neue `##`-Folie.

Belege: MINT-the-GAP/lia-DynFlex, [README.md, Zeilen 37–64](https://github.com/MINT-the-GAP/lia-DynFlex/blob/d91ae5c4445070b96f03b5438241ae9cfebc8817/README.md#L37-L64), [Zeilen 114–147](https://github.com/MINT-the-GAP/lia-DynFlex/blob/d91ae5c4445070b96f03b5438241ae9cfebc8817/README.md#L114-L147), [Zeilen 181–250](https://github.com/MINT-the-GAP/lia-DynFlex/blob/d91ae5c4445070b96f03b5438241ae9cfebc8817/README.md#L181-L250) und [src/flex.ts, Zeilen 130–135](https://github.com/MINT-the-GAP/lia-DynFlex/blob/d91ae5c4445070b96f03b5438241ae9cfebc8817/src/flex.ts#L130-L135).

## lia-annotation: handschriftliche Tafelarbeit

Nach Import steht eine Toolbar für Cursor, Stift, Radierer, Undo, Redo, Annotationen ein-/ausblenden und manuelles Koordinatensystem-Platzieren zur Verfügung. Der Stift bietet zehn Farben, 1–24 px Breite und 10–100 % Deckkraft; der Radierer 4–80 px und Löschen aller Striche der aktuellen Folie. Keine erfundenen `@annotation`- oder `@pen`-Makros verwenden.

Bei Rechenwegen und Tafelbesprechungen die Annotation früh mitdenken. Für OCR-Rechteckauswahl und Übernahme ins nächste Antwortfeld zusätzlich lia-canvas-ocr direkt importieren. Erkannter Text wird als LaTeX eingefügt und erhält eine TeX-Vorschau. Skizzierte Achsen können nach Bestätigung in ein DGS-System überführt werden; dieser Erkennungsweg ist experimentell. JSXGraph beziehungsweise lia-coordinate muss für das interaktive Board vorhanden sein; ohne erreichbare JSXGraph-Laufzeit entsteht eine statische Achsen-Vorschau.

Die dokumentierte Integrations-API unter `window.__LIA_ANNOTATION__` umfasst `setVisible(bool)`, `toggleVisible()`, `exportState()`, `importState(state)`, `exportFreezeState()`, `importFreezeState(state)`, `hasFreezeData()`, `setReadOnly(true|false|null)`, `clearSlide()` und `clearAllSlides()`. `null` beim Schreibschutz bedeutet automatische Erkennung. Zusätzlich exportiert der geprüfte Quellcode `isOcrAvailable`, `recognizeLatestAnnotationText`, `submitOcrTextToNearestQuiz`, `transferToNearestQuiz`, `startDgsPlacementMode`, `refresh`, `getStore` und `getSlideKey`. Das sind Integrationshooks, keine weiteren Kursmakros; gewöhnliche Kursgenerierung nutzt den Import und die Toolbar.

Belege: MINT-the-GAP/lia-annotation, [README.md, Zeilen 56–103](https://github.com/MINT-the-GAP/lia-annotation/blob/d7be96c56ff84e50df4341632b448db3396d226e/README.md#L56-L103), [Zeilen 119–162](https://github.com/MINT-the-GAP/lia-annotation/blob/d7be96c56ff84e50df4341632b448db3396d226e/README.md#L119-L162) und [src/api.ts, Zeilen 978–1004](https://github.com/MINT-the-GAP/lia-annotation/blob/d7be96c56ff84e50df4341632b448db3396d226e/src/api.ts#L978-L1004).

## lia-navigation: gegliedertes Inhaltsverzeichnis

Der Import aktiviert einen ein-/ausklappbaren hierarchischen Navigationsbaum mit Lesezeichen, Hervorhebung der aktuellen Folie, Ebenengestaltung und gespeichertem Zustand. Die gepinnte README definiert keine öffentlichen Kursmakros oder Autor-Konfigurationsattribute. Für längere, gegliederte Kurse mitdenken; die Überschriftenhierarchie bleibt die strukturelle Grundlage. Keine `@navigation(...)`-Optionen erfinden und aus diesem Template keine Portal-, Geheimfolien- oder Zugangssperren-API ableiten.

Beleg: MINT-the-GAP/lia-navigation, [README.md, Zeilen 1–44](https://github.com/MINT-the-GAP/lia-navigation/blob/065c05a7180318d5c9056a4033596b5de8f85fd7/README.md#L1-L44).

## ABCjs: Musik anzeigen, hören und bearbeiten

| Makro | Verwendung |
| --- | --- |
| `@ABCJS.render` | An der öffnenden `abc`-Codezaunzeile: Noten und Wiedergabe mit Vorgaben |
| `@ABCJS.renderWith(...)` | An derselben Stelle, mit HTML-artigen Attributen, etwa `channel="10" audio="true" notes="false"` |
| `@ABCJS.eval` | Eigene Zeile nach dem geschlossenen `abc`-Codeblock; editierbare, ausführbare Komposition |
| `@ABCJS.evalWith(...)` | Editorvariante mit denselben Optionen, etwa `autoplay="false"` |

| Option | Bedeutung / dokumentierte Vorgabe |
| --- | --- |
| `audio` | Audiosteuerung anzeigen; `true` |
| `autoplay` | Sofortiger Wiedergabestart; deaktiviert |
| `channel` | MIDI-Kanal; `10` bedeutet Percussion |
| `debug` | Visuelle ABCJS-Debugdarstellung für Boxen und Raster |
| `notes` | Noten anzeigen; aktiviert; `false` ermöglicht reine Hördarstellung |
| `program` | MIDI-Instrumentnummer, falls nicht im ABC-Text gesetzt |
| `responsive` | Responsive Notendarstellung aktiviert; `false` führt auf kleinen Bildschirmen zu Scrollbalken |
| `tablature` | Tabulatur-Konfigurationsobjekte; README-Beispiel mit Instrument `violin` und Stimmung `G,`, `D`, `A`, `e` |
| `voicesOff` | Melodie stummschalten, Begleitung/Metronom und Animation beibehalten |
| `chordsOff` | Akkordsymbole nicht vertonen; Metronom bleibt möglich |
| `stereo` | Stereopanorama; Vorgabe `false` |

Alle Optionen können zusätzlich als `% option: wert` im ABC-Text gesetzt werden; solche Kommentare überschreiben Makroeinstellungen. Die README-Editorprobe ist eine Beispielkonfiguration, keine Defaulttabelle (`program: 60` und `stereo: true` dort nicht zu universellen Vorgaben erklären). Beim Musikunterricht Notenansicht, Hörvariante ohne Noten, Instrumentierung, Stimmen-/Akkordisolierung und eigenen ABC-Editor als unterschiedliche didaktische Möglichkeiten vorbereiten. Tabulatur-Unteroptionen sind im lokalen README-Ausschnitt nicht vollständig spezifiziert; für neue Instrumentkonfigurationen die verlinkte primäre ABCjs-Dokumentation gezielt prüfen.

Belege: LiaTemplates/ABCjs, [README.md, Zeilen 20–35](https://github.com/LiaTemplates/ABCjs/blob/385c4c55d2a2858aea6c78d199ecebeb99457719/README.md#L20-L35), [Zeilen 79–87](https://github.com/LiaTemplates/ABCjs/blob/385c4c55d2a2858aea6c78d199ecebeb99457719/README.md#L79-L87), [Zeilen 132–222](https://github.com/LiaTemplates/ABCjs/blob/385c4c55d2a2858aea6c78d199ecebeb99457719/README.md#L132-L222) und [Zeilen 224–238](https://github.com/LiaTemplates/ABCjs/blob/385c4c55d2a2858aea6c78d199ecebeb99457719/README.md#L224-L238).

## AVR8js: Arduino- und Assembly-Experimente

| Makro | Argumente und Bindung |
| --- | --- |
| `@AVR8js.sketch` / `@AVR8js.sketch(container-id)` | Eigene Zeile nach einem C++-/Arduino-Codeblock; setzt den Dateinamen `sketch.ino`. Ohne ID werden sichtbare Wokwi-Elemente des Abschnitts gebunden. |
| `@AVR8js.project(container-id,datei1,datei2,…)` | Nach mehreren Codeblöcken. Dateinamen müssen in Blockreihenfolge passen; eine Datei muss `sketch.ino` heißen. Leeres erstes Argument erlaubt, zum Beispiel `@AVR8js.project( ,params.h,sketch.ino)`. Der geprüfte Makrokopf bietet neun Dateinamensargumente `@1` bis `@9`. |
| `@AVR8js.asm` / `@AVR8js.asm(container-id)` | Assembly-Codeblock; eigenes asynchrones Build-/Ausführungsverfahren. Erklärabschnitt ist noch `todo`, Definition und Assembly-Beispiel sind vorhanden. |

Mehrere Experimente auf derselben Folie über eindeutige Container-IDs isolieren. Wokwi-Elemente werden über ihre `pin`-Attribute angeschlossen; `simulation-time` zeigt optional die simulierte Zeit. Die README enthält LEDs und Taster (`color`, `pin`, `label`), 7-Segment (`digits`, `pin`), Buzzer, Neopixel-Matrix (`pin`, `cols`, `rows`) und SSD1306-Beispiele sowie Arduino-Mega/-Uno/-Nano-, DHT22-, LCD1602-, Membrane-Keypad-, Neopixel-, Potentiometer-, Widerstands-, Rotary-Dialer- und Servo-Webkomponenten. Bloß dargestellte Komponenten sind kein Beleg für vollständige elektrische Simulation oder jede denkbare Pinoption. Weitere Komponentenattribute müssen in der jeweiligen Primärdokumentation geprüft werden.

Für Informatik-/Technikkurse Serial-I/O, editierbaren Sketch, getrennte Headerdateien, zugeordnete Ein-/Ausgabeelemente und Assembly als passende Ausbaustufen mitdenken. Die Kompilierung nutzt laut README einen externen Builddienst, das Ergebnis läuft in der Simulation; keine uneingeschränkte Offlinefähigkeit behaupten. Das große Projektbeispiel ist ausdrücklich als noch nicht funktionierend markiert und wird nicht als funktionierende Vorlage übernommen. Der README-Kopf nennt Version `0.0.10`, bindet aber das Bundle `0.0.11`; ein gepinnter README-Commit pinnt nicht automatisch alle referenzierten Abhängigkeiten auf denselben Commit.

Belege: LiaTemplates/AVR8js, [README.md, Zeilen 6–38](https://github.com/LiaTemplates/AVR8js/blob/68dd1a3bf5544ff85ddef8c172aa63441ff76e75/README.md#L6-L38) (Version, Argumentplätze), [Zeilen 109–158](https://github.com/LiaTemplates/AVR8js/blob/68dd1a3bf5544ff85ddef8c172aa63441ff76e75/README.md#L109-L158) (Assembly), [Zeilen 198–310](https://github.com/LiaTemplates/AVR8js/blob/68dd1a3bf5544ff85ddef8c172aa63441ff76e75/README.md#L198-L310) (Syntax), [Zeilen 337–710](https://github.com/LiaTemplates/AVR8js/blob/68dd1a3bf5544ff85ddef8c172aa63441ff76e75/README.md#L337-L710) (Komponenten und Einschränkung) und [Zeilen 978–987](https://github.com/LiaTemplates/AVR8js/blob/68dd1a3bf5544ff85ddef8c172aa63441ff76e75/README.md#L978-L987) (Builddienst).
