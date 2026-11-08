# Lokaler Include-Graph, Index und Suche

Diese Referenz beschreibt die technischen Komponenten der optionalen lokalen
Orientierung. Maßgeblich bleibt der
[Orientierungsvertrag](local-orientation-contract.md). Die kanonische
Skill-Laufzeitroute ist konservativ aktiviert und bleibt bei fehlender oder
deaktivierter lokaler Konfiguration dormant. Die öffentliche Suche bleibt
unabhängig nutzbar. Die Implementierungsabnahme verwendet ausschließlich
temporäre synthetische Quellen und belegt keine reale private Nutzung.

## Daten und Autorität

Lokale Daten haben ausschließlich `usage_context=orientation-only`.
LiaScript-Syntax und Template-APIs werden weiterhin aus öffentlichen,
geprüften Originalquellen abgeleitet. Private Quellen sind keine zitierbare
öffentliche Evidenz. Ein technischer Indexbuild ist keine inhaltliche
Freigabe und keine Bestätigung, dass eine neue Aufgabe lokale Orientierung
verwendet hat.

Das [Metadatenschema](local-orientation-metadata.schema.json) erlaubt
konfigurierte Fach-, Jahrgangs-, Lerngruppen- und Dokumentartzuordnungen sowie
Parsermerkmale zu Aufgaben, Operatoren, Lösungen und Struktur. Die
Klassifikationsbasis bleibt `configured`. `archive_policy` ist eine
Quellenrichtlinie; sie beweist keinen dokumentweisen Archivstatus.

Die kontrollierte Facherschließung ergänzt geschlossene IDs für Themen,
Aufgabenfamilien, Lernhandlungen, Antwort- und Lösungsformen, Rechen-,
Begründungs- oder Argumentationsstruktur, abstrakte Zahlen-, Einheiten- und
Kontextprofile, Darstellungsformen, Progression und strukturelle Komplexität.
Jedes Merkmal trägt eine kontrollierte Basis und Vertrauensstufe. Unklare
Erkennung bleibt unbekannt oder mehrdeutig. Die IDs werden niemals aus
Dateinamen geraten und ersetzen keine semantische Suche. Volltexte, Snippets,
konkrete Werte, Formeln, Tokenlisten und Embeddings sind nicht Teil dieses
Index.

Bewusst nicht erkannt werden derzeit semantische Antworttypen jenseits der
rein strukturellen Ein-/Mehrteiligkeit, inhaltliche Lösungsqualität oder
Lösungsstrategien jenseits der Blockzuordnung, Größenprofile jenseits des
groben Merkmals `unit-bearing`, exakte Zahlenwerte und Formeln sowie
Anforderungsbereich und fachliche Schwierigkeit. Freie Themen, seltene
dokumentweise Merkmalskombinationen und private Kontexte werden ebenfalls
nicht erschlossen. Fehlende Klassen bleiben unbekannt oder prüfpflichtig und
werden nicht aus Operatoren ergänzt.

## Include-Graph

`local_orientation_includes.analyze_sources` erhält aktive validierte
Quellen. Der Resolver verwendet die gemeinsame Kommentar-, Makro- und
Verbatim-Analyse des statischen Parsers. Er unterstützt eindeutig statische,
geklammerte `input`-, `include`- und `subfile`-Argumente. Bei fehlender
Dateiendung wird `.tex` ergänzt. Die Auflösung erfolgt relativ zum
verweisenden Dokument und ausschließlich zu bereits unabhängig attestierten
Allowlist-Kandidaten derselben Quelle.

Referenzierung erweitert keine Freigabe. Excludes gelten weiter. Absolute
Pfade, Laufwerke, URIs, ADS-artige Angaben, `..`, dynamische Argumente und
externe Ressourcen werden nicht aufgelöst. Es gibt keine TeX-Suchpfade,
Makroexpansion oder Kompilation. Rohargumente bleiben kurzlebig intern.

`IncludeGraph` enthält dokumentweise Metadaten, attestierte Kandidaten,
interne Kanten und abstrakte Warncodes. Es entsteht kein zusammengefügter
TeX-Text. Lösungszuordnungen bleiben dokumentlokal. Mehrfachverweise erzeugen
keine doppelten Dokumente oder Kanten. Zyklen werden markiert und mit einer
iterativen Graphprüfung behandelt.

Harte Höchstgrenzen: 32 Quellen, 512 Dokumente, 2.048 Referenzvorkommen
einschließlich nicht auflösbarer Ziele, Tiefe 32, 32 MiB Quellbytes und
30 Sekunden. Einzeldateien unterliegen zusätzlich dem Parserlimit von 4 MiB.
Auch die Verzeichnissuche ist durch die Kandidatenauswahl begrenzt. Kleinere
Budgets sind zulässig; größere Parameter heben die Höchstgrenzen nicht auf.
Zeitbudgets werden zwischen begrenzten Arbeitsschritten geprüft; sie sind
keine Betriebssystemgarantie gegen blockierende Dateisystemaufrufe.

## Persistenz und Sicherheitsgrenze

`local_orientation_index.build_local_index` baut ausschließlich bei
ausdrücklichem Aufruf. Der feste Zielort ist
`.schullia-local/state/orientation.sqlite`; ein freier Ausgabeort ist nicht
vorgesehen. Die gesamte lokale Kontrollzone muss ignoriert und unversioniert
bleiben. Quellverzeichnisse werden niemals beschrieben.

Der Build validiert Metadaten gegen das kanonische Schema und zusätzliche
dokumentlokale Beziehungen. SQLite arbeitet im Speicher. Erst die
serialisierten Datenbankbytes werden über geprüfte, exklusiv geöffnete
Dateihandles und eine atomare Ersetzung gespeichert. SQLite erzeugt keine
Dateijournale oder WAL-Nebendateien im Zustandspfad.

Elternverzeichnisse, Index, Buildlock und temporäre Dateien unterliegen
Link-, Reparse-, Hardlink- und Identitätsprüfungen. Ein exklusives `build.lock`
verhindert konkurrierende Builds; ein vorhandener Lock wird nicht automatisch
gelöscht. Ein fehlgeschlagener Build ersetzt keinen bestehenden Index.
Temporäre Artefakte werden nur bei unveränderter eigener Identität entfernt.

Unter Windows bleiben Verzeichnishandles während des gesamten Builds
gehalten. Native relative Dateioperationen mit `RootDirectory` und
`OBJ_DONT_REPARSE` verhindern Umleitungen durch einen zwischenzeitlich
gesetzten Reparse Point. Löschen und Publizieren prüfen die ursprünglich
attestierte Dateiidentität am geöffneten Handle unmittelbar vor der
Änderung. Eine bloße erneute Pfadprüfung genügt dafür nicht.

Produktive lokale Builds sind derzeit auf diese Windows-Implementierung
begrenzt. Auf anderen Plattformen wird vor jedem Zustands-Schreibzugriff
`state_platform_unsupported` gemeldet: Die Python-Standardbibliothek bietet
dort nicht die hier verlangte identitätsgebundene Ersetzung und Löschung.
Der öffentliche Skill bleibt plattformunabhängig. Read-only-Prüfpfade nutzen
auf geeigneten POSIX-Systemen gehaltene `dir_fd`-Handles und `O_NOFOLLOW`;
dies ist keine Freigabe für lokale Builds auf diesen Systemen.

Der Index speichert ausschließlich schema-konforme Metadaten, interne
Graphbeziehungen und technische Gültigkeitsdaten. Relative lokale Provenienz
und Integritätswerte bleiben lokal. Absolute Quellpfade werden nicht
persistiert. Die serialisierte Datenbank ist auf 64 MiB begrenzt.

Die lokale Indexfunktion benötigt SQLite-Serialisierung und
Deserialisierung der Python-Laufzeit. Fehlen diese Fähigkeiten, bricht sie mit
einem abstrakten Fehler ab. Die öffentliche Skillfunktion bleibt verfügbar.

## Transactionale Aktivierung

`local_orientation_activation.py` bindet die erste reale Aktivierung an eine
explizite Bestätigung und eine geschlossene Windows-Transaktion. Es ändert nur
das oberste Konfigurationsfeld `enabled`, bewahrt Konfiguration und einen
gegebenenfalls vorhandenen Index bytegenau als identitätsgebundene Backups und
schreibt nie in Quellverzeichnisse. Aktivierungsmanifest, Stage-Datei und
Backups liegen ausschließlich in der ignorierten lokalen Kontrollzone.

Die verbindliche Reihenfolge lautet:

1. `stage_activation` erzeugt eine aktivierte Staging-Konfiguration, ohne die
   kanonische Konfiguration umzuschalten.
2. Genau ein ausdrücklich angeforderter Build verwendet diese
   Staging-Konfiguration; `attest_index(..., phase="staged")` bindet den
   geprüften Index an die Transaktion.
3. Die reale End-to-End-Autorenabnahme läuft weiterhin gegen die
   Staging-Konfiguration. Die kanonische Konfiguration bleibt währenddessen
   deaktiviert.
4. Jeder fehlende Nachweis führt über `rollback_activation` zur bytegenauen
   Ausgangslage; ein zuvor fehlender Index wird wieder entfernt.
5. Erst nach vollständig bestandener Acceptance darf `commit_activation`
   die kanonische Konfiguration aktivieren.
6. Ein abschließender expliziter Build mit der kanonischen Konfiguration,
   `attest_index(..., phase="final")`, ein Smoke-Test und
   `finalize_activation` schließen die Transaktion.

Aktivierung, Rollback und produktiver Build sind wegen der
Identitätsanforderungen ausschließlich unter Windows freigegeben. Kein
Routing-, Such-, Guidance- oder Acceptance-Aufruf startet diese Schritte
automatisch. Ein vorhandener Buildlock, veränderte Transaktionsdateien oder
abweichende Identitäten sperren den Vorgang fail-closed.

Jede Aktivierungsoperation hält den gemeinsam verwendeten Buildlock als
exklusive, identitätsgebundene Lease. Sie entfernt ausschließlich den selbst
erzeugten Lock; ein fremder oder nach Prozessabbruch verbliebener Lock erfordert
bewusste manuelle Prüfung. Beim Austausch der Konfiguration werden DACL,
Vererbungsschutz, Owner und Group vor und nach der Veröffentlichung
handle-gebunden geprüft. SACL und Mandatory-Integrity-Information werden nicht
angefordert. Ein externer, nicht kooperierender Prozess mit passenden
Schreibrechten bleibt wegen der fehlenden atomaren
Dateiidentitäts-Compare-and-Swap-Operation unter Windows ein theoretisches
TOCTOU-Risiko.

## Gültigkeit und Lesen

Die zentralen Python-Schnittstellen sind:

```python
build_local_index(repo_root, explicit_config=None, environ=None, limits=None)
load_valid_index(repo_root, explicit_config=None, environ=None, limits=None)
search_local_orientation(repo_root, *, explicit_config=None, environ=None,
                         filters=None, limit=8, limits=None)
search_with_local_orientation(repo_root, *, scope='public', corpus=None,
                              public_query='', public_types=None,
                              public_operator=None, local_filters=None,
                              explicit_config=None, environ=None,
                              limit=8, limits=None)
prepare_orientation_guidance(search_result, *,
                             requested_filter_dimensions=())
record_guidance_application(guidance, *, applied_feature_ids,
                            completed_counterchecks,
                            non_leak_confirmed)
search_orientation_guidance(repo_root, *, scope,
                            explicit_config=None, environ=None,
                            local_filters=None, limit=8, limits=None)
decide_orientation_route(*, subject, authoring_action,
                         browser_or_url_only, filesystem_available,
                         python_available, user_scope='auto')
stage_activation(repo_root, *, confirmed=False)
attest_index(repo_root, *, phase, confirmed=False)
commit_activation(repo_root, *, confirmed=False)
rollback_activation(repo_root, *, confirmed=False)
finalize_activation(repo_root, *, confirmed=False)
run_acceptance(repo_root, *, candidate_text=None, candidate_path=None,
               case_id, scope, filters, applied_feature_ids=(),
               public_evidence_status, subject_review_status,
               evaluator_status, sources_unchanged,
               no_private_content_used, no_private_content_output,
               no_private_content_versioned, explicit_config=None,
               environ=None, guidance_limit=8)
```

Der Build liefert `BuildResult.safe_dict()` für sichere Diagnosen. Der Loader
liefert einen ausschließlich lokalen `IndexSnapshot` mit `documents`, `edges`
und `warning_codes`; er ist kein öffentliches Austauschformat. Weitere
öffentliche Suchfilter des Wrappers sind in seiner CLI-Hilfe aufgeführt.
`prepare_orientation_guidance` bildet noch keine Verwendung ab;
`record_guidance_application` verlangt eine bewusste Auswahl aus dem
vorbereiteten Brief sowie alle geschlossenen Gegenprüfungs-IDs.
`search_orientation_guidance` akzeptiert ausschließlich den ausdrücklich
lokalen oder kombinierten Scope. Die reine Routingentscheidung importiert
keine Konfigurations-, Such-, Index- oder Buildkomponente.

Das Near-Copy-Gate wird ausschließlich innerhalb der geschlossenen Acceptance
verwendet. Es lädt nur bereits attestierte Kandidaten über die gehärtete
Parser- und Indexkette, bildet begrenzte Vergleichsprofile flüchtig im Speicher
und verwirft sie beim Schließen der Session. Weder Quelltexte noch
Fingerprints, Tokenprofile oder Ähnlichkeitswerte werden dem SQLite-Index
hinzugefügt.

`load_valid_index` liest begrenzte geprüfte Indexbytes in eine
Speicherdatenbank. Die Datenbank wird als nicht vertrauenswürdige Eingabe
geprüft; Zusatzobjekte, Erweiterungen und unerwartete Schemata sind unzulässig.
Laden und Suche schreiben keine Zustandsdateien.

Gültigkeit hängt von aktiver Konfiguration, Quellenwurzeln, Freigaberegeln,
Risikopolitik, Parser-, Schema-, Feature-, Taxonomie- und Indexversion sowie
Dateiidentitäten und Integritätswerten ab. Die Feature-Taxonomie und die
deterministische Erschließungslogik gehören zum Versionsfingerprint. Vor einer
Trefferfreigabe wird der aktuelle begrenzte Quellenstand erneut sicher
analysiert und exakt mit dem gespeicherten Stand verglichen. Auch
schema-konforme Manipulationen dürfen dadurch keine neuen Treffer erzeugen.

Deaktivierung, entzogene Freigaben, geänderte oder entfernte Dokumente sowie
abweichende Versionen verhindern die Verwendung des alten Stands. Ein nach
einem fehlgeschlagenen Build erhaltener Index gilt nicht automatisch weiter
als aktuell. Die Suche baut oder repariert niemals selbstständig.
Nach jeder beabsichtigten Änderung privater Quellen ist deshalb ein
ausdrücklich angeforderter Wartungsbuild mit anschließender Gültigkeitsprüfung
erforderlich.

## Suche, Ausgabe und Föderation

`search_local_orientation.search_local_orientation` liefert interne
`LocalHit`-Objekte in einem `LocalSearchResult`; dessen `as_dict()` enthält
ausschließlich die öffentliche Diagnoseprojektion. Die Ergebnisgrenze ist
standardmäßig acht, maximal sechzehn. Pro Suche gelten höchstens 512
Dokumente, 25.000 geprüfte Aufgaben und 30 Sekunden einschließlich erneuter
Indexprüfung. Die Konsolenausgabe ist auf 12.000 Zeichen begrenzt. Die
öffentliche Teilabfrage des Wrappers hat zusätzlich ein Budget von zehn
Sekunden; ihre Suchzeichenfolge ist auf 512 Zeichen begrenzt. Beide
Teilabfragen laufen nacheinander mit insgesamt bis zu 40 Sekunden Budget
zuzüglich begrenztem Verwaltungsaufwand und gegebenenfalls blockierenden
Dateisystemaufrufen.

Die lokale Suche verwendet nur vorhandene strukturierte Merkmale.
Nicht unterstützte Filter erhalten einen abstrakten Fehlergrund. SQL-Werte
werden parametrisiert; Auswahl und Ranking sind deterministisch. Fachliche
Passung und sichere Lösungszuordnung gehen bloßer Änderungszeit vor. Risiken
und eingeschränkte Eignung bleiben erkennbar. Änderungszeit beweist keine
fachliche Aktualität und Operatoren bestimmen keinen AFB.

Interne Treffer können lokale Metadaten und Provenienz enthalten. Ihre
Repräsentation verbirgt diese Werte. Die konsolenfähige Projektion enthält
nur Zustand, abstrakten Grund und Ausführungs-/Bereitschaftsflags. Sie gibt
keine lokalen IDs, Pfade, Hashes, Lerngruppennamen, Texte oder Trefferzahlen
aus. Insbesondere darf die ältere Parser-`safe_summary()` mit ihren
Strukturzahlen nicht als öffentliche Trefferprojektion verwendet werden.

Der gesonderte föderierte Wrapper verwendet standardmäßig nur den
öffentlichen Suchraum. Erst eine ausdrückliche lokale oder kombinierte
Scope-Auswahl berührt lokale Konfiguration und Index. Öffentliche und lokale
Ergebnisse bleiben getrennt; es gibt keine gemeinsame Autoritätsrangliste.
Der lokale Ausfall darf öffentliche Ergebnisse nicht verhindern. Es gibt
keinen lokalen `show`-Befehl, Rohtextdump oder privaten Export.

Die Bibliotheksfilter heißen `subject`, `grade`, `learner_group`,
`document_type`, `operator`, `solution_presence`, `solution_assignment`,
`response_shape`, `suitability`, `has_warnings`, `min_subtasks`, `min_tasks`,
`max_tasks`, `modified_after_ns`, `topic_id`, `task_family`,
`learning_action`, `response_form`, `solution_form`, `number_profile`,
`context_profile`, `representation` und `complexity_band`. Für
Fachmerkmale sind ausschließlich IDs der öffentlichen kontrollierten
Taxonomie zulässig. Die lokale CLI verwendet entsprechende
Bindestrichoptionen; der Wrapper versieht sie mit `--local-`. Freie lokale
`query`- und `topic`-Werte sowie `archive_status` werden ausdrücklich
zurückgewiesen. Öffentlicher Suchtext gilt ausschließlich für die
öffentliche Ergebnisgruppe.

## Fachmerkmale und Orientierungsbrief

`local_orientation_features.py` arbeitet innerhalb der bestehenden
attestierten und vorverarbeiteten Parserkette. Kommentare, Makrodefinitionen,
Verbatim- und Codebereiche sowie dynamische Konstrukte liefern keine
Merkmalsbelege. Die Erkennung persistiert nur schema-validierte geschlossene
IDs, Basis und Vertrauensstufe.

`local_orientation_guidance.py` ist die einzige für den Autorenprozess
bestimmte Abstraktionsfläche. Es konsumiert interne Treffer, gibt aber weder
Trefferobjekte noch dokumentweise Metadaten aus. Ein Brief verlangt mindestens
drei unabhängige Dokumentfamilien. Bytegleiche Dateien zählen einmal; durch
Include-Kanten verbundene Dokumente bilden gemeinsam eine Familie. Nur von
mehreren Familien gestützte Merkmale werden als flache IDs ausgegeben.
Unterstützungszahlen und Beziehungen zwischen einzelnen Dokumenten und
Merkmalen bleiben intern.

`local_orientation_routing.py` entscheidet vor jedem lokalen Zugriff, ob
Auftragsart, Fach, Umgebung und Nutzerentscheidung die Route erlauben.
Browser-, URL-only-, Opt-out- und fachfremde Anfragen schließen kurz, bevor
eine lokale Konfiguration berührt wird. Die vollständige Autorenregel steht
in der [Routingreferenz](local-orientation-routing.md).

Orientierungsbrief und Witness verwenden eigene strikt begrenzte
Ausgabeobjekte mit konstanter Repräsentation. Sie enthalten nur kontrollierte
Merkmals- und Gegenprüfungs-IDs. Es entstehen keine zusätzlichen
Persistenzartefakte.

Schnittstellenbeispiele mit ausschließlich synthetischen Platzhalterwerten:

```text
python scripts/build_local_orientation.py --repo-root SYNTHETIC_REPO --config SYNTHETIC_CONFIG --json
python scripts/search_local_orientation.py --repo-root SYNTHETIC_REPO --config SYNTHETIC_CONFIG --subject mathematics --grade 7 --operator berechnen --json
python scripts/search_with_local_orientation.py Bruch --repo-root SYNTHETIC_REPO --config SYNTHETIC_CONFIG --scope both --local-subject mathematics --local-grade 7 --json
```

Diese Beispiele aktivieren keine Konfiguration. Die Abnahme führt die
entsprechenden Aufrufe nur mit tatsächlich angelegten temporären
synthetischen Testlayouts aus.

## Zustände und Freigabegrenze

Die vier Verfügbarkeitszustände des Orientierungsvertrags bleiben erhalten.
Indexbereitschaft, tatsächlich ausgeführte Suche, vorbereiteter
Orientierungsbrief und tatsächlich verwendete Orientierung sind eigenständige
Angaben. Ein erfolgreicher Build oder eine Suche setzt
`local_orientation_used` nicht auf wahr. Auch
`orientation_profile_prepared=true` belegt noch keine Verwendung. Eine
erfolgreich ausgeführte Suche ohne Treffer ist von fehlender Konfiguration zu
unterscheiden.

Reale Bestands- und Trefferzahlen bleiben intern und sind durch die
Witness-Regel nicht zur Veröffentlichung freigegeben. Synthetische Testzahlen
sind keine realen Bestandsprofile.

Aktivierung, Near-Copy und Acceptance sind technisch und synthetisch
abgesichert. Daraus folgt noch keine Freigabe einer konkreten Installation.
Diese entsteht nur durch die oben beschriebene reale Transaktion, getrennte
Autoren- und Evaluatorrollen, einen bestandenen geschlossenen Witness und das
abschließende Leak-Gate. Reale Witnesses und Aktivierungsdaten werden nicht im
Repository persistiert.
