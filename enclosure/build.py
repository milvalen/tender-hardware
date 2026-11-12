"""Build the TND-01 belt enclosure, run fit checks and export STEP/STL.

Usage (from the repository root):
    .venv/bin/python enclosure/build.py [--out out]

Exports go to out/ (ignored by Git). Released files are copied to exports/
only for tagged releases.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from build123d import Box, Color, Compound, Pos, export_step, export_stl  # noqa: E402

from params import Tnd01Params  # noqa: E402
from tnd01_belt import build  # noqa: E402

COLORS = {
    "front_shell": Color(0.12, 0.12, 0.11),
    "back_cover": Color(0.20, 0.22, 0.17),
    "key_step": Color(0.30, 0.30, 0.28),
    "key_next": Color(0.30, 0.30, 0.28),
    "key_ack": Color(0.30, 0.30, 0.28),
    "key_request": Color(0.30, 0.30, 0.28),
    "wheel": Color(0.30, 0.30, 0.28),
    "talk_button": Color(0.30, 0.30, 0.28),  # graphite: orange is for screen alerts only
}


def payload_dummy(p: Tnd01Params):
    pay = p.payload
    return Pos(0, p.pocket_center_y, p.shell.back_t + pay.depth / 2 + 0.2) * Box(pay.length, pay.width, pay.depth)


def check(parts: dict, p: Tnd01Params) -> list[str]:
    problems = []
    for name, part in parts.items():
        if not part.is_valid:
            problems.append(f"{name}: invalid solid")
        if part.volume <= 0:
            problems.append(f"{name}: zero volume")
    dummy = payload_dummy(p)
    for name in ("front_shell", "back_cover"):
        overlap = (parts[name] & dummy).volume
        if overlap > 1e-3:
            problems.append(f"{name}: overlaps the payload by {overlap:.2f} mm3")
    # Moving parts must not collide with the shell or the board.
    for name in [n for n in parts if n not in ("front_shell", "back_cover")]:
        overlap = (parts["front_shell"] & parts[name]).volume
        if overlap > 1e-3:
            problems.append(f"{name}: collides with front_shell by {overlap:.2f} mm3")
        overlap = (dummy & parts[name]).volume
        if overlap > 1e-3:
            problems.append(f"{name}: presses into the board by {overlap:.2f} mm3")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    p = Tnd01Params()
    parts = build(p)

    bb = Compound(children=list(parts.values())).bounding_box()
    print(f"envelope: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm (with belt loop and controls)")
    print(f"shell: {p.shell.width:.1f} x {p.shell.height:.1f} x {p.depth:.1f} mm")
    for name, part in parts.items():
        print(f"  {name:12s} volume {part.volume / 1000:6.2f} cm3")

    problems = check(parts, p)
    for msg in problems:
        print("FAIL", msg)

    for name, part in parts.items():
        part.label = name
        part.color = COLORS[name]
        export_stl(part, str(out / f"tnd01_{name}.stl"))
    assembly = Compound(children=list(parts.values()), label="TND-01")
    export_step(assembly, str(out / "tnd01_assembly.step"))
    print(f"exported to {out}/")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
