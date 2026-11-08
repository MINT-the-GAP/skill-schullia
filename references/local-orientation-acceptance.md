# Abnahme und flüchtiger Nutzungs-Witness der lokalen Orientierung

Diese Referenz beschreibt die enge Abschlussgrenze zwischen einem
schema-validierten Orientierungsbrief und einem auslieferbaren LiaScript-
Kandidaten. Sie ergänzt den
[Routingvertrag](local-orientation-routing.md), ersetzt aber weder die
[Autorenabnahme](authoring-acceptance.md) noch Fach-, Qualitäts- oder
Urheberrechtsprüfungen.

## Geltungsbereich

Der produktive Runner ist auf die festgelegten Vorwärtsfälle `L1` und `L3`
und die Scopes `public_only` und `both` begrenzt. Er liest einen fertig
erzeugten Kandidaten nur als begrenzte UTF-8-Markdowndatei oder als bereits im
Speicher vorhandenen Text. Eine Datei unter `.schullia-local`, eine TeX-Datei,
ein Link, ein Reparse Point, ein Hardlink oder eine während des Lesens
ausgetauschte Datei wird abgewiesen.

Vor jedem lokalen Zugriff muss der Kandidat den strikten LiaScript-Validator
im festgelegten Profil bestehen. Im Scope `both` bereitet der Runner den
Orientierungsbrief mit denselben vorab festgelegten, geschlossenen Filtern neu
vor. Freie Suchtexte, Lerngruppennamen, Dokumenttypen, Zeitstempel und private
Dateimerkmale sind keine Acceptance-Filter.

## Verbindliche Gates

Eine Freigabe setzt gemeinsam voraus:

1. geprüfte öffentliche Evidenz,
2. bestandene unabhängige Fachprüfung,
3. bestandene unabhängige Evaluatorprüfung,
4. einen warnungsfreien strikten LiaScript-Validatorlauf,
5. unveränderte private Quellen,
6. bestätigte Rohinhalts-, Ausgabe- und Versionierungsgrenzen,
7. `anti_copy_pass` aus einer echten, höchstens dreimal verwendbaren
   Anti-Copy-Session,
8. ein sauberes Git-Leak-Gate.

Im Scope `both` gelten zusätzlich:

- `local_search_performed=true`,
- `orientation_profile_prepared=true`,
- mindestens eine angewandte Feature-ID aus dem frisch erzeugten Brief,
- eine im fertigen Kandidaten unabhängig beobachtbare öffentliche
  Taxonomiegrundlage für jede angewandte Feature-ID.

Erst danach ruft der Runner `record_guidance_application(...)` mit exakt den
vier Gegenprüfungen `public_evidence`, `subject_review`,
`technical_validation` und `no_private_content_used` auf. Nur dieses Ergebnis
darf im Scope `both` `local_orientation_used=true` begründen. Der Scope
`public_only` ruft weder Guidance noch `record_guidance_application(...)` auf;
seine lokalen Statusflags bleiben falsch. Das separat ausgeführte Anti-Copy-
Gate macht einen Public-only-Autorenlauf nicht zu einem lokal orientierten
Autorenlauf.

## Feature-Nachweis

Der Runner akzeptiert nur IDs aus der öffentlichen geschlossenen
Feature-Taxonomie. Er belegt ihre Anwendung erneut am tatsächlichen
LiaScript-Kandidaten anhand öffentlicher Begriffe, Makros,
Operatorerkennung oder geschlossener Strukturdetektoren. Eine vom Autor bloß
behauptete ID, eine nur im Brief vorkommende ID oder ein interner lokaler
Treffer genügt nicht. Dieser Nachweis ist keine fachliche Bewertung und keine
Anforderungsbereichsklassifikation.

## Geschlossener Witness

Das Schema
[local-orientation-acceptance.schema.json](local-orientation-acceptance.schema.json)
erlaubt nur den Fall, Scope, das Fach, Filterdimensionen, geschlossene Status-
und Grundcodes, die drei lokalen Zustandsflags, tatsächlich angewandte
öffentliche Feature-IDs, die vier Gegenprüfungs-IDs, den Anti-Copy-Status
sowie boolesche Sicherheitsbestätigungen.

Der Witness enthält niemals Kandidaten- oder Quellenpfade, Dateinamen, lokale
IDs, Hashes, Texte, Werte, Formeln, Treffer-, Bestands-, Unterstützungs- oder
Verteilungszahlen, Rankings, Ähnlichkeitswerte oder Fundstellen. Er bleibt
laufbezogen und flüchtig. Repositorydateien dürfen weder reale Witnesses noch
reale Aktivierungsdaten aufnehmen.

`anti_copy_risk`, `anti_copy_inconclusive`, jede Warnung, ein blockierter oder
unbelegter Prüfschritt und jedes unsaubere Leak-Gate sind Release-Blocker.
Anti-Copy ist ein technisches Nähe-Gate, keine urheberrechtliche Freigabe.
