# tender-hardware

Enclosure, wiring and bill of materials for **TENDER TND-01** — a self-contained wearable unit for restaurant floor work. FIELD SERVICE UNIT.

Concept, functions and the Ink Industrial design language live in [tender-vault](https://github.com/milvalen/tender-vault).

## Status

Planned. Stage 0 uses ready-made boards with snap-in connectors (Qwiic / STEMMA QT / Grove): no soldering. The enclosure is printed by an on-demand service (SLA resin preferred for sharp plate edges).

## Planned layout

| Path | Contents |
|---|---|
| `enclosure/` | Parametric enclosure as code ([build123d](https://github.com/gumyr/build123d)); exports STEP and STL |
| `exports/` | Released STEP/STL files for printing (tagged releases only) |
| `wiring/` | Module wiring diagrams |
| `bom.md` | Bill of materials with sources and prices |

## Branches

`dev` is the default branch. `main` is the release branch and is never ahead of `dev`. Agents work in `ai/<area>` branches.
