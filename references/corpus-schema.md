# Korpus und Index

## Generierte Artefakte

`scripts/sync_sources.py` erzeugt unter `corpus/`:

- `sources/<id>/files/`: vollständige lokale Quellsnapshots
- `sources.json`: Quellen, Revisionen, Lizenzen und Aktualitätsstatus
- `files.jsonl`: Inventar aller Dateien einschließlich Binärdateien
- `state.json` und `sync-report.json`: Sync-Zustand und Fehler

`scripts/build_index.py` erzeugt:

- `index.sqlite`: kanonischer Suchindex
- `tasks.jsonl`, `quizzes.jsonl`, `macros.jsonl`, `operators.jsonl`:
  deterministische Austauschformate

## SQLite-Tabellen

- `sources`: Quelle, Branch, Commit, Lizenz und Zustand
- `documents`: Dateiinhalt, Header, Überschriften und Parserwarnungen
- `tasks`: Aufgabenaufforderung, Operatorbefunde, Quiztypen und Makros
- `quizzes`: einzelne Syntaxknoten mit 1-basierten Zeilen
- `macros`: Makroaufrufe und Definitionen
- `operators` und `operator_occurrences`: normalisierte Operatoren und Belege
- `search_items` und optional `search_fts`: begrenzte Volltextsuche

Jeder abgeleitete JSONL-Datensatz enthält `_provenance` mit Quelle, Commit,
Pfad, Hash, Zeilen und gepinntem GitHub-Link.

## Kontextdisziplin

Lade nie pauschal den gesamten Korpus in den Modellkontext. Suche zuerst,
begrenze Trefferzahl und Ausgabegröße und lies danach nur die relevantesten
lokalen Originaldateien. Verwende `rg` zusätzlich für exakte Syntaxsuche.
