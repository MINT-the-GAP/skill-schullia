# lia-loot: API, Variation und Lösbarkeit

## Quellenrang und Aktualität

Verwende für öffentliche Makros und Laufzeitverhalten zuerst die vollständig
gespeicherte `README.md` des lokalen, commit-gepinnten
`ghrepo:mint-the-gap/lia-loot`-Snapshots. Suche sie mit:

```text
python scripts/search_knowledge.py search Gamification --type document --source lia-loot --path README.md --limit 2 --json
```

Diese Referenz und [lia-loot-options.json](lia-loot-options.json) wurden gegen
Revision `05d7c365f963623aca56313b2e26a84ca41632a9` und den README-SHA-256
`afdf7b44e46e8950d5d8f9dfa5224e4e3760ea65ea26332c4466f085f4f77a4b`
geprüft. Weicht der aktuelle Snapshot ab, lies README, Quellcode und Tests erneut
und aktualisiere beide Referenzen, bevor du neue Syntax behauptest.

Behandle die vier großen Beispieldateien unterschiedlich:

- `README.md` ist die API- und Verhaltensquelle.
- `TemplateTargets.md` belegt direkte Importe und Zielkompatibilität.
- `EscapeRoom.md` ist ein absichtlich knapper End-to-End-Testfall, kein
  Standardbauplan.
- `StressTest.md` ist eine extreme QA-Fixture. Seine Schloss- und Truhendichte
  ist keine didaktische Empfehlung.

Der geprüfte Snapshot dokumentiert noch keinen Release-Tag und verwendet
`main`. Prüfe dies bei jeder aktuellen Kursgenerierung erneut. Verwende nach
einer Veröffentlichung den von der README empfohlenen Release-Tag und erfinde
keinen Tag.

## Einbindung und tatsächlicher Funktionsumfang

Importiere Loot direkt im LiaScript-Hauptkopf:

```markdown
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-loot/main/README.md
```

Importiere jedes verwendete Fremdtemplate ebenfalls direkt im Hauptkopf des
Kurses. Verlasse dich nicht auf verschachtelte Template-Importe.

Loot besitzt öffentlich:

- Highscore und elf feste Erfolge,
- Gold, Diamanten und optionale Energie,
- Gold-, Diamant- und Energietruhen,
- sechs Schlüsselfarben sowie Lupe, Schaufel und Gießkanne,
- sichtbare oder verborgene Erd- und Pflanzenfreigaben,
- Theme-, Farbmodus- und Annotationsbedingungen für Fundobjekte,
- monotone bedingte Bereiche mit `@lootif(...; spawn)`,
- Verbergung, Portale, Schlösser und Geheimfolien.

Es gibt keine frei definierbare Quest- oder Missions-API, keine frei
definierbaren Itemtypen, Skins, Achievement-Bedingungen, Trigger oder Aktionen.
`@lootif` bietet nur die unten katalogisierten festen Trigger und die Aktion
`spawn`. Insbesondere erzeugt ein korrekt gelöstes Quiz nicht automatisch eine
Truhe. Modelliere eine narrative Quest durch Kursstruktur, Aufgaben,
Folienzugang und explizite Loot-Makros. Verwende nie interne
`@Loot..._`-Makros in einem Kurs.

## Vollständige öffentliche Makrooberfläche

Verwende in generierten Kursen nur die kanonischen Schreibweisen dieser Tabelle.
Der Parser akzeptiert teilweise zusätzliche deutsche und englische Aliasse; sie
sind kein Grund, uneinheitliche Syntax zu erzeugen.

| Makro | Öffentliche Grammatik | Vertrag |
|---|---|---|
| `@Highscore` | `@Highscore(max, fehlversuch, hinweis, freiminuten, proMinute)` | genau fünf Zahlen; `max > 0`, alle Abzüge und Zeiten `>= 0` |
| `@Ressourcen` | `@Ressourcen(gold, diamanten[, energie])` | zwei oder drei nichtnegative Werte; für neue Kurse nur ganze Zahlen verwenden |
| `@achievements` | ohne Argument | aktiviert elf feste Erfolge; Aliasse `@Achievements`, `@Erfolge` |
| `@lootif` … `@Endelootif` | `@lootif(trigger; spawn)` | dauerhafte bedingte Bereichsfreigabe; drei dokumentierte End-Aliasse |
| `@Schatztruhe` | `@Schatztruhe([menge;] [ziele...;] [fundoptionen...])` | Default: inline, ein Gold |
| `@Diamanttruhe` | dieselben Optionen | Default: inline, ein Diamant |
| `@Energiekiste` | dieselben Optionen | Default: inline, eine Energie; benötigt aktivierte Energie |
| `@Schluessel` | `@Schluessel([farbe]; [oberflächenziel]; [fundoptionen...])` | höchstens eine Farbe und ein Oberflächenziel |
| `@Lupe` | `@Lupe([fundoptionen...])` | kursweiter Gesammelt-Zustand |
| `@Schaufel` | `@Schaufel([fundoptionen...])` | einmaliges Aktionswerkzeug für Erde |
| `@Giesskanne` | `@Giesskanne([fundoptionen...])` | einmaliges Aktionswerkzeug für Pflanzen |
| `@Erdhaufen` … `@EndeErdhaufen` | öffnendes Makro optional mit Fundoptionen | blockweiser Inhalt wird durch Schaufeln freigegeben |
| `@Pflanze` … `@EndePflanze` | öffnendes Makro optional mit Fundoptionen | erst gießen, dann Blüte anklicken; Aliasse `@Blume`, `@EndeBlume` |
| `@Unsichtbar` | `@Unsichtbar(einzeiliger Inhalt)` | vollständig verdeckt, nur im Lupenkreis bedienbar |
| `@Zauberstaub` | `@Zauberstaub(einzeiliger Inhalt)` | schwach funkelnd verdeckt |
| `@Portal` | `@Portal(foliennummer[; hinundher|einweg])` | Default: Zweiwegportal |
| `@Einwegportal` | `@Einwegportal(foliennummer)` | Kurzform für Einwegmodus |
| `@Einbahnportal` | `@Einbahnportal(foliennummer)` | Alias von `@Einwegportal` |
| `@Schloss` | `@Schloss(ziel, farbe[; anker])` | genau ein Ziel und eine explizite Farbe |
| `@Geheimfolie` | ohne Argument, allein auf der Folie | verbirgt die Folie vor ToC und normaler Navigation |

Die vollständigen Optionsgruppen, Aliasse und Kombinationsregeln stehen
maschinenlesbar in [lia-loot-options.json](lia-loot-options.json). Erzeuge
kanonische Schreibweisen, auch wenn der Parser aus Kompatibilitätsgründen
weitere deutsche oder englische Aliasse akzeptiert.

### Highscore und Ressourcen

Setze `@Highscore` auf die erste Folie; dort beginnt die Zeitmessung. Der Score
ist:

```text
max(0,
  maxPoints
  - Fehlprüfungen * Fehlprüfungsabzug
  - geöffnete Hinweise * Hinweisabzug
  - volle Sekunden nach der Freigrenze * Minutenabzug / 60)
```

Die Anzeige verwendet höchstens eine Nachkommastelle. Ab 90 Prozent erscheint
Gold, ab 75 Prozent Silber, ab 50 Prozent Kupfer, darunter keine Trophäe.

Verwende genau einen gültigen `@Ressourcen`-Aufruf. Die erste gültige,
alleinstehende Deklaration wird aus dem Kursquelltext vorab erkannt; ein später
gerenderter Aufruf mit anderen Startwerten kann den Zustand zurücksetzen.

| Aktion | Kosten bei aktivierten Ressourcen |
|---|---:|
| nativen Hinweis öffnen | 1 Gold |
| natives Auflösen | 1 Diamant |
| gültig auf Prüfen klicken | 1 Energie |
| manuellen `lia-timer` im Modus `onclick` erfolgreich starten | 1 Energie |

Bei Bestand null wird die Aktion blockiert. Ohne dritten Ressourcenwert sind
Prüfen und Timerstart unbegrenzt und das Energiesymbol fehlt. Ohne
`@Ressourcen` bleiben Quizaktionen kostenlos, aber keine Truhe ist einsammelbar.
Eine Energiekiste ist nur mit dem dritten Ressourcenwert einsammelbar. Die
Runtime akzeptiert nichtnegative Dezimalwerte und rundet sie ab; generiere zur
eindeutigen Bilanz ausschließlich nichtnegative ganze Zahlen.

### Truhen, Schlüssel, Lupe und Verbergung

Bei allen Truhen gilt:

- Die optionale Menge ist eine positive sichere Ganzzahl, steht immer zuerst und
  gilt vollständig für jede erzeugte Zieltruhe.
- Mehrere Ziele erzeugen unabhängige Truhen. `@Schatztruhe(3; toc; menu)`
  bedeutet zwei Truhen mit jeweils drei Goldstücken.
- Ohne Ziel bleibt die Truhe inline. `anker`, Dauer oder Verbergung ändern
  allein die Inline-Platzierung nicht.
- Unbekannte optionsartige Tokens, eine ungültige oder falsch platzierte Menge,
  eine zweite Dauer sowie doppelte oder widersprüchliche Itemverbergungen machen
  den Fund fail-closed. Wiederholte identische Ziele werden dagegen
  dedupliziert, gleiche Umweltwerte bilden weiterhin dieselbe ODER-Alternative
  und wiederholtes `anker` ist parserseitig idempotent. Generiere trotzdem jede
  solche Option nur einmal.

Kanonische Schlüsselfarben sind `rot`, `blau`, `gruen`, `gelb`,
`lila` und `orange`. Ohne Farbe wird sie stabil aus der Fund-ID bestimmt,
nicht bei jedem Lauf neu gewürfelt. Verwende automatisch gefärbte Schlüssel nur
für optionale Überraschungsfunde. Jeder Pflichtschlüssel erhält eine explizite
Farbe. Ein Schloss verbraucht genau einen passenden Schlüssel; gleiche Farben
bleiben einzelne Inventareinheiten.

Schlüssel funktionieren ohne `@Ressourcen`, dürfen aber nur inline oder an
höchstens einem der sechs LiaScript-Oberflächenziele liegen. Fremdtemplate-Ziele
sind für Schlüssel nicht zulässig.

Die Lupe ist ein kursweites Werkzeug mit einem einzigen Gesammelt-Zustand. Plane
gewöhnlich genau einen erreichbaren Lupenfund. `@Unsichtbar` lässt keinen
visuellen Suchhinweis, `@Zauberstaub` ein schwaches Pixelmuster. Beide sind
Spieleffekte, keine Zugriffssicherheit; Inhalt bleibt in Quelle und DOM. Setze
einen Parameter mit Kommas gemäß LiaScript-Makroregeln in Backticks.

### Gemeinsame Fundoptionen

Schlüssel, alle drei Truhen, Lupe, Schaufel, Gießkanne, Erdhaufen und
Pflanze/Blume akzeptieren die gemeinsamen Anker-, Zeit- und
Umweltbedingungen. Portale, Schlösser sowie die Inhaltsmakros
`@Unsichtbar` und `@Zauberstaub` akzeptieren sie nicht.

| Achse | Kanonische Optionen | Semantik |
|---|---|---|
| Folienbindung | `anker` | nur auf der Quellfolie; Countdown beginnt beim ersten Betreten |
| Verzögerung | etwa `12s`, `30 Sekunden`, `2min`, `1.5 Minuten` | höchstens eine nichtnegative Dauer bis 2 147 483 647 ms |
| Theme | `theme=rot`, `theme=gelb`, `theme=tuerkis`, `theme=blau` | `theme=standard` und `theme=türkis` meinen ebenfalls Türkis; dokumentierte Kurzformen `theme-*` |
| Farbmodus | `farbmodus=dunkel`, `farbmodus=hell` | Aliasse `darkmode`, `lightmode` |
| Annotationen | `annotationen=aus` | Alias `ohne-annotation`; ohne Annotationsanzeige erfüllt |
| Itemverbergung | `unsichtbar` oder `zauberstaub` | genau eine; nur unter aktiver Lupe als gefunden gezählt |

Mehrere Werte derselben Umweltachse sind ODER-Alternativen; verschiedene Achsen
werden UND-verknüpft. Anker, Verzögerung, Itemverbergung und direkte Schichten
kommen ebenfalls per UND hinzu. Die Umwelt wird live ausgewertet: Ein noch nicht
gesammelter Fund kann beim Theme-, Modus- oder Annotationswechsel erscheinen
oder wieder verschwinden. Unbekannte oder widersprüchliche optionsartige Tokens
machen das Objekt fail-closed.

Ein Folienwechsel setzt einen begonnenen Countdown nicht zurück. Ein Reload
startet ihn für noch nicht gesammelte Funde neu. Mache deshalb keine lange,
unkommentierte Wartezeit zur einzigen Pflichtbarriere. Liegt ein Pflichtfund
hinter einer Umweltbedingung, enthält der Witness die erreichbare UI-Aktion zum
Herstellen dieses Zustands; ein dafür benötigtes Menü darf nicht selbst
unerreichbar gesperrt sein.

Der Countdown läuft unabhängig davon, ob die Umweltbedingung gerade passt.
Ohne `anker` beginnt er bei vorab erkannten globalen Funden mit der
Quellkatalogisierung, bei lokalen Funden mit dem ersten Rendern; mit `anker`
beim ersten Betreten der Quellfolie. Nach Ablauf bleibt nur noch die jeweilige
Umweltbedingung als Sichtbarkeitsgate.

### Direkte Erd- und Pflanzenschichten

Schlüssel, alle Truhen, Lupe, Schaufel und Gießkanne akzeptieren beliebig
geordnete direkte Schichten:

- `erde`, `pflanze` oder der kanonisch nicht zu erzeugende Alias `blume`,
- je Schicht optional `-unsichtbar` oder `-zauberstaub`,
- gelesen von links nach rechts als außen nach innen; das Item folgt zuletzt.

Eine Itemverbergung ist unabhängig von den Schichten. Bei
`@Schluessel(blau; erde-unsichtbar; pflanze; unsichtbar)` müssen also zuerst
die unsichtbare Erde gefunden und gegraben, dann die Pflanze gegossen und ihre
Blüte geöffnet und zuletzt der unsichtbare Schlüssel mit der Lupe gefunden
werden. Jede Schicht und jede Verbergung ist ein eigenes Katalogobjekt.

Schaufel und Gießkanne bleiben nach dem Fund in der Ressourcenleiste. Höchstens
eines dieser Aktionswerkzeuge ist gleichzeitig aktiv; die Lupe kann parallel
aktiv sein. Der aktive Werkzeugmodus selbst wird beim Reload nicht bewahrt, die
gesammelten Werkzeuge und bearbeiteten Schichten dagegen im aktuellen Tab.
Lupe, Schaufel und Gießkanne sind je Werkzeugart Singleton-Besitzstände:
Das Einsammeln einer Instanz entfernt weitere Fundstellen derselben Art.
Generiere deshalb standardmäßig genau eine erreichbare Instanz je benötigter
Werkzeugart. Mehrere Instanzen sind nur zulässig, wenn der Witness alle
instanzspezifischen Schichten und Verbergungen vor dem ersten Einsammeln
vollständig abschließt; insbesondere ist eine zweite verborgene Lupe kein
Rettungspfad.

### Blockweise Freigabebereiche

`@Erdhaufen`/`@EndeErdhaufen` und
`@Pflanze`/`@EndePflanze` umschließen beliebigen LiaScript-Inhalt. Start
und Ende stehen jeweils allein, auf derselben Folie und derselben Folienebene,
nicht in Listen, Zitaten oder einem gemeinsamen HTML-Container. Bereiche dürfen
verschachtelt werden und schließen strikt in umgekehrter Reihenfolge.
`@Blume` und `@EndeBlume` sind Aliasse der Pflanzenform.

Ein Erdhaufen gibt den Inhalt nach dem Graben frei. Eine Pflanze muss erst
gegossen werden; das genügt für den Blüherfolg. Erst der zusätzliche Klick auf
die Blüte gibt den Inhalt frei. Der Öffner akzeptiert gemeinsame Fundoptionen,
aber keine zusätzliche direkte Erd-/Pflanzenschicht: Der Container beschreibt
bereits genau seine eigene Schicht. Fehlender, falscher oder
folienübergreifender Abschluss bleibt verborgen und ist kein zulässiger
Pflichtpfad.

## Zielkatalog

### LiaScript-Oberflächen und lokale Ziele

Truhen und Schlüssel unterstützen:

| ID | Ziel |
|---|---|
| `toc` | Inhaltsverzeichnis |
| `menu` | Design und Einstellungen |
| `classroom` | Teilen und Classroom |
| `info` | Info-Menü |
| `translator` | Sprache und Übersetzung |
| `mode` | Darstellungsmodus |

Ein Truhenaufruf darf mehrere dieser Ziele kombinieren, ein Schlüssel höchstens
eines. Schlösser unterstützen außerdem:

| Zielklasse | IDs und Bindung |
|---|---|
| global | `toc`, `mode`, `menu`, `translator`, `classroom`, `info`, `seitenwechsel` |
| lokale Quizaktion | `check`, `resolve`, `hint` |
| Gegenstand | `portal` |

Globale Schlösser werden bereits beim Kursstart registriert und wirken ohne
`anker` kursweit. `seitenwechsel` sperrt Vor/Zurück-Buttons, LiaScript-Pfeile,
`Alt+Shift+N/P` sowie Swipe/Drag gemeinsam; direkte ToC-Sprünge und Portale
bleiben eigene Kanten im Graphen. Mit `anker` wirkt ein globales Schloss nur
auf seiner Quellfolie. Ein Quizschloss
steht unmittelbar nach dem zugehörigen Quiz; mehrere Schlösser folgen dort ohne
fremden Inhalt direkt aufeinander. Ein Portalschloss steht unmittelbar nach dem
Portal und bezieht sich auf das letzte davor stehende Portal derselben Folie.

### Direkt importierte Fremdtemplates

Jedes Ziel benötigt den direkten Template-Import, einen echten Laufzeitmarker und
eine tatsächlich sichtbare passende Instanz. Gleichnamiges Autoren-HTML genügt
nicht. Folienlokal wird das erste sichtbare passende Exemplar verwendet.

| Truhen-ID | empfohlene Schloss-ID | Scope | Besonderheit |
|---|---|---|---|
| `dynflex` | `dynflex` | Folie | ganze DynFlex-Fläche |
| `timer` | `timer` | Folie | Schloss nur bei sichtbarem `onclick`-Startbutton |
| `boardmode` | `boardmodefontbutton` | global | Truhe nur im geöffneten Schriftmenü |
| `marker` oder `textmarker` | `textmarkerbutton` | global | Truhe nur im geöffneten Markermenü |
| `markerquiz` | `markerquiz` | Folie | gesamte Markerquiz-Fläche |
| `annotation` | `annotationsbar` | global | Truhe bei ausgeblendeten Annotationen |
| `canvasocr` | `canvasocr` | Folie | Truhe erst in geöffneter Canvas |
| `kachel` | `kachel` | Folie | ganze Kachelaufgabe |
| `llm` | `llm` | Folie | ganzer LLM-Quizbereich |
| `coordinate` | `coordinate` | Folie | registrierter Board-Container |
| `freeze` | `freeze` | Folie | nur eine tatsächlich bedienbare Freeze-Fläche sperren |
| `mathpath` | `mathpath` | Folie | nur sichtbare Explain-Links werden gesperrt |

Bei globalen Template-Zielen macht `anker` Truhe oder Schloss foliengebunden.
Für `timer` sind `immediate` und `oncheck` keine sperrbaren Startziele.
Bei MathPath muss der Explain-Link im geplanten Zustand tatsächlich entstehen.
Eine gültige, aber nicht vorhandene Template-Zieldeklaration kann in den
Achievement-Katalog gelangen, obwohl das Objekt nie erscheint. Prüfe daher Import,
Instanz und Zustand, nicht nur die Schreibweise.

## Portale und Geheimfolien

Portalziele sind 1-basierte positive Ganzzahlen. Das Ziel muss existieren und
eine andere Folie sein; Titel sind keine Portalziele. `@Portal(n)` erzeugt
einen Hin- und Rückweg. Das temporäre Rückportal verschwindet, sobald die
Zielfolie auf anderem Weg verlassen wird. `@Portal(n; einweg)`,
`@Einwegportal(n)` und `@Einbahnportal(n)` erzeugen keinen Rückweg.

Einwegportale ersetzen zwar ihren Browser-History-Schritt, lassen ToC und
LiaScript-Pfeile aber unverändert. Behaupte deshalb keine absolute
Einbahnstraße, solange diese Wege offen sind. Portale verbrauchen selbst keine
Ressourcen oder Schlüssel. Ein `@Schloss(portal, farbe)` ist dagegen ein
normales Schloss und zählt für den Schlosserfolg.

Eine Geheimfolie wird von normaler Navigation übersprungen. Für die
dokumentierte Suchroute muss ihr vollständiger Titel aus erreichbarem Inhalt
ableitbar, normalisiert eindeutig und das ToC zugänglich sein. Ein Portal darf
eine Geheimfolie öffnen, aber validiere für den Erfolg `Geheimnis entdeckt`
konservativ zusätzlich die dokumentierte exakte Suchroute: Der geprüfte
Runtime-Stand schaltet den Erfolg zwar auch beim Portalpermit frei, die README
beschreibt als Bedingung jedoch die Suche. Geheimfolien sind keine
Zugriffssperre und dürfen keine vertraulichen Inhalte oder unerwünschten
Initialisierungsseiteneffekte enthalten.

## Bedingte Bereiche mit `@lootif`

Ein Bereich beginnt mit `@lootif(trigger; spawn)` und endet kanonisch mit
`@Endelootif`. Unterstützte End-Aliasse sind `@EndeLootif`,
`@endlootif` und `@EndLootIf`. Beide Makros stehen allein auf einer Zeile,
auf derselben Folie und derselben Folienebene. Die Bereichsregeln für Listen,
Zitate, HTML und LIFO-Verschachtelung entsprechen den Freigabebereichen.

Nur `spawn` ist eine gültige Aktion. Vor dem ersten erfüllten Trigger ist der
Inhalt verborgen und inert; danach bleibt er monoton sichtbar, auch wenn die
Bedingung später wieder falsch wird. Der Spawn-Zustand ist kurs- und
versionsgebunden im `sessionStorage` des aktuellen Tabs persistent.

| Triggerfamilie | Kanonische Beispiele | Prüfregel |
|---|---|---|
| vorherige Aufgabe | `Vorherige Aufgabe gelöst` | unmittelbar vorhergehendes bewertbares natives Quiz |
| aktuelle Folie | `Alle Aufgaben der aktuellen Folie gelöst` | mindestens ein aktuell erreichbares bewertbares Quiz und alle solchen Quizze gelöst |
| gelöste Aufgaben | `mindestens 3 bewertbare Aufgaben gelöst`, `bewertbare Aufgaben >= 3` | nichtnegative Ganzzahl |
| Ressourcen | `Gold >= 5`, `Diamanten = 2`, `Energie > 0` | nichtnegative Zahl; Ressource muss aktiviert sein |
| geöffnete Truhen | `Schatztruhen >= 2`, `Diamanttruhen = 1`, `Energiekisten < 4` | je Truhentyp getrennte nichtnegative Ganzzahl |
| Schlossziel | `Schloss: translator` | normalisierter Zieltyp; irgendein geöffnetes Schloss dieses Targets genügt, nicht eine bestimmte Instanz |
| Geheimfolie | `Geheime Folie besucht` | mindestens eine Geheimfolie besucht |
| Lupe | `Lupe gefunden` | kursweiter Lupenzustand |
| Markierfarbe | `markiert: gelb` | irgendein Nutzerwort in dieser Farbe |
| Markierwort | `markiert: gelb: Energie` | Farbe und normalisierter Wortlaut |

Zahlenvergleiche unterstützen `>`, `>=`, `=`, `<=` und `<`.
Kanonische Markerfarben sind `gelb`, `grün`, `blau`, `rosa`,
`orange` und `rot`. Markertrigger verlangen einen direkten
lia-marker-Import und eine erreichbare Markieroberfläche. Der
Wortvergleich normalisiert Groß-/Kleinschreibung, Unicode und Leerraum, aber
ein Generator verwendet trotzdem den exakt beabsichtigten sichtbaren Wortlaut.
Der kursweite Zähler gelöster Aufgaben persistiert nur Quizze mit stabiler,
eindeutiger ID; doppelte IDs werden für diesen Trigger fail-closed nicht
gezählt.

Verschachtelte Bereiche können erst außen und dann innen spawnen. Ungültiger
Trigger, andere Aktion, leeres oder zusätzliches Semikolonfeld, fehlendes Ende,
falsche Verschachtelung oder ein Folienwechsel machen den Bereich fail-closed.
Vollständig geschlossene gültige Bereiche gehören schon vor dem Spawn zum
vollständigen Kurs- und Achievement-Katalog; ihre Source-Deklarationen werden
erst nach dem Spawn aktiv.

Behandle daher jeden gültigen Bereich als Gate im Abhängigkeitsgraphen. Sein
einziges Prärequisit darf nie ausschließlich im eigenen Bereich oder in einem
noch geschlossenen inneren Bereich liegen. Das gilt insbesondere für
Ressourcen-/Truhenschwellen, Schlüssel und Schlösser, Lupe, Markierungen und
Quizze. Ein „alle Aufgaben der Folie“-Trigger mit keiner vorher erreichbaren
bewertbaren Aufgabe bleibt falsch und ist kein Bootstrap.

## Automatik, Abschluss und Erfolge

Das letzte bewertbare native LiaScript-Quiz auf der letzten Kursseite ist die
automatische Abschlussaufgabe. Ein korrekt beobachteter Prüfen-Erfolg stoppt die
Zeit und öffnet den Highscore. Bloßes Auflösen löst diesen Finish-Handler nicht
aus. Stelle deshalb sicher:

- Die letzte Kursseite ist erreichbar und nicht als Pflichtabschluss verborgen.
- Dort existiert das beabsichtigte letzte native Quiz.
- Antwort, Energie und gegebenenfalls der Schlüssel für `check` sind vorher
  erreichbar.
- Keine nachfolgende Quizinstanz verschiebt versehentlich den Abschluss.

`@achievements` aktiviert genau elf feste Erfolge:

| ID | Erfolg | Katalogbedingung |
|---|---|---|
| `all-quizzes-solved` | Aufgaben-Meister | Abschluss korrekt geprüft und alle dabei geladenen bewertbaren nativen Quizze gelöst |
| `perfect-highscore` | Perfekter Highscore | Endscore entspricht exakt der Maximalpunktzahl |
| `all-treasure-chests-opened` | Schatzjäger | alle Goldtruheninstanzen geöffnet |
| `all-diamond-chests-opened` | Diamantensammler | alle Diamanttruheninstanzen geöffnet |
| `all-energy-chests-opened` | Energiesammler | alle Energiekisteninstanzen geöffnet |
| `all-invisible-objects-found` | Unsichtbares entdeckt | jede vollständig unsichtbare Instanz tatsächlich unter der aktiven Lupe gefunden |
| `all-magic-dust-objects-found` | Zauberstaubspürnase | jede Zauberstaubinstanz tatsächlich unter der aktiven Lupe gefunden |
| `all-soil-dug` | Ausgrabungsprofi | alle Erdcontainer und direkten Erdschichten gegraben |
| `all-plants-bloomed` | Grüner Daumen | alle Pflanzencontainer und direkten Pflanzenschichten gegossen und zum Blühen gebracht |
| `all-locks-opened` | Schlossknacker | alle gezählten gültigen Schlösser geöffnet |
| `secret-slide-found` | Geheimnis entdeckt | Runtime: Geheimfolie durch exakte Suche oder erlaubten Portalzugang tatsächlich geöffnet; README-Tabelle nennt nur die Suche |

Die drei Truhentypen werden getrennt ausgewertet; jedes tatsächlich erzeugte
Ziel einer Mehrziel-Truhe zählt als eigene Instanz. Für Lupenerfolge zählen
`@Unsichtbar`/`@Zauberstaub`, die Verbergung eines Funditems und jede
verborgene Erd- oder Pflanzenschicht jeweils einzeln. Bloße Existenz oder
Zauberstaubschimmer genügt nicht. Für `all-plants-bloomed` genügt das Gießen;
für einen dahinterliegenden Kursinhalt bleibt der anschließende Blütenklick
Pflicht.

Jede „alle“-Kategorie wird erst nach geladenem Vollkatalog geprüft und nur bei
mindestens einem Objekt dieser Kategorie vergeben. Gültig geschlossene
`@lootif`-Bereiche zählen bereits vor ihrem Spawn; der 100%-Witness muss sie
deshalb spawnen und ihre Objekte abschließen. Ungültige oder unbalancierte
Bereiche zählen nicht. Erfolge vergeben keine Ressourcen oder Items.

Versprich `Perfekter Highscore` nur, wenn ein Pfad ohne Fehlprüfung und bei
positivem Hinweisabzug ohne verpflichtenden nativen Hinweis existiert. Eine
verpflichtende MathPath-Fehlprüfung kann diesem Ziel widersprechen.

Der Hauptzustand bleibt in `sessionStorage` innerhalb desselben Tabs erhalten.
Ein neuer Tab startet separat; `api.reset()` setzt nur den Highscore zurück.
Ändert sich die Struktur von Quizzen, Funden, Schlössern oder Routen, erhöhe die
Kursversion gemäß [liascript-basics.md](liascript-basics.md), damit alter Zustand
keine neue Route scheinbar lösbar macht.

## Variationsvertrag

Die Pixelgrafiken und Achievementtexte sind fest; eine nicht vorhandene
Skin-Option darf nicht erfunden werden. Erzeuge Eigenständigkeit durch
Mechanikmix, Topologie, Platzierung, Ökonomie, Pacing und Narrativ.

Erstelle vor jedem Entwurf intern diesen Fingerabdruck:

```text
Primärmechanik
Pfadtopologie
Narrativ und fachliche Rolle
aktive Featurefamilien
Ressourcenmodell und Belohnungsmix
Fundorte und Verbergung
Werkzeug- und Freigabekette
Tiefe und Reihenfolge direkter Schichten
Bedingte Spawn-Strategie
Theme-/Modus-/Annotationsstrategie
Portalstruktur
Schlossdichte und Verteilung der Zielklassen
Geheimnisstrategie
Highscore-/Achievement-Feedback
Pacing
visuelle Inszenierung und Interaktionsrhythmus
```

Vergleiche damit alle zugänglichen früheren lia-loot-Kurse im Zielprojekt und
frühere Entwürfe des Gesprächs. Ein Fingerabdruck darf nie identisch wiederholt
werden. Gegen den ähnlichsten Vergleich müssen mindestens drei strukturelle
Dimensionen wechseln; mindestens eine davon ist Primärmechanik, Topologie oder
Ressourcenmodell. Gegenüber dem unmittelbar vorherigen Entwurf wechselt
zusätzlich Primärmechanik oder Topologie. Geänderte Farben, Zahlen, Dauern,
Titel, Bilder oder ein bloß umbenanntes Schlossnarrativ zählen allein nicht.

Ohne verfügbare Historie kannst du keine absolute Neuheit garantieren. Wähle
dann bewusst unter mehreren Kandidaten und gib den neuen Fingerabdruck bei der
Übergabe an, damit er künftig vergleichbar bleibt.

Mögliche Primärprofile sind beispielsweise:

- Highscore-Meisterschaft ohne Schlösser,
- Ressourcenexpedition mit sichtbaren Truhen,
- Lupen- und Detektivpfad,
- Hub-and-Spoke mit Zweiwegportalen,
- optionale Geheimfolien-Seitenquest,
- UI-Schatzsuche,
- Achievement-Sammelkurs,
- sparsamer Schlüsselpfad an wenigen Meilensteinen,
- bedingter Meilensteinpfad mit unterschiedlichen `@lootif`-Triggerfamilien,
- Grabungs- oder Gartenkette mit Werkzeug-Bootstrap,
- live umschaltbare Theme-/Modus-/Annotationssuche.

Verwende nicht automatisch alle Features. Schlüssel und Schlösser sind nur eine
Familie und dürfen vollständig fehlen. Wenn sie vorkommen:

- sperre nicht jedes Quiz und nicht wiederholt nur `check`,
- verwende bei mindestens vier Schlössern mindestens zwei der Zielklassen
  Oberfläche, Quizaktion, Portal oder Fremdtemplate,
- lasse kein einzelnes Schlossziel mehr als die Hälfte der Schlösser stellen,
- lasse mindestens die Hälfte der gamifizierten Interaktionen aus
  Nicht-Schloss-Mechaniken bestehen,
- wiederhole auf aufeinanderfolgenden Folien nicht denselben Gate-Typ ohne
  fachlichen Grund,
- plane nach zwei aufeinanderfolgenden Schlosskursen zuerst einen schlossfreien
  Kandidaten.

Rotiere ebenso Werkzeuge, Spawn-Trigger, Fundoberflächen, Schichttiefen und
Umweltachsen. „Alle Features überall“ ist kein eigenes Profil. Der gewählte
Mix muss die fachliche Dramaturgie unterstützen und visuell wie interaktiv
anders gestaffelt sein als der unmittelbar vorherige Kurs.

Das sind Generierungsregeln, keine Behauptungen über technische Grenzen der API.

## Verbindlicher Lösbarkeitsvertrag

Ein Vergleich der Gesamtzahlen von Schlüsseln und Schlössern reicht nicht. Beweise
vor der Ausgabe mindestens einen konkreten, ausführbaren Vollständigkeitspfad.

### Zustandsmodell

Modelliere mindestens:

```text
aktuelle und besuchte Folien
gelöste Quizze
Gold, Diamanten und Energie
Schlüssel-Multiset der sechs Farben
Lupe vorhanden und aktivierbar
Schaufel und Gießkanne vorhanden; aktives Aktionswerkzeug
jede Erdschicht: sichtbar/gefunden/gegraben
jede Pflanzenschicht: sichtbar/gefunden/gegossen/geöffnet
geordnete direkte Schichten und freigegebene Bereichsinhalte
Theme, Farbmodus und Annotationssichtbarkeit
Markierungen nach Farbe und normalisiertem Wort
gelöste-Aufgaben- und geöffnete-Truhen-Zähler je Typ
gültige lootif-Bereiche und monotone Spawn-Zustände
gesammelte Schlüssel und Truhen
geöffnete Schlösser
besuchte Geheimfolien
aktuelle Zweiweg-Rückroute
abgelaufene Pflichtverzögerungen
Vollkatalog und Fortschritt jeder nichtleeren Achievement-Kategorie
```

Zulässige Übergänge sind Fund sammeln, Lupe oder Aktionswerkzeug umschalten,
Theme/Modus/Annotationen ändern, eine Verbergungsinstanz mit der Lupe wirklich
finden, graben, gießen, Blüte öffnen, markieren, bedingten Bereich spawnen,
Schloss öffnen, korrekt prüfen, Hinweis öffnen, auflösen, manuellen Timer
starten, normal navigieren, Oberfläche öffnen, Portal benutzen oder
zurückkehren, Geheimfolie exakt suchen und endlich warten.

Das Zielprädikat umfasst:

- Abschlussquiz korrekt per Prüfen gelöst,
- alle verpflichtenden Lernfolien besucht,
- alle verpflichtenden Quizze gelöst,
- alle gültigen bedingten Bereiche gespawnt,
- alle gültig katalogisierten Truhen erreichbar und gesammelt,
- alle katalogisierten Verbergungsinstanzen gefunden und alle Erd- und
  Pflanzenschichten bis zur nötigen Inhaltsfreigabe bearbeitet,
- alle gültigen Schlösser erreichbar und geöffnet,
- alle vorgesehenen Geheimfolien besucht,
- bei aktivem `@achievements` alle nichtleeren Kategorien abgeschlossen,
  sonst alle ausdrücklich versprochenen Erfolge erreichbar.

### Harte Invarianten

1. **Ein Witness:** Derselbe Aktionspfad erfüllt das gesamte Ziel. Er setzt weder
   Reload, Browser-Zurück, neuen Tab, Quelltexteinsicht noch zufälliges Erraten
   eines unsichtbaren Fundorts voraus.
2. **Schlüsselpräfix:** Vor jedem Schloss steht mindestens ein bereits
   erreichbarer, unverbrauchter Schlüssel derselben Farbe zur Verfügung.
   Gesamtgleichheit der Farb-Multisets genügt nicht.
3. **Ressourcenpräfix:** Vor jeder kostenpflichtigen Aktion ist der Bestand
   mindestens eins; nach jedem Präfix bleibt er nichtnegativ. Belohnungen werden
   erst nach tatsächlicher Sichtbarkeit und Zugänglichkeit gutgeschrieben.
4. **Keine Zyklen:** Kein Gate schließt sein einziges eigenes Prärequisit ein.
   Insbesondere liegen weder ein ToC-Schlüssel im gesperrten ToC noch die Energie
   für eine Prüfung hinter genau dieser Prüfung.
5. **Werkzeug-Bootstrap:** Vor jeder Pflichterde ist mindestens eine Schaufel,
   vor jeder Pflichtpflanze mindestens eine Gießkanne erreichbar. Die einzige
   Schaufel liegt nicht hinter eigener Erde, die einzige Gießkanne nicht hinter
   eigener Pflanze. Mehrere Makroinstanzen sind kein unabhängiger Ersatz, weil
   jedes Werkzeug kursweit nur einmal gesammelt wird.
6. **Lupe zuerst:** Jede verpflichtende Verbergungsinstanz hat eine vorher
   erreichbare Lupe. Das gilt auch für Lupe, Werkzeuge und direkte Schichten,
   wenn sie selbst verborgen sind. Vollständig unsichtbare Pflichtobjekte haben
   zusätzlich einen fairen Hinweis auf ihren Ort und werden im Witness wirklich
   mit der aktiven Lupe gescannt.
7. **Bedingte Trigger:** Jeder gültige `@lootif`-Bereich kann außen nach innen
   spawnen. Sein Trigger ist ohne eigenen Inhalt erreichbar. „Alle Aufgaben der
   Folie“ hat mindestens ein vorher erreichbares Quiz; „vorherige Aufgabe“
   verweist auf ein tatsächlich erreichbares DOM-Vorgängerquiz. Ressourcen-,
   Truhen-, Schloss-, Geheim-, Lupen- und Markertrigger besitzen eine reale
   auslösende Aktion.
8. **Umweltzustand:** Für jedes Pflichtobjekt existiert ein erreichbarer
   passender Theme-/Modus-/Annotationszustand. Die nötige Oberfläche bleibt
   zugänglich; mehrere Zustände können in der Witness-Reihenfolge umgeschaltet
   werden.
9. **Truhenaktivierung:** Jede Pflichttruhe besitzt einen gültigen
   `@Ressourcen`-Aufruf; Energiekisten besitzen zusätzlich den dritten Wert.
   Mehrziel-Truhen werden als einzelne volle Belohnungen samt ihrer Schichten
   und Verbergungen expandiert.
10. **Oberflächenzugang:** Eine Oberfläche ist erreichbar, bevor ihr Fund
    benötigt wird. Kein Schlüssel liegt ausschließlich in der Oberfläche, die
    er selbst entsperrt.
11. **Template-Vertrag:** Direkter Import, echte sichtbare Instanz und
    benötigter UI-Zustand existieren. Ein Timer-Schloss hat einen
    `onclick`-Button.
12. **Portalroute:** Jedes Portalziel ist positiv, vorhanden und verschieden von
    der Quellfolie. Jeder Zweig führt zurück oder verschmilzt mit dem Hauptpfad.
    Vor einem Einwegübergang sind alle nur vorher erreichbaren Pflichtobjekte
    gesammelt.
13. **Globale Sperren:** Kursweite `seitenwechsel`-, ToC- oder Menüschlösser
    blockieren nicht gemeinsam alle Wege zu ihren Schlüsseln, Werkzeugen oder
    Umweltsteuerungen. Sie wirken schon beim Kursstart.
14. **Bereiche und Kataloge:** Alle Bereichsmakros sind auf einer Folie korrekt
    LIFO-geschlossen. `@Highscore`, `@Ressourcen`, `@achievements` und
    kursweit benötigte `@Geheimfolie`-Deklarationen stehen nicht ausschließlich
    in einem noch inaktiven Bereich. Jedes Objekt des Vollkatalogs wird im
    Witness materialisiert und abgeschlossen.
15. **Geheimfolien:** Titel sind normalisiert eindeutig, der vollständige Titel
    ist erreichbar und ToC oder ein valider Portalweg steht zur Verfügung.
16. **Abschluss:** Das letzte bewertbare native Quiz der letzten erreichbaren
    Seite ist korrekt prüfbar; es bleibt mindestens eine Energie übrig, wenn
    Energie aktiviert ist.
17. **Erfolge:** Alle Objekte jeder nichtleeren Kategorie besitzen reale
    Instanzen und sind im selben Witness abschließbar. Pflanzen werden zusätzlich
    geöffnet, wenn Pflichtinhalt hinter ihrer Blüte liegt. Der perfekte
    Highscore hat einen abzugslosen Witness.
18. **Fehlerreserve:** Zusätzlich zum perfekten Witness bleibt standardmäßig
    nach einer einzelnen Fehlprüfung, einem optionalen Hinweis oder einem
    angebotenen Seitenzweig noch ein Abschlussweg. Eine absichtlich exakte
    Nullreserve ist nur auf ausdrücklichen Wunsch zulässig und wird offengelegt.

### Planungsalgorithmus

1. Analysiere Folien, Quizze, Hinweise, Imports, Template-Instanzen,
   Abschlussquiz und fachliche Prärequisiten.
2. Fingerprinte verfügbare Vergleichskurse und bilde mehrere deutlich
   verschiedene Gamification-Kandidaten.
3. Wähle den didaktisch passenden Kandidaten mit großem strukturellem Abstand.
4. Plane zuerst einen öffentlichen Hauptpfad, dann optionale Zweige mit Rückweg
   oder Merge.
5. Plane vom Ziel rückwärts: Schloss zu Schlüssel, Verbergung zu Lupe, Erde zu
   Schaufel, Pflanze zu Gießkanne und Blütenklick, bedingter Bereich zu
   erreichbarem Trigger, Umweltbedingung zur zugänglichen Steuerung,
   Kostenaktion zu vorheriger Ressource und Ziel zu gültigem Zugang.
6. Expandiere Mehrziel-Truhen, jede direkte Schicht und
   Verbergungsinstanz, Blockbereiche, verschachtelte `@lootif`-Gates,
   gestapelte Schlösser, globale Scopes und jede nichtleere
   Achievement-Kategorie in einzelne Zustandsobjekte.
7. Suche vorwärts über die Zustände und simuliere Gates außen nach innen.
   Verwirf Zustände, die am selben Ort bei gleichem Fortschritt weniger
   Ressourcen und Schlüssel besitzen oder einen erforderlichen Werkzeug-,
   Umwelt- oder Spawnzustand nicht mehr herstellen können.
8. Speichere einen Witness mit Schritt, Folie, Aktion, Prärequisit,
   Umwelt-/Werkzeugzustand, Bestand vorher, Effekt und Bestand nachher. Nenne
   Wechsel, Scan, Grabung, Gießen, Blütenöffnung, Markierung und Spawn jeweils
   als eigene Aktion.
9. Prüfe mindestens eine Fehlprüfung, einen optionalen Hinweis, jeden
   angebotenen Zweig und alle verwendeten Umweltzustände als Abweichung.
10. Erzeuge erst jetzt LiaScript und prüfe den geschriebenen Kurs erneut gegen
    denselben Witness.

Verwende für die Übergabe mindestens diese beiden Tabellen:

| Schritt | Folie | Aktion | Voraussetzung | Umwelt/Werkzeug | Bestand vorher | Effekt | Bestand nachher |
|---:|---|---|---|---|---|---|---|

| Objekt | Fund-/Zielort | Prärequisiten | im Witness erreicht | Beleg |
|---|---|---|---|---|

Schlägt die Suche fehl, melde den frühesten unerfüllten Schnitt konkret:
fehlende Schlüsselfarbe oder Ressource, fehlendes Werkzeug, ungesehene
Verbergung, unerfüllbare Umweltbedingung, nicht erreichter Spawn-Trigger,
unerreichbare Oberfläche, verlorener Rückweg, ungültiges Ziel, unvollständiger
Katalog oder Prärequisitenzyklus. Ergänze nicht nur nach Gefühl weitere Truhen.

## Typische Sackgassen

| Antimuster | Warum unlösbar oder unfair |
|---|---|
| `@Schluessel(gruen; toc)` plus `@Schloss(toc, gruen)` | Schlüssel liegt hinter seinem eigenen Schloss |
| Pflichtschlüssel `unsichtbar`, Lupe erst hinter seinem Portal | Lupe kann das Gate nicht mehr vorbereiten |
| einzige `@Schaufel(erde)` oder Schaufel im eigenen Erdhaufen | Werkzeug liegt hinter der Schicht, die es selbst entfernen müsste |
| einzige `@Giesskanne(pflanze)` oder Gießkanne in eigener Pflanze | Werkzeug liegt hinter der Pflanze, die es selbst gießen müsste |
| einzige `@Lupe(unsichtbar)` ohne frühere Lupe | vollständig unsichtbares Suchwerkzeug kann nicht fair gefunden werden |
| `@lootif(Gold >= 5; spawn)` enthält die einzige Belohnung zum Erreichen von fünf Gold | Trigger schließt sein eigenes Prärequisit ein |
| `@lootif(Vorherige Aufgabe gelöst; spawn)` nach einem unerreichbaren Quiz | DOM-Vorgänger kann nie gelöst werden |
| `@lootif(Alle Aufgaben der aktuellen Folie gelöst; spawn)` ohne vorher erreichbares Quiz | die nicht-vakuose Bedingung bleibt falsch |
| Pflichtfund nur bei `theme=rot`, aber Theme-Menü unerreichbar gesperrt | benötigter Umweltzustand kann nicht hergestellt werden |
| unpassend oder folienübergreifend geschlossener Reveal-/lootif-Bereich | Inhalt bleibt fail-closed und Katalog/Witness laufen auseinander |
| `@Ressourcen(0, 0, 0)` und Energiekiste hinter dem ersten Quiz | Belohnung liegt hinter ihrer eigenen Kostenaktion |
| globale Seitenwechsel- und ToC-Schlösser, Schlüssel auf späterer Folie | keine Startkante bleibt offen |
| automatisch gefärbter Schlüssel für ein Pflichtschloss | geforderte Farbe ist nicht planbar |
| `@Energiekiste` bei `@Ressourcen(gold, diamanten)` | sichtbar, aber nicht einsammelbar |
| `@Energiekiste(menu; 3)` | Menge steht nicht zuerst; Fund ist fail-closed |
| `@Schloss(timer, rot)` bei `immediate` | kein sperrbarer manueller Startbutton |
| Zweiwegziel anderweitig verlassen und später Rückportal erwarten | Rückportal wurde entfernt |
| Einwegportal in gesperrten Bereich ohne weiteren Ausgang | Abschluss bleibt unerreichbar |
| perfekter Highscore verlangt einen kostenpflichtigen Pflichthinweis | Maximalpunktzahl ist im selben Lauf unmöglich |
| Mehrziel-Truhe nur an einem Ziel geöffnet | Schatzjäger und vollständige Bilanz bleiben unvollständig |
| Pflanze nur gegossen, Pflichtinhalt aber nicht über die Blüte geöffnet | Blüherfolg kann erreicht sein, der Kurs bleibt trotzdem unvollständig |
| gültige katalogisierte Truhe in nie gespawntem `@lootif` | Achievement-Kategorie und 100%-Pfad bleiben unvollständig |

## Grenzen statischer Prüfung

Führe eingebettete Laufzeitskripte nicht aus. Bei dynamischen Quizlösungen,
zufällig erzeugten Aufgaben oder erst zur Laufzeit erscheinenden
Fremdtemplate-Flächen kann eine statische Prüfung nur Voraussetzungen und
Struktur belegen. Erfinde keine konkrete Laufzeitlösung. Kennzeichne verbleibende
Annahmen und verlange bei komplexen UI-Zielen einen manuellen Browser-Smoke-Test,
ohne ihn als Ersatz für den statischen Witness zu verwenden.
