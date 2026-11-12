# tender-hardware

Enclosure, wiring and bill of materials for **TENDER TND-01** — a self-contained wearable unit for restaurant floor work. FIELD SERVICE UNIT.

Concept, functions and the Ink Industrial design language live in [tender-vault](https://github.com/milvalen/tender-vault).

![TND-01 belt module, rev 0.2](renders/tnd01_front.png)

## Status

Rev 0.2 of the belt module enclosure (concept B). It applies the design review of rev 0.1 in tender-vault (`10-concept/design-review-rev-0-1.md`). Geometry builds and passes the fit checks below. Not printed yet.

Stage 0 uses ready-made boards with snap-in connectors (Qwiic / STEMMA QT / Grove): no soldering. The enclosure is printed by an on-demand service (SLA resin preferred for sharp plate edges).

## Enclosure rev 0.2

| | |
|---|---|
| Payload | M5Stack StickS3, 48 × 24 × 15 mm (maker spec), lying landscape |
| Shell | 62 × 62 × 20.6 mm; 62 × 65 × 29.6 mm with belt loop and controls |
| Parts | `front_shell`, `back_cover` (with webbing belt loop for 25 mm webbing), `key_step` (convex, over StickS3 key A), `key_next` (pusher on the top face, over StickS3 key B), `key_ack` (flat) and `key_request` (ribbed) over the Dual Button unit |
| Markings | `UNIT TND-01` and the key functions `STEP`, `NEXT`, `ACK`, `REQ`, engraved 0.4 mm. Fill the engraving with white paint after the print |
| Fasteners | 4 × M2 self-tapping screws, back cover into front shell |
| Lower bay | 44 × 20 × 15.4 mm for the M5Stack Dual Button unit (Grove) |

Limits:

- Screen window, key A, key B, Dual Button key and USB-C positions are placeholders marked `[?]` in `enclosure/params.py`. Measure the real boards and update them before printing.
- Key B of the StickS3 must face up, toward the top pusher. If it faces down, turn the board and set display rotation 3 in the firmware.
- The thumb wheel and the talk button are off (`Controls.wheel`, `Controls.talk`) until electronics stand behind them. The visor is off (`Plates.visor`): it hid the top screen line from above.

![Exploded view](renders/tnd01_exploded.png)

## Usage

Requires Python ≥ 3.10. With [uv](https://docs.astral.sh/uv/):

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python build123d pyvista
.venv/bin/python enclosure/build.py     # checks + STEP/STL to out/
.venv/bin/python enclosure/render.py    # previews to renders/
```

`build.py` checks that every part is a valid solid, that the shell does not overlap the payload, and that keys do not collide with the shell or press into the board. It exits with status 1 on a failure.

Change dimensions in `enclosure/params.py`, not in the model code.

## Layout

| Path | Contents |
|---|---|
| `enclosure/params.py` | All dimensions |
| `enclosure/tnd01_belt.py` | Parametric model (build123d) |
| `enclosure/build.py` | Fit checks and STEP/STL export to `out/` |
| `enclosure/render.py` | Preview renders to `renders/` |
| `exports/` | Released STEP/STL files (tagged releases only) |

## Branches

`dev` is the default branch. `main` is the release branch and is never ahead of `dev`. Agents work in `ai/<area>` branches.
