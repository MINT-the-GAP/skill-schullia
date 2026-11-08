# SchulLia Knowledge

`schullia-knowledge` ist ein portabler Agent Skill zum belegten Erstellen,
Überarbeiten, Erklären und Klassifizieren von SchulLia- und LiaScript-Aufgaben.
Er verbindet die öffentlichen Repositories von MINT-the-GAP mit der offiziellen
LiaScript-Dokumentation und ausgewählten LiaTemplates-Referenzen.

Der Skill erweitert Agent-Anwendungen wie Claude Code oder GitHub Copilot. Ein
reines Chatmodell ohne Skill-, Datei- und Werkzeugzugriff kann dieses Repository
nicht automatisch verwenden.

## Was der Skill bietet

- LiaScript-Dokumentköpfe, Metadaten und Grundsyntax
- Quizstrukturen, Makros, Hinweise, Feedback und Lösungen
- imperative Operatoren, Aufgabenarten und erkannte Zuordnungen
- Fach-, Themen- und Klassenstufenkontext aus realen Aufgaben
- commit-gepinnte Belege mit Repository, Pfad, Zeilen und Revision
- automatische Erkennung neuer öffentlicher MINT-the-GAP-Repositories
- lokale Suche ohne vollständiges Laden des Korpus in den Modellkontext
- einen im Hauptskill verankerten `schullia-gamification`-Skill mit
  read-only Positionsmapper für Erde, Pflanzen und importierte Loot-Ziele

## Unterstützte Agenten

Die `SKILL.md` folgt dem offenen
[Agent-Skills-Standard](https://agentskills.io/specification). Dadurch nutzt
jeder kompatible Agent dieselbe kanonische Wissensbasis.

| Agent-Umgebung | Unterstützung |
| --- | --- |
| OpenAI Codex | nativer Agent Skill; zusätzliche UI-Metadaten unter `agents/openai.yaml` |
| [Claude Code](https://code.claude.com/docs/en/slash-commands) | nativer Agent Skill unter `.claude/skills/` |
| [GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | Agent Mode, CLI, Cloud Agent und weitere skillfähige Copilot-Oberflächen |
| [Gemini CLI](https://geminicli.com/docs/cli/skills/) | nativer Agent Skill unter `.gemini/skills/` oder `.agents/skills/` |
| [Cursor](https://cursor.com/docs/skills) | nativer Agent Skill |
| [Windsurf](https://docs.windsurf.com/de/windsurf/cascade/skills) | nativer Agent Skill unter `.windsurf/skills/` oder `.agents/skills/` |
| weitere Anbieter | nutzbar, sofern sie Agent Skills oder als Fallback `AGENTS.md` unterstützen |

Copilot-Inline-Vervollständigungen sind keine Agent-Ausführung und laden den
Skill nicht vollständig. Verwende dafür Copilot Chat im Agent Mode, die CLI oder
eine andere skillfähige Copilot-Oberfläche.

## Nutzung in Browser-LLM-Oberflächen

Ein eingefügter Link installiert oder aktiviert keinen Agent Skill. Eine
Browser-LLM kann `schullia-knowledge` nur eingeschränkt verwenden, wenn sie die
verlinkte `SKILL.md` und die für die konkrete Anfrage benötigten Referenzen
tatsächlich öffnen kann.

| Umgebung | Kanonische Anweisungen und Referenzen | Lokaler Korpus und Prüfskripte |
| --- | --- | --- |
| Installierter, werkzeugfähiger Agent | liest `SKILL.md` und geroutete lokale Dateien | verfügbar, sofern Datei-, Shell- und Python-Zugriff bestehen |
| Browser-LLM mit URL-Zugriff | liest öffentliche Dateien gezielt über ihre URLs | gewöhnlich nicht verfügbar; fehlende Prüfungen müssen genannt werden |
| Reines Chatmodell ohne URL- oder Dateizugriff | kann verlinkte Inhalte nicht selbst laden | nicht verfügbar |

Verwende für den schnellen Einstieg den
[kopierbaren Browser-Startprompt](assets/browser-bootstrap-prompt.md) oder dessen
[Raw-Version](https://raw.githubusercontent.com/MINT-the-GAP/skill-schullia/main/assets/browser-bootstrap-prompt.md)
und ergänze dort die eigentliche SchulLia-Anfrage. Für eigene Repository-,
Branch- oder Metadatenvorgaben steht zusätzlich das vollständige
[Browser-Autorenpaket](assets/browser-authoring-pack.md) als
[Raw-Version](https://raw.githubusercontent.com/MINT-the-GAP/skill-schullia/main/assets/browser-authoring-pack.md)
bereit. Es enthält den parametrischen Hauptprompt, den selektiven Ladeplan und
vier kurze Anwendungsrezepte. Beide Dateien verweisen auf die kanonische
[SKILL.md](https://raw.githubusercontent.com/MINT-the-GAP/skill-schullia/main/SKILL.md)
und sind keine zweite Skillkopie.

Browserausgaben verwenden für vollständige Wochenaufgaben `weekly` und sonst
`course`. Ohne ausdrückliche Bitte um einen Einfügeausschnitt entsteht ein
vollständiges LiaScript-Dokument mit Hauptkopf und allen benötigten
Direktimporten; das gilt auch für eine einzelne eigenständig nutzbare Aufgabe,
die als Ein-Aufgaben-Kurs ausgegeben wird. Nur ein eindeutig verlangtes Fragment
bleibt headerlos.

Kann die Oberfläche keine URLs öffnen, stelle ihr die vollständige `SKILL.md`
und danach nur die von deren Routing verlangten Referenzdateien als Anhänge oder
eingefügten Text bereit. Ohne lokalen Datei-, Shell- und Python-Zugriff sind
insbesondere die lokale Korpussuche, die Aktualisierung des Korpus und
`scripts/validate_lia.py` nicht ausführbar. Eine so erzeugte Browserausgabe muss
daher in einem eingeschränkten Prüf-Witness aufführen, welche Quellen gelesen,
welche Prüfungen tatsächlich ausgeführt und welche lokalen Prüfungen nicht
durchgeführt wurden.

Für eine nachvollziehbare manuelle Abnahme steht das
[anbieterneutrale Browser-End-to-End-Testpaket](assets/browser-e2e-test-pack.md)
bereit. Es trennt die Erreichbarkeit öffentlicher URLs, lokale
Validatorergebnisse und einen tatsächlich durchgeführten Browser-LLM-Lauf. Die
Ergebnistabelle ist bewusst nicht vorab ausgefüllt.

Für Skillpflege und Freigabeentscheidungen verbindet die
[Verhaltensabnahme](references/authoring-acceptance.md) fünf lokale
Vorwärtsfälle mit unabhängiger Autoren-/Bewertungsrolle, strikter Validierung
und dem getrennten Browsergate. Sie ist kein zusätzlicher Stilführer und wird
bei gewöhnlichen Autorenanfragen nicht geladen.

## Voraussetzungen

- Python 3.10 oder neuer, ausschließlich mit Standardbibliothek
- Git
- Internetzugriff für die Synchronisierung
- eine Agentenumgebung mit Datei- und Shellzugriff
- optional `GITHUB_TOKEN` oder `GH_TOKEN`, um GitHub-API-Limits zu erhöhen

## Installation

### Empfohlen: GitHub CLI

Eine aktuelle GitHub CLI mit `gh skill` installiert das Repository am richtigen
Ort und speichert zugleich Herkunftsinformationen für spätere Updates. Weil die
`SKILL.md` in diesem Repository direkt im Stamm liegt, muss ihr Pfad angegeben
werden:

```text
gh skill install MINT-the-GAP/skill-schullia SKILL.md --agent <agent> --scope user
```

Ersetze `<agent>` beispielsweise durch:

- `codex`
- `claude-code`
- `github-copilot`
- `gemini-cli`
- `cursor`
- `windsurf`

Wiederhole den Befehl für jede gewünschte Agentenumgebung. Mit
`--scope project` wird der Skill nur im aktuellen Projekt installiert; ohne
Scope-Angabe ist `project` der Standard. Details stehen in der offiziellen
[GitHub-CLI-Dokumentation](https://cli.github.com/manual/gh_skill_install).

Falls `gh` den Unterbefehl `skill` noch nicht kennt, aktualisiere GitHub CLI oder
verwende die manuelle Installation.

### Manuell mit Git

Klone das vollständige Repository in einen unterstützten Skill-Ordner. Der
Zielordner sollte wegen des Namens im Frontmatter `schullia-knowledge` heißen:

```text
git clone https://github.com/MINT-the-GAP/skill-schullia.git <skill-verzeichnis>/schullia-knowledge
```

Typische persönliche Zielverzeichnisse sind:

| Agent | Zielverzeichnis |
| --- | --- |
| Codex | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| GitHub Copilot | `~/.copilot/skills/` oder `~/.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` oder `~/.agents/skills/` |
| Windsurf | `~/.codeium/windsurf/skills/` oder `~/.agents/skills/` |

Für projektbezogene Installationen unterstützen viele Agenten
`.agents/skills/schullia-knowledge/`. Claude Code verwendet stattdessen
`.claude/skills/schullia-knowledge/`; Copilot akzeptiert zusätzlich
`.github/skills/schullia-knowledge/`.

## Erster Wissensabgleich

Der generierte Korpus wird bewusst nicht mit Git ausgeliefert. Führe nach einer
frischen Installation im Skill-Verzeichnis einmal aus:

```text
python scripts/update_knowledge.py
python scripts/search_knowledge.py status
```

Verwende `python3`, falls Python 3 auf deinem System unter diesem Namen
installiert ist. Bei der ersten passenden Anfrage führt ein werkzeugfähiger
Agent diesen Schritt gemäß `SKILL.md` ebenfalls selbst aus.

## Verwendung

Der Agent kann den Skill anhand seiner Beschreibung automatisch auswählen. Du
kannst ihn auch ausdrücklich nennen, zum Beispiel:

```text
Nutze schullia-knowledge, um eine Mathematikaufgabe für Klasse 7 als
LiaScript-Quiz zu erstellen. Verwende einen passenden Operator und belege die
gewählte Struktur mit realen Quellen.
```

Weitere Beispiele:

- „Prüfe den LiaScript-Header dieses Kurses und ergänze fehlende Angaben.“
- „Klassifiziere Operator und Aufgabenart, ohne Widersprüche zu verschweigen.“
- „Erkläre diese Quizsyntax und zeige passende MINT-the-GAP-Beispiele.“
- „Erstelle nur einen einfügbaren Aufgabenausschnitt, keinen vollständigen Kurs.“
- „Kartiere alle technisch möglichen Erde-/Pflanzenpositionen dieses Kurses und
  entwirf drei strukturell verschiedene Gamification-Varianten.“

## Quellen

Bei jedem Abgleich werden alle öffentlichen Repositories der Organisation
[MINT-the-GAP](https://github.com/orgs/MINT-the-GAP/repositories) über die
GitHub-API ermittelt. Dadurch werden auch später neu angelegte Repositories
regulär berücksichtigt. Gespeichert wird jeweils ein commit-gepinnter Snapshot
des Default-Branches.

Zusätzlich sind folgende Dokumentationsquellen fest konfiguriert:

- die offizielle LiaScript-Dokumentation
- Algebrite
- JSXGraph
- Speech-Recognition-Quiz
- ABCjs
- AVR8js

„Fest konfiguriert“ bedeutet nicht, dass ihr Inhalt eingefroren ist: Beim
Abgleich wird der aktuelle Stand des jeweils angegebenen Branches aufgelöst.
Neue zusätzliche Einzelquellen werden in `references/sources.json` eingetragen.

Falls die GitHub-Organisationsabfrage ausfällt, verwendet der Skill die
Fallback-Liste aus `references/sources.json` und kennzeichnet dies im
Synchronisationsbericht. Ein ganz neues Repository kann während eines solchen
Ausfalls erst nach Ergänzung der Fallback-Liste erkannt werden.

## Aktualisierung

Skill-Code und Wissenskorpus werden getrennt aktualisiert.

### Installierten Skill-Code aktualisieren

Bei einer Installation mit GitHub CLI:

```text
gh skill update --dry-run
gh skill update --all
```

Bei einer manuellen Git-Installation im Skill-Verzeichnis:

```text
git pull --ff-only
```

Weitere Optionen beschreibt die
[GitHub-CLI-Dokumentation](https://cli.github.com/manual/gh_skill_update).

### MINT-the-GAP- und Dokumentationsquellen aktualisieren

Es läuft kein Hintergrunddienst. Einen Neuabgleich erzwingst du mit:

```text
python scripts/update_knowledge.py --force
```

Für einen altersabhängigen Abgleich verwendet der Skill:

```text
python scripts/update_knowledge.py --max-age-hours 24
```

Normale Änderungen und neue öffentliche Repositories von MINT-the-GAP brauchen
keine Änderung am Skill-Code. Der Parser muss nur angepasst werden, wenn neue
oder bisher falsch erkannte Syntax auftaucht.

## Repository-Struktur

```text
SKILL.md                         kanonische Agent-Skill-Anweisung
skills/schullia-gamification/   verankerter Gamification-Skill samt Mapper
AGENTS.md                        knapper anbieterübergreifender Repo-Einstieg
CLAUDE.md / GEMINI.md            dünne Imports für Anbieter-Kontextdateien
.github/copilot-instructions.md  knapper Copilot-Einstieg
agents/openai.yaml               optionale Codex-Oberflächenmetadaten
references/                      Taxonomien, Quellen und Fachreferenzen
references/authoring-acceptance.md  Verhaltensabnahme und Freigabegates
references/syntax-contract.json    maschinenlesbarer Syntax- und Templatevertrag
references/template-electro.md     geprüfte lia-electro-API und Importfolge
scripts/                         Synchronisierung, Suche und Validierung
assets/                          Vorlagen und anbieterneutrale Browser-Einstiege
assets/browser-authoring-pack.md  parametrischer Hauptprompt und URL-Ladeplan
assets/browser-bootstrap-prompt.md  kopierbarer Einstieg für Browser-LLMs
assets/browser-e2e-test-pack.md  manuelle, anbieterneutrale Browser-Abnahme
corpus/                          generiert und nicht in Git eingecheckt
```

Die Anbieterdateien duplizieren den Skill nicht. `SKILL.md`, `references/`,
`scripts/` und `assets/` bleiben die gemeinsame Quelle für alle Agenten.

## Validierung

```text
python scripts/test_parser.py
python scripts/test_sync.py
python scripts/test_validate_lia.py
python scripts/test_template_inventory.py
python scripts/template_inventory.py --check
python skills/schullia-gamification/scripts/test_map_course.py
python skills/schullia-gamification/scripts/test_profile_weekly_courses.py
python skills/schullia-gamification/scripts/profile_weekly_courses.py --check
python scripts/validate_corpus.py
python scripts/validate_corpus.py --deep
```

## Sicherheit und Lizenzen

Synchronisierte Inhalte gelten als nicht vertrauenswürdige Daten. Der Skill
analysiert darin enthaltene Programme und Modellanweisungen nur statisch und
führt sie nicht aus. Der lokale Rohkorpus wird nicht eingecheckt.

Öffentliche Lesbarkeit ist keine Nutzungslizenz. Prüfe vor einer Weitergabe des
Rohkorpus die Lizenz jeder Quelle.

## Autor und Projektlizenz

- Autor und Entwicklung: Martin Lommatzsch
- Projekt: [MINT-the-GAP](https://github.com/MINT-the-GAP)
- Lizenz dieses Skill-Repositories: noch nicht festgelegt

Solange keine `LICENSE`-Datei vorhanden ist, werden durch die Veröffentlichung
keine allgemeinen Wiederverwendungsrechte eingeräumt.
