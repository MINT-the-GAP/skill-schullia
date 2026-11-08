# Kontrolliertes Routing lokaler Orientierung

Diese Referenz beschreibt die optionale Autorenroute zwischen der öffentlichen
SchulLia-Evidenz und einer ausschließlich lokal verfügbaren,
datensparsamen Orientierung. Maßgeblich bleiben der
[Orientierungsvertrag](local-orientation-contract.md), die
[Index- und Suchreferenz](local-orientation-index.md) und die kanonische
`SKILL.md`.

Die Route ist anbieterneutral. Die öffentliche Gesamtroute ist fail-soft; der
lokale Freigabezweig ist fail-closed. Aktivierung, Near-Copy und Acceptance
sind implementiert und synthetisch prüfbar. Synthetische Tests aktivieren
keine reale Konfiguration und belegen keine tatsächliche Verwendung privater
Quellen. Eine konkrete Installation benötigt weiterhin ihre eigene
transaktionale End-to-End-, Autoren-, Evaluator- und Leak-Abnahme.

## Autorität und Reihenfolge

Nutzerauftrag und vorhandener Zielkurs bestimmen Lernziel und zulässigen
Änderungsumfang. Kanonische SchulLia-Verträge bestimmen Ausgabeprofil,
Operatoren, Lösungen, Fachsprache und Qualitätssicherung. Offizielle
LiaScript-Dokumentation und geprüfte Template-READMEs bleiben für Syntax und
APIs maßgeblich.

Die öffentliche SchulLia-Suche wird zuerst ausgeführt. Die in der
`SKILL.md` verlangten öffentlichen Aufgaben- und Kursbeispiele bleiben
zwingend und werden durch lokale Orientierung weder ersetzt noch als lokale
Treffer ausgegeben. Erst nach ihrer Prüfung darf ein abstrakter lokaler
Orientierungsbrief den Autorenplan ergänzen.

Lokale Quellen sind keine zitierbare Evidenz. Sie dürfen keine LiaScript-
Syntax, Template-API, fachliche Aussage oder Bewertung allein begründen.

## Entscheidung vor jedem lokalen Zugriff

Die testbare Routingentscheidung wird getroffen, bevor lokale Konfiguration,
Index, Quelle, Near-Copy oder Acceptance berührt werden.

Die lokale Route ist nur zulässig, wenn alle folgenden Bedingungen erfüllt
sind:

- Es handelt sich um die Neuerstellung oder wesentliche fachliche
  Überarbeitung einer Mathematik- oder Physikaufgabe beziehungsweise eines
  entsprechenden vollständigen Kurses.
- Datei- und Pythonzugriff sind lokal verfügbar.
- Die Umgebung ist weder Browser- noch URL-only.
- Der Nutzer hat lokale Orientierung nicht ausgeschlossen.
- Eine aktive, validierte lokale Konfiguration und ein gültiger vorhandener
  Index sind verfügbar.

Eine aktive Konfiguration ist ein dauerhaftes lokales Opt-in. Trotzdem muss
die konkrete Suche den Scope `local` oder `both` ausdrücklich wählen; der
öffentliche Standard wird niemals stillschweigend umgedeutet.

Die lokale Route wird nicht verwendet bei:

- Browser- und URL-only-Ausführung,
- fehlendem lokalen Datei- oder Pythonzugriff,
- einem ausdrücklichen Wunsch nach ausschließlich öffentlichen Quellen,
- reiner LiaScript-, Quiz-, Template-, Makro- oder Operatorerklärung,
- reiner Klassifikation ohne fachliche Aufgabenerstellung,
- reiner Gamification eines eingefrorenen Fachtextes,
- anderen Fächern als Mathematik und Physik,
- fehlender, deaktivierter, unerreichbarer oder sicherheitsbedingt
  ausgeschlossener Konfiguration,
- fehlendem, veraltetem oder ungültigem lokalem Index.

Diese Ausschlüsse müssen vor jedem Konfigurationszugriff kurzschließen.
Insbesondere versucht eine Browserroute nicht, eine lokale Konfiguration zu
finden, und fordert keine privaten Dateien über öffentliche URLs an.

## Ausführung

Eine zulässige Route verwendet ausschließlich die gehärteten Komponenten:

- `search_with_local_orientation.py` für die ausdrücklich getrennte
  öffentliche und lokale Suche,
- `local_orientation_features.py` für kontrollierte, geschlossene
  Merkmals-IDs,
- `local_orientation_guidance.py` für den abstrahierten Orientierungsbrief,
- `local_orientation_routing.py` für die testbare Routingentscheidung,
- `local_orientation_activation.py` für explizite transaktionale
  Aktivierung und Rollback,
- `local_orientation_near_copy.py` als flüchtiges internes Nähe-Gate,
- `local_orientation_acceptance.py` als einzige Freigabefläche für einen
  vollständigen Kandidaten und den geschlossenen Witness.

Private Quellen werden nicht mit allgemeinen Dateiwerkzeugen, einem
`show`-Befehl oder internen Trefferobjekten in den Modellkontext geladen.
Es gibt keinen Rohtext-, Snippet-, Volltext-, Token-, Embedding- oder
Exportpfad.

Suche und Routing bauen, aktualisieren oder reparieren keinen Index. Ist kein
gültiger Index vorhanden, wird ohne Qualitätsabstrich mit der vollständigen
öffentlichen Autorenroute fortgefahren. Ein lokaler Fehler verhindert weder
öffentliche Suche noch LiaScript-Validierung.

Ein lokaler Ausfall, `anti_copy_risk` oder `anti_copy_inconclusive` sperrt
jedoch den lokal orientierten Kandidaten vollständig. Er darf nicht als
öffentliche Fallbackausgabe umetikettiert werden. Zulässig ist nur ein
unabhängig und ausschließlich aus öffentlicher Evidenz neu entwickelter
Kandidat.

## Orientierungsbrief

Der Orientierungsbrief wird ausschließlich aus schema-validierten internen
Metadaten gebildet. Er verlangt mindestens drei unabhängige
Dokumentfamilien. Bytegleiche Dateien zählen einmal; über den Include-Graphen
verbundene Dateien bilden gemeinsam eine Dokumentfamilie. Ein einzelnes
Dokument oder eine vervielfältigte Quelle kann das Diversitätsgate daher
nicht erfüllen.

Ausgegeben werden nur von mehreren unabhängigen Familien gestützte,
geschlossene Merkmals-IDs und grobe Klassen. Dokumentweise Beziehungen,
Unterstützungszahlen und seltene rekonstruierbare Kombinationen bleiben
unterdrückt.

Zulässige Merkmalsgruppen sind:

- Thema,
- Aufgabenfamilie und Lernhandlung,
- Antwort- und Lösungsform,
- Rechen-, Begründungs- oder Argumentationsstruktur,
- abstraktes Zahlen-, Größen-, Einheiten- und Kontextprofil,
- Darstellungsform,
- grobe Dokumentprogression,
- rein strukturell begründete Komplexität.

Alle Merkmale sind Orientierungshypothesen. Sie bestimmen keinen
Anforderungsbereich und belegen keine fachliche Schwierigkeit. Unklare oder
widersprüchliche Erkennung bleibt `unknown`, `ambiguous` oder
`review_required`.

Der Brief enthält weder freie Texte noch lokale IDs, Pfade, Dateinamen,
Hashes, Lerngruppennamen, konkrete Werte, Formeln, Lösungsschritte,
Trefferzahlen oder technische Provenienz. Er wird nicht als zusätzliche
Datei, Log oder Austauschformat persistiert.

## Statusübergänge

Verfügbarkeit, Indexbereitschaft, Suche, Profilbildung und tatsächliche
Verwendung sind getrennte Aussagen:

- `local_search_performed=true` setzt eine tatsächlich abgeschlossene lokale
  Suche voraus.
- `orientation_profile_prepared=true` setzt zusätzlich ein bestandenes
  Schema-, Sicherheits- und Diversitätsgate voraus.
- `local_orientation_used=true` setzt zusätzlich voraus, dass mindestens
  eine im Brief enthaltene Merkmals-ID bewusst in den Autorenplan übernommen,
  am vollständigen Kandidaten öffentlich, fachlich und technisch
  gegengeprüft, durch das Leak-Gate bestätigt und mit
  `anti_copy_pass` freigegeben wurde.

Konfiguration, Index, Suche oder Profilbildung allein setzen
`local_orientation_used` niemals auf wahr. Eine leere Suche, ein
verworfener Einzelhit oder ein nicht verwendeter Brief behält den Wert
`false`.

Ein `task`-Fragment kann das Gate nur innerhalb seines vollständigen
Zielkurses oder eines vollständigen Testumschlags durchlaufen. Pro
Acceptance-Session werden höchstens drei vollständige Kandidaten geprüft.
Risk- und Inconclusive-Resultate enthalten keine reparaturgebenden
Vergleichsdetails.

## Zulässiger Einfluss

Ein verwendeter Orientierungsbrief darf Aufgabenmix, Gliederungsprinzip,
grobe Aufgabendichte, Progressionsform, Antwort- und Lösungsformen sowie
abstrakte Zahlen-, Kontext- und Darstellungsprofile beeinflussen.

Er liefert niemals konkrete Aufgabenformulierungen, Werte, Gleichungen,
private Kontexte, charakteristische Kombinationen, private Lösungswege oder
eine vollständige Aufgabenfolge. Neue Aufgaben und Musterlösungen werden aus
Lernziel, Nutzerauftrag, kanonischen Regeln und öffentlichen Belegen neu
entwickelt und unabhängig fachlich geprüft.

## Sicherer Witness

Der Witness folgt dem geschlossenen
[Acceptance-Schema](local-orientation-acceptance.schema.json) und darf nur
enthalten:

- den Verfügbarkeitszustand und einen abstrakten Grundcode,
- öffentliche beziehungsweise auftragsbezogene Filterdimensionen,
- `local_search_performed`,
- `orientation_profile_prepared`,
- `local_orientation_used`,
- tatsächlich verwendete öffentliche Merkmals-IDs,
- geschlossene IDs der fachlichen, öffentlichen und technischen
  Gegenprüfungen,
- geschlossene Release-, Anti-Copy-, Validator-, Fach- und Evaluatorstatus,
- boolesche Bestätigungen für unveränderte Quellen, ein sauberes Leak-Gate
  sowie die Ausgabe- und Versionierungsgrenze.

Unzulässig bleiben reale Bestands-, Treffer-, Quellen-, Unterstützungs- oder
Verteilungszahlen, lokale Provenienz, interne Rankings, Pfade, Namen, Hashes,
Snippets, Volltexte, Formeln und Werte.

Die synthetische Implementierungsabnahme ist kein realer Nutzungs-Witness.
Ein realer Witness ist laufbezogen, bleibt flüchtig und wird weder als
Repositorydatei noch als lokales Langzeitprotokoll persistiert. Browser-,
URL-only- und Opt-out-Routen schließen weiterhin vor jedem Konfigurations-,
Index-, Near-Copy- oder Acceptance-Zugriff kurz.
