# Vertrag für optionale lokale Orientierungsquellen

Dieses Dokument definiert den Vertrag für eine optionale lokale
Orientierungsquelle. Konfigurationsschema, ignorierte lokale Kontrollzone,
Konfigurationsvalidator, read-only Git-Leak-Gate, sichere kandidatenweise
Allowlist-Expansion, begrenzter statischer TeX-Strukturparser und lokales
Metadatenschema, begrenzte Include-Auflösung, getrennter lokaler Index und
explizite lokale beziehungsweise föderierte Suche, kontrollierte
Fachmerkmale, ein diversitätsgeschützter Orientierungsbrief und das
konservative kanonische Laufzeitrouting, transaktionale Aktivierung, das
flüchtige Near-Copy-Gate und die geschlossene Acceptance sind implementiert
und synthetisch prüfbar. Ob eine konkrete lokale Installation aktiviert und
für eine reale Nutzung freigegeben ist, ist Laufzustand und wird nicht aus
diesem Dokument abgeleitet. Eine synthetisch geprüfte Route belegt keine
tatsächliche Verwendung privater Quellen.
Eine gültige Konfiguration bezeugt weder einen gültigen Index noch eine
ausgeführte Analyse, Suche oder verwendete lokale Orientierung.

## 1. Zweck und Nichtziele

Ein optionales lokales Overlay darf die Erstellung und Überarbeitung von
SchulLia-Inhalten durch abstrahierte Merkmale privater Unterrichtsmaterialien
ergänzend unterstützen. Es ist weder Bestandteil des öffentlichen
SchulLia-Korpus noch Ersatz für offizielle Dokumentation, geprüfte
Template-APIs, kanonische SchulLia-Regeln, fachliche Eigenprüfung oder den
Nutzerauftrag.

Der Vertrag erlaubt weder die Veröffentlichung privater Quellen noch die
Rekonstruktion, Konvertierung oder Weitergabe vollständiger privater
Materialien. Er erteilt keine urheberrechtliche oder datenschutzrechtliche
Freigabe.

## 2. Begriffe

- **Öffentlicher Korpus:** Die durch die öffentliche Quellenkonfiguration
  synchronisierten, commit-gepinnten Quellen samt öffentlichem Index und
  Austauschformaten.
- **Optionales lokales Overlay:** Eine nicht veröffentlichbare,
  rechnergebundene Orientierungsquelle außerhalb des Repositorys mit eigener
  lokaler Konfiguration und eigenen Artefakten.
- **Orientierungstreffer:** Ein begrenzter lokaler Treffer, aus dem nur
  abstrahierbare Gestaltungs- oder Qualitätsmerkmale abgeleitet werden dürfen.
- **Öffentliche Provenienz:** Nachvollziehbare öffentliche Quelle mit Revision,
  Pfad und gegebenenfalls gepinntem Link.
- **Lokale Provenienz:** Ausschließlich lokal gespeicherte technische
  Zuordnung, die nicht in öffentliche Antworten oder Repositoryartefakte
  gelangt.
- **`orientation-only`:** Nutzungskontext für lokale Treffer. Er
  unterscheidet sich von `task-content` für öffentliche reale
  SchulLia-Aufgaben und `documentation` für technische Dokumentation.

Die öffentliche Konfigurationsstruktur ist im
[maschinenlesbaren Konfigurationsschema](local-orientation-config.schema.json)
festgelegt. Reale Werte gehören ausschließlich in eine ignorierte lokale
Konfiguration.

Die ausschließlich lokal zulässige Struktur abstrahierter Parsergebnisse ist
im [lokalen Metadatenschema](local-orientation-metadata.schema.json)
festgelegt. Reale Instanzen dieses Schemas sind keine öffentlichen
Repositoryartefakte.

Technische Provenienz belegt Herkunft und Integrität. Sie begründet keine
inhaltliche Autorität, Fachrichtigkeit oder Wiederverwendungserlaubnis.

## 3. Autoritäts- und Quellenhierarchie

Für LiaScript-Grundsyntax ist die offizielle LiaScript-Dokumentation
maßgeblich. Für eine Template-API gilt die vollständig geprüfte
Original-README der verwendeten Revision. Die kanonischen SchulLia-Verträge
bestimmen Ausgabeprofile, Fachsprache, Operatoren, Lösungen, Gestaltung und
Qualitätsgates.

Der öffentliche SchulLia-Korpus belegt nachvollziehbare Projektkonventionen
und öffentliche Aufgabenmuster. Das lokale Overlay darf erst danach
ergänzende Orientierung liefern. Eine lokale Datei ist niemals alleinige
Autorität für LiaScript-Syntax, Template-APIs, aktuelle Fachrichtigkeit oder
verbindliche SchulLia-Konventionen.

Nutzerauftrag und vorhandener Zielkurs bestimmen Ziel und zulässigen
Änderungsumfang. Sie setzen technische Syntax, Fachrichtigkeit,
Sicherheitsgrenzen und kanonische Fachsprachregeln nicht außer Kraft.
Abweichende oder historische Formulierungen aus einem lokalen Treffer werden
nicht übernommen.

## 4. Zulässige Orientierungsmerkmale

Aus lokalen Treffern dürfen ausschließlich abstrahierbare Merkmale gewonnen
werden:

- Fach, Jahrgang beziehungsweise Lerngruppe, Thema und Dokumentart,
- Aufgabenfamilie, Lernhandlung und erwartete Antwortform,
- sichtbarer Operator und geforderte Bearbeitungstiefe,
- grobe Progression und ausschließlich strukturell begründete Komplexität,
- Art der Zahlen-, Kontext- und Darstellungswahl,
- Umfang, Aufgabendichte und Gliederungsprinzip,
- Rechen-, Begründungs- oder Argumentationsstruktur,
- Lösungsform, jedoch nicht der konkrete private Lösungstext,
- Aktualitäts-, Archiv- und Vertrauensstatus.

Jedes Merkmal bleibt eine Orientierungshypothese und muss gegen Nutzerauftrag,
Fachregeln, öffentliche Belege und die technisch zulässige LiaScript-
Umsetzung geprüft werden.

Fachmerkmale werden ausschließlich als geschlossene öffentliche IDs mit
Erkennungsbasis und begrenzter Vertrauensstufe gespeichert. Freitext,
Fundstellen, konkrete Werte, Formeln, Tokenlisten, n-Gramme und Embeddings
sind unzulässig. Unsichere Erkennung bleibt `unknown`, `ambiguous` oder
`review_required`. Operatoren und Strukturmerkmale bestimmen keinen
Anforderungsbereich und belegen keine fachliche Schwierigkeit.

Ein verwendbarer Orientierungsbrief setzt mehrere unabhängige
Dokumentfamilien voraus. Bytegleiche Dateien zählen einmal; über den
Include-Graphen verbundene Dateien bilden gemeinsam eine Familie. Einzelne
Dokumente und seltene dokumentbezogene Merkmalskombinationen werden nicht
ausgegeben.

## 5. Verbotene Übernahmen und Anti-Kopier-Regel

Private Aufgaben, Lösungen, Materialien und vollständige Abläufe dürfen weder
wörtlich noch in nur kosmetisch veränderter Form ausgegeben werden. Ebenfalls
unzulässig sind die Rekonstruktion eines vollständigen privaten Dokuments,
das Beibehalten einer charakteristischen Kombination aus Kontext, Werten,
Teilfragen und Lösung sowie die Ausgabe privater Pfade oder Dateinamen.

Neue Inhalte werden aus Lernziel, Nutzerauftrag, kanonischen Regeln,
öffentlichen Belegen und mehreren abstrahierten Merkmalen neu entwickelt. Ein
einzelner Orientierungstreffer darf weder Textvorlage noch fachlicher
Nachweis sein. Jede erzeugte Aufgabe und Musterlösung wird unabhängig
fachlich geprüft.

## 6. Datenschutz und Nichtweitergabe

In versionierten Dateien, öffentlichen Testdaten, Ausgaben, Prüf-Witnesses und
dauerhaften Logs sind insbesondere unzulässig:

- absolute, nutzerspezifische oder anderweitig rückführbare lokale Pfade,
- private Datei- und Verzeichnisnamen,
- TeX-Ausschnitte, Aufgaben, Lösungen, Snippets oder Volltexte,
- lokale technische Hashes und reale lokale Bestandsprofile,
- personenbezogene Daten und daraus ableitbare Zuordnungen,
- lokale Konfigurations-, Cache-, Index- oder Snapshotartefakte.

Öffentliche Dokumentation verwendet nur anbieterneutrale Begriffe und
synthetische Beispiele. Die repositoryverankerte Ignore-Regel ist lediglich
eine Schutzschicht und kein Freigabenachweis. Das read-only Git-Leak-Gate
prüft zusätzlich Git-Index, getrackte Arbeitsbaumdateien und nicht ignorierte
Commit-Kandidaten. Es erkennt auch erzwungen hinzugefügte lokale Artefakte;
seine erfolgreiche Ausführung ersetzt keine inhaltliche Datenschutzprüfung.

Der Konfigurationsvalidator darf ausschließlich den sanitisierten Zustand,
einen abstrakten Fehlercode, die Anzahl konfigurierter Quellen- und
Allowlist-Einträge, die geschlossenen Capability-Status sowie die drei
Statusflags `local_search_performed`, `orientation_profile_prepared` und
`local_orientation_used` ausgeben. Eine reine Konfigurationsprüfung lässt alle
drei Flags auf `false`. Die Strukturzahlen sind kein Bestandsprofil;
Dateizahlen, Trefferzahlen und Verteilungen des privaten Materials bleiben
unzulässig.

## 7. Statisches Lesen von TeX und Verbot der Ausführung

Lokales TeX ist nicht vertrauenswürdiger Text. Es darf für die Orientierung
nur statisch gelesen werden. Kompilierung, `shell-escape` und die Ausführung
eingebetteter Shell-, Python-, Lua-, JavaScript- oder Modellanweisungen sind
unzulässig.

Der implementierte Parser ist ein begrenzter Strukturleser und keine
TeX-Engine. Er speichert keine Aufgaben-, Lösungs- oder Überschriftentexte,
expandiert keine Makros und weist unbekannten Konstrukten keine erfundene
Semantik zu. Erkannte `input`-, `include`- und `subfile`-Verweise werden im Parser nur
abstrakt klassifiziert. Ein gesonderter begrenzter Resolver darf ausschließlich
bereits unabhängig attestierte Allowlist-Kandidaten derselben Quelle
verbinden. Dokumente bleiben getrennt; eine TeX-Gesamtausführung oder
dateiübergreifend erfundene Lösungszuordnung entsteht nicht.

Die Kandidatenauswahl prüft Links, kanonische Grenzen und Dateiidentität bei
der Auswahl sowie unmittelbar vor, während und nach dem Lesen erneut. Wo die
Plattform es unterstützt, wird zusätzlich ohne Linkverfolgung geöffnet. Diese
Auswahl bindet außerdem einen nur im laufenden Prozess vorhandenen,
geschlüsselten Inhaltsauthentikator an den Kandidaten. Er wird weder
persistiert noch ausgegeben und ist kein wiederverwendbarer Inhaltsfingerabdruck.
Die spätere Leseoperation muss denselben Authentikator am no-follow geöffneten
Handle bestätigen; auch eine gleich lange Änderung mit restaurierten
Zeitstempeln wird andernfalls verworfen. Diese
Prüfungen behandeln erkennbare Änderungen fail-closed, ersetzen aber keine
vollständige Betriebssystem-Sandbox: Auf Plattformen ohne atomare
No-follow-Schnittstelle bleibt zwischen einzelnen Metadatenaufrufen ein
kleines TOCTOU-Zeitfenster. Ein in diesem Fenster veränderter Kandidat darf
niemals als erfolgreich gelesenes Dokument zurückgegeben werden.

Die statische Auflösung von `input`- oder `include`-Verweisen darf
nur innerhalb ausdrücklich erlaubter Wurzeln erfolgen. Pfadtraversalen,
Symlinks, Junctions und andere Umleitungen dürfen eine Allowlist-Grenze nicht
überschreiten. Externe Ressourcen werden nicht beiläufig nachgeladen oder
ausgeführt.

## 8. Allowlist-, Ausschluss- und Archivpolitik

Lokale Quellen werden nur durch eine ausdrückliche lokale Allowlist
zugelassen. Erreichbarkeit oder Auffindbarkeit allein gilt nicht als
Freigabe. Nicht klassifizierte Bereiche bleiben standardmäßig ausgeschlossen.

Archivmaterial bleibt als solches erkennbar und wird gegenüber aktuellen
geeigneten Quellen geringer gewichtet. Aktualität erhöht nur das
Auswahlgewicht und beweist weder Fachrichtigkeit noch didaktische Eignung.
Kodierungsfehler, veraltete Fachsprache, technische Altlasten und fachliche
Fehler werden nicht als Stilmerkmale übernommen.

Allowlist, Ausschlüsse und private Bereichsbezeichnungen bleiben lokal. Der
öffentliche Vertrag enthält keine reale Verzeichnisstruktur.

## 9. Prüfungen, Drittmaterial und personenbezogene Daten

Standardmäßig ausgeschlossen sind:

- fremde oder urheberrechtlich unklare Materialien,
- nicht ausdrücklich freigegebene Prüfungen und Erwartungshorizonte,
- Dateien mit möglichen Namen oder anderen personenbezogenen Angaben,
- administrative Unterlagen und Bewertungslisten,
- Materialien mit unklarer Herkunft oder Weitergabeberechtigung.

Eine spätere Aufnahme erfordert eine bewusste lokale Freigabe und eine
inhaltsspezifische Risikoprüfung. Dateiname, Speicherort oder früherer eigener
Gebrauch genügen nicht. Eine automatische Prüfung kann das Fehlen
personenbezogener oder fremder Inhalte nicht garantieren.

## 10. Lokale Provenienz ohne öffentliche Pfadweitergabe

Öffentliche Provenienz bleibt unverändert commit-gepinnt. Lokale Provenienz
darf nur in vollständig ignorierten lokalen Artefakten existieren. Sie darf
dort höchstens eine opake Quellen-ID, einen innerhalb der freigegebenen Wurzel
zulässigen relativen Pfad, eine lokale Änderungszeit und einen technischen
Integritätswert enthalten.

Öffentliche Antworten nennen keine konkrete lokale Quelle. Ein späterer
Witness darf nur abstrakt ausweisen, dass lokale Orientierung verwendet wurde,
welche Auswahlmerkmale galten und welche Gegenprüfungen stattfanden.

## 11. Verfügbarkeitszustände

Ein späteres Overlay verwendet genau einen der folgenden Zustände:

- **lokal verfügbar:** Konfiguration, Quelle und Sicherheitsprüfung sind
  vorhanden; eine tatsächlich ausgeführte lokale Suche darf bezeugt werden.
- **lokal nicht konfiguriert:** Es existiert keine aktive lokale
  Overlaykonfiguration.
- **lokal nicht erreichbar:** Eine konfigurierte Quelle ist in der aktuellen
  Umgebung nicht lesbar.
- **lokal wegen Sicherheitsprüfung ausgeschlossen:** Quelle oder Treffer
  verletzt eine Allowlist-, Pfad-, Herkunfts- oder Datenschutzregel.

Nur `lokal verfügbar` erlaubt die Behauptung, eine lokale Suche ausgeführt
oder lokale Orientierung verwendet zu haben.

## 12. Fail-soft-Verhalten und Browsergrenze

Der öffentliche Skill muss ohne lokales Overlay vollständig funktionieren.
Ein fehlendes, unerreichbares oder ausgeschlossenes Overlay ist kein Fehler
des öffentlichen Skills und darf öffentliche Synchronisierung, Suche oder
Validierung nicht beeinträchtigen.

Browser- und URL-only-Umgebungen verwenden ohne lokale Konfiguration den
Zustand `lokal nicht konfiguriert` und bei einer konfigurierten, aber dort
nicht lesbaren Quelle den Zustand `lokal nicht erreichbar`. Sie dürfen
niemals `lokal verfügbar` behaupten, private Pfade erraten oder lokale
Dateien über öffentliche URLs anfordern. Öffentliche Antworten dürfen nicht
den Eindruck erwecken, dass ein Repository-Link Zugriff auf private lokale
Quellen vermittelt.

## 13. Trennung von öffentlichem und lokalem Index

`references/sources.json` bleibt ausschließlich die Konfiguration
öffentlicher fester Quellen. Private Quellen gelangen weder in öffentliche
Snapshots und Manifeste noch in den öffentlichen SQLite-Index oder dessen
JSONL-Austauschformate.

Die tatsächliche lokale Konfiguration und Zustands-, Cache- und
Indexartefakte liegen ausschließlich in der vollständig ignorierten lokalen
Kontrollzone oder in einer ausdrücklich übergebenen externen Konfiguration.
Sie bleiben physisch und logisch vom öffentlichen Korpus getrennt. Private
Ursprungsdateien bleiben an ihrem ursprünglichen Ort. Sie werden nicht in das
Repository kopiert und nicht über Symlinks oder Junctions darin eingebunden.

Öffentliche Tests verwenden ausschließlich temporäre synthetische
TeX-Fixtures. Reale private Dateien und daraus erzeugte Snapshots sind als
Testdaten unzulässig.

Auch die öffentliche föderierte Suche behandelt ihren Korpuspfad als
Sicherheitsgrenze. Korpus und Index müssen regulär, unverlinkt und kanonisch
innerhalb des Repository-Stamms liegen; Symlinks, Junctions, Reparse Points,
Hardlinks sowie Windows-Aliase der privaten Kontrollzone werden verworfen.
SQLite wird nur read-only und immutable geöffnet, und die Indexidentität wird
vor und nach der Abfrage geprüft. Das kleine nicht-atomare Austauschfenster
einer pfadbasierten SQLite-Öffnung bleibt als bekannte Restgrenze bestehen.

## 14. Begrenztes Retrieval

Die lokale Suche filtert nach vorhandenen strukturierten Metadaten wie Fach,
Jahrgang oder Lerngruppe, Dokumentart, Operator, Struktur und
Lösungszuordnung. Zusätzlich sind kontrollierte geschlossene Filter für
Thema, Aufgabenfamilie, Lernhandlung, Antwort- und Lösungsform, abstraktes
Zahlen- und Kontextprofil, Darstellungsform und strukturelle Komplexität
zulässig. Eine freie lokale Textabfrage bleibt verboten. Nicht unterstützte
oder unbekannte Filter werden ausdrücklich zurückgewiesen. Änderungszeit ist
nur ein technisches Merkmal; sie beweist keine fachliche Aktualität.
`archive_policy` ist keine erkannte Archiveigenschaft eines Dokuments.

Öffentliche und lokale Treffer bleiben in Suchraum, Ranking, Provenienz und
Ausgabe unterscheidbar. Der öffentliche Suchraum bleibt der Standard. Die
[Index- und Suchreferenz](local-orientation-index.md) dokumentiert Budgets,
Gültigkeitsprüfung und öffentlichen Fallback. Die begrenzte erneute statische
Quellenprüfung läuft innerhalb der Werkzeuge; sie lädt keine Rohtexte in den
Modellkontext. Es gibt keinen lokalen Volltext-, Snippet- oder Exportpfad.
Nur der gesonderte, schema-validierte Orientierungsbrief darf geschlossene,
von mehreren Dokumentfamilien gestützte Merkmals-IDs in den Autorenprozess
geben. Die Einzelheiten stehen in der
[Routingreferenz](local-orientation-routing.md).

## 15. Near-Copy- und Acceptance-Gate

Die öffentliche, fest kalibrierte
[Near-Copy-Policy](local-orientation-near-copy-policy.json) wird ausschließlich
auf einen vollständigen LiaScript-Kandidaten angewandt. Private Vergleichsdaten
bleiben während der begrenzten Prüfung flüchtig im Speicher. Weder Texte,
Fingerprints noch Ähnlichkeitsdaten werden im Index, in Logs, im Repository
oder bei externen Diensten gespeichert; Embeddings und LLM-Vergleiche sind
ausgeschlossen. Eine Session prüft höchstens drei vollständige Kandidaten.

Das Gate gibt nur `anti_copy_pass`, `anti_copy_risk` oder
`anti_copy_inconclusive` samt geschlossenem Grundcode aus. Es liefert keine
Fundstellen, Scores, Quellhinweise oder Reparaturanleitung und ist daher kein
Abfrageorakel. Ausschließlich `anti_copy_pass` kann eine Freigabe ermöglichen.
Das Gate ist eine technische Näherungsprüfung und keine urheberrechtliche
Freigabe.

Kurze Kandidaten ohne ausreichende Vergleichsbasis, dynamische oder unbekannte
Konstrukte und nicht eindeutig attestierbare Vergleichsräume dürfen
`anti_copy_inconclusive` ergeben. Die Erkennung beansprucht weder
semantische Vollständigkeit noch den Nachweis unabhängiger Urheberschaft.

Die [geschlossene Acceptance](local-orientation-acceptance.md) verbindet
öffentliche Evidenz, unabhängige Fach- und Evaluatorprüfung, strikte
LiaScript-Validierung, Quellenunverändertheit, Inhaltsgrenzen, Near-Copy und
Leak-Gate. Erst ihr bestandener Zustandsübergang darf
`local_orientation_used=true` setzen.

## 16. Anforderungen an einen Prüf-Witness

Der schema-validierte, laufbezogene Witness nennt ausschließlich:

- Fall, Scope, Fach und verwendete Filterdimensionen,
- den Verfügbarkeitszustand,
- geschlossene Release- und Grundcodes,
- die getrennten Flags `local_search_performed`,
  `orientation_profile_prepared` und `local_orientation_used`,
- die tatsächlich übernommenen öffentlichen Merkmals-IDs,
- geschlossene IDs der öffentlichen, fachlichen und technischen
  Gegenprüfungen,
- Anti-Copy-, Validator-, Fach- und Evaluatorstatus,
- boolesche Bestätigungen für unveränderte Quellen, ein sauberes Leak-Gate
  sowie die Ausgabe- und Versionierungsgrenze.

Reale Bestands-, Treffer-, Quellen-, Unterstützungs- und Verteilungszahlen
bleiben intern; synthetische Testzahlen sind zulässig. Öffentliche Diagnosen
enthalten nur Zustand, abstrakte Gründe und Ausführungsflags.

Pfade, Dateinamen, Hashes, Snippets, Volltexte und personenbezogene Angaben
sind im Witness unzulässig. Ohne tatsächlich ausgeführte lokale Suche darf
keine lokale Orientierung behauptet werden. Suche oder Profilbildung allein
setzen `local_orientation_used` nicht auf wahr. Die synthetische
Implementierungsabnahme ist kein realer Nutzungs-Witness.

## 17. Implementierungsstand und Freigabegrenze

Implementiert und synthetisch prüfbar sind:

- das anbieterneutrale Konfigurationsschema,
- die lokale Konfigurationsauflösung und die vier Verfügbarkeitszustände,
- die repositoryverankerte Ignore-Grenze,
- der Pfad- und Allowlist-Validator,
- das read-only Git-Leak-Gate einschließlich Index- und Force-Add-Prüfung,
- die sichere kandidatenweise Expansion der Wildcard-Allowlists mit erneuter
  Link-, Identitäts- und Grenzprüfung jedes einzelnen Kandidaten,
- der begrenzte statische TeX-Strukturparser ohne Makroausführung,
- das strikte lokale Metadatenschema ohne Rohtextfelder,
- die begrenzte statische Include-Auflösung zwischen attestierten Kandidaten,
- der getrennte atomar erstellte lokale Metadatenindex samt Gültigkeitsprüfung,
- die begrenzte strukturierte Suche und ein expliziter föderierter Wrapper,
- die kontrollierte Facherschließung mit geschlossenen Mathematik- und
  Physikmerkmalen,
- der diversitätsgeschützte abstrakte Orientierungsbrief,
- testbare Zustandsübergänge zwischen Suche, Profilbildung und Verwendung,
- das konservative kanonische Routing mit Browser- und öffentlichem Fallback,
- die explizit bestätigte transaktionale Windows-Aktivierung mit
  Stage-, Attestierungs-, Commit-, Finalisierungs- und bytegenauem
  Rollbackpfad,
- das flüchtige, geschlossene Near-Copy-Gate mit fester öffentlicher Policy,
- die geschlossene L1-/L3-Acceptance samt strengem Validator, Gegenprüfungen,
  Leak-Gate und schema-validiertem Witness,
- synthetische Persistenz-, Index-, Such- und Fallbackprüfungen,
- synthetische Konfigurations-, Kandidaten-, Parser-, Schema- und
  Sicherheitsregressionen.

Nicht allein durch den Quellcode belegt sind:

- die erfolgreiche Aktivierung auf einem konkreten Rechner,
- eine reale Autoren- und blinde Evaluatorabnahme,
- ein tatsächlich bestandener Anti-Copy-Vergleich und Leak-Gate-Lauf,
- ein geschlossener realer Witness für genau diesen Lauf.

Diese Nachweise werden transaktional und laufbezogen erbracht und nicht im
Repository persistiert. Bei jedem fehlenden Nachweis wird zurückgerollt oder
die lokale Ausgabe gesperrt. Die kanonische Route bleibt bei deaktivierter
oder fehlender lokaler Konfiguration dormant und arbeitet auf fremden Rechnern
und im Browser vollständig öffentlich.
