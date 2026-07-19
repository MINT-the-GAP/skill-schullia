# Imperative Operatoren

## Vertrauensmodell

Halte drei Befundarten auseinander:

- `metadata_tag`: ausdrücklich im LiaScript-Header deklariert
- `body_pattern`: aus der formulierten Aufgabenaufforderung abgeleitet
- `bold_imperative_candidate`: nur typografisch erkannter Kandidat

Bewahre Metatag und Wortlaut getrennt. Überschreibe einen Konflikt wie
`tags: …, Angeben` gegenüber „Fülle … aus“ nicht stillschweigend. Berichte
beide Befunde und lies den Originalausschnitt.

## Normalisierung

Verwende [`operator-taxonomy.json`](operator-taxonomy.json) ausschließlich zur
sprachlichen Normalisierung, beispielsweise:

- „Gib … an“ → `angeben`
- „Wähle … aus“ → `auswaehlen`
- „Ordne … zu“ → `zuordnen`
- „Stelle … dar“ → `darstellen`

Erweitere Alias- und Musterlisten nur mit überprüfbaren Belegen. Erhalte die
Oberflächenform im Vorkommnisdatensatz.

## Didaktische Einordnung

Leite Anforderungsbereiche oder kognitive Niveaus nicht allein aus dem Verb
ab. Verwende eine solche Einordnung nur, wenn eine konkrete Taxonomiequelle
vorliegt, und zitiere diese Quelle. Die aktuelle Datei enthält bewusst keine
pauschale AFB-Zuordnung.

## Rechercheworkflow

1. Suche Aufgaben mit `--operator <id>`.
2. Begrenze reale Aufgaben mit `--usage-context task-content`.
3. Lies `operator_declared`, `operator_detected`, `operator_basis` und
   `operator_confidence`.
4. Öffne den gepinnten Quellausschnitt vor einer endgültigen Klassifikation.
