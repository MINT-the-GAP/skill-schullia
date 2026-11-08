# lia-electro: Schaltpläne und Ergänzungsquiz

## Quellenstand und Status

Diese Referenz wurde statisch gegen die vollständig gespeicherte `README.md`
von MINT-the-GAP/lia-electro, Revision
`02937818345dd3bb139afa3df275401301199c1e`, README-SHA-256
`d758253cb1987a71cf4e8f2dd7b422f61298914b5290fc9ac9e5bbaa5269237a`,
geprüft. Das Template bezeichnet seine Kopplung an die globale Board-Registry
von `lia-coordinate` selbst als Proposal. Statische Syntaxprüfung ersetzt daher
keinen Browser-Smoke-Test des Editors, der Speicherung und des Quiz.

## Direkte Importe

Kurse importieren alle drei Abhängigkeiten direkt und in dieser Reihenfolge:

```text
import: https://cdn.jsdelivr.net/gh/LiaTemplates/JSXGraph@main/README.md
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-coordinate/Proposal/README.md
import: https://raw.githubusercontent.com/MINT-the-GAP/lia-electro/main/README.md
```

Für den Prüf-Witness gelten die oben genannte commit-gepinnte Revision und die
jeweils inventarisierten Revisionen von JSXGraph und `lia-coordinate`. Verlasse
dich nicht auf die verschachtelten Importe der Template-README.

## Board und Editor

| Makro | Öffentliche Autorenform |
|---|---|
| `@Electro(spec)` | Erzeugt über `@CoordinateSystem` ein neues Board und bindet den Editor ein. Die Semikolon-Spec benötigt eine eindeutige `id`; `snap`/`raster` hat den Standard `0.5`, `stub` den Standard `0.35`. |
| `@ElectroOn(spec)` | Bindet den Editor an ein zuvor erzeugtes Coordinate-Board. Die Board-ID darf positional oder als `id=...` stehen; die mehrdeutigen IDs `0` und `1` müssen benannt werden. |

`@DGS` und `@ElectroOn` nicht gleichzeitig an dasselbe Board binden. Beide
verwalten Pointer-Ereignisse und eigene Werkzeugleisten.

## Exportierter Makroblock

Die verbindliche Reihenfolge lautet:

```text
CoordinateSystem → Komponenten → Kabel → ElectroOn → optionales Ergänzungsquiz
```

Alle Komponenten verwenden ein einzelnes Backtick-Argument mit dieser
Semikolongrammatik:

```text
board;id;x;y;rotation[;name;value;showMeasurement;locked]
```

- `board` und `id`: `[A-Za-z0-9_-]{1,80}`,
- `x` und `y`: endliche Zahlen,
- `rotation`: `0`, `90`, `180` oder `270`,
- `name` und `value`: einzeilig, problematische Semikola nur in der vom
  Exporter erzeugten kodierten Form,
- `showMeasurement`: nur bei Volt- und Amperemeter; `0` oder `1`,
- `locked`: `0`, `1` oder leer.

Öffentliche Komponentenmakros besitzen englische und, soweit dokumentiert,
deutsche Aliasse:

- Quelle und passive Bauteile: `@ElectroBattery`/`@ElectroBatterie`,
  `@ElectroVoltageSource`/`@ElectroSpannungsquelle`,
  `@ElectroResistor`/`@ElectroWiderstand`,
  `@ElectroVariableResistor`/`@ElectroRegelbarerWiderstand`,
  `@ElectroCapacitor`/`@ElectroKondensator`, `@ElectroInductor`/`@ElectroSpule`,
  `@ElectroIronCoreInductor`/`@ElectroSpuleMitEisenkern`;
- Messgeräte und Verbraucher: `@ElectroVoltmeter`,
  `@ElectroAmmeter`/`@ElectroAmperemeter`, `@ElectroMotor`,
  `@ElectroLamp`/`@ElectroLampe`;
- Halbleiter und Schalter: `@ElectroDiode`, `@ElectroPhotodiode`,
  `@ElectroLED`, `@ElectroTransistor`, `@ElectroSwitch`/`@ElectroSchalter`,
  `@ElectroChangeoverSwitch`/`@ElectroUmschalter`;
- weitere Symbole: `@ElectroGround`/`@ElectroErde`,
  `@ElectroAntenna`/`@ElectroAntenne`,
  `@ElectroTransformer`/`@ElectroTransformator`.

Kabel verwenden `@ElectroWire` beziehungsweise `@ElectroKabel` mit:

```text
board;id;fromComponent;fromPort;toComponent;toPort;route
```

`route` ist `horizontal-first` oder `vertical-first`. Anschluss-IDs müssen zum
jeweiligen Symboltyp passen. Erfinde keine weiteren Bauteil- oder Anschluss-IDs.

## Exportprofil

`@ElectroOn` kann die belegten Listen
`components=[stabile-ID;...]` und `restrictions=[stabile-ID;...]` enthalten.
Fehlende beziehungsweise leere Komponentenlisten lassen die volle Palette zu;
`components=[0]` bezeichnet ausdrücklich keine neu platzierbaren Bauteile.
Bei Restriktionen bedeutet auch `[0]` uneingeschränkt. Die beiden
Rechtsklickrestriktionen `100` und `110` sind gegenseitig ausgeschlossen;
`100` gewinnt bei einer handschriftlichen Kollision.

## Ergänzungsquiz

`@ElectroErgaenzungsquiz` und `@ElectroCompletionQuiz` sind gleichwertige
Aliasse. Der Aufgabentext steht als normaler Absatz unmittelbar vor dem Makro.
Die Spec lautet:

```text
board;condition=Bedingung;component=Messgerät;target=Wert;tolerance=Wert;required=[Typ:Anzahl];preserve=1;changed=1
```

Belegte Bedingungen sind `closed`, `ammeter-current`, `voltmeter-voltage`,
`total-current` und `equivalent-resistance`. Messbedingungen benötigen die in
der README ausgewiesenen Kombinationen aus `component`, `target` und
`tolerance`. Werte dürfen SI-Präfixe und Einheiten enthalten. `mode=signed`
aktiviert den vorzeichenbehafteten Vergleich; ohne diese Option wird der Betrag
verglichen. `required` fordert neu eingesetzte Bauteile, `preserve=1` schützt
die Vorgabe und `changed=1` weist eine unveränderte Abgabe zurück.

## Grenzen der statischen Prüfung

Statisch prüfbar sind Direktimporte, Reihenfolge, öffentliche Makronamen,
Backtick-/Semikolonstruktur, Board-ID-Bezüge und die grobe Quiz-Spec. Nur im
Browser prüfbar sind Editorinitialisierung, Pointer- und Tastaturbedienung,
Persistenz, Undo/Redo, Export, elektrische Knotenanalyse, Messwertanzeige und
die tatsächliche Laufzeitbewertung des Ergänzungsquiz. Die Analyse ist laut
README auf lineare stationäre Gleichstromnetze und die dort ausdrücklich
unterstützten Quellen, Widerstände sowie idealen Messgeräte begrenzt.
