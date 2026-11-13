"""Build the TND-01 belt enclosure, run fit checks and export STEP/STL.

Usage (from the repository root):
    .venv/bin/python enclosure/build.py [--out out]

Exports go to out/ (ignored by Git). Released files are copied to exports/
only for tagged releases.
"""
import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from build123d import Box, Color, Compound, Cylinder, Pos, export_step, export_stl  # noqa: E402

from params import Tnd01Params  # noqa: E402
from tnd01_belt import _screw_points, bay_center_y, build  # noqa: E402

COLORS = {
    "front_shell": Color(0.12, 0.12, 0.11),
    "back_cover": Color(0.20, 0.22, 0.17),
    "key_step": Color(0.30, 0.30, 0.28),
    "key_next": Color(0.30, 0.30, 0.28),
    "key_ack": Color(0.30, 0.30, 0.28),
    "key_talk": Color(0.30, 0.30, 0.28),
    "wheel": Color(0.30, 0.30, 0.28),
    "talk_button": Color(0.30, 0.30, 0.28),  # graphite: orange is for screen alerts only
}


def payload_dummy(p: Tnd01Params):
    pay = p.payload
    return Pos(p.pocket_x, p.pocket_center_y, p.shell.back_t + pay.depth / 2 + 0.2) * Box(pay.length, pay.width, pay.depth)


def dual_dummy(p: Tnd01Params):
    """Dual Button unit as a block up to the top of its keys."""
    d = p.dual
    return Pos(p.pocket_x, bay_center_y(p), p.shell.back_t + d.height / 2) * Box(d.length, d.width, d.height)


def clip_strain(p: Tnd01Params) -> float:
    """Peak strain at the tongue root when the tip opens to let the thickest
    belt past the ridge: eps = 3 t d / (2 L^2), cantilever with an end load."""
    c = p.clip
    free = c.length - c.root_h - c.flare_len / 2
    opening = c.belt_max + c.ridge_h - c.gap
    return 3 * c.thickness * opening / (2 * free * free)


def check(parts: dict, p: Tnd01Params) -> list[str]:
    problems = []
    for name, part in parts.items():
        if not part.is_valid:
            problems.append(f"{name}: invalid solid")
        if part.volume <= 0:
            problems.append(f"{name}: zero volume")
    dummies = {"StickS3": payload_dummy(p), "Dual Button unit": dual_dummy(p)}
    for name in ("front_shell", "back_cover"):
        for what, dummy in dummies.items():
            overlap = (parts[name] & dummy).volume
            if overlap > 1e-3:
                problems.append(f"{name}: overlaps the {what} by {overlap:.2f} mm3")
    # Moving parts must not collide with the shell or the boards.
    for name in [n for n in parts if n not in ("front_shell", "back_cover")]:
        overlap = (parts["front_shell"] & parts[name]).volume
        if overlap > 1e-3:
            problems.append(f"{name}: collides with front_shell by {overlap:.2f} mm3")
        for what, dummy in dummies.items():
            overlap = (dummy & parts[name]).volume
            if overlap > 1e-3:
                problems.append(f"{name}: presses into the {what} by {overlap:.2f} mm3")
    # Each screw pilot hole needs solid wall around it, clear of every cavity.
    s = p.shell
    for sx, sy in _screw_points(p):
        r, wall = s.screw_pilot_d / 2, 0.8
        ring = Pos(sx, sy, s.back_t + 4) * Cylinder(r + wall, 8)
        missing = ring.volume - (ring & parts["front_shell"]).volume
        if missing > math.pi * r * r * 8 + 0.5:
            problems.append(f"screw at ({sx:.1f}, {sy:.1f}): less than {wall} mm wall around the pilot hole")
    if p.back_mount == "clip":
        strain = clip_strain(p)
        if strain > p.clip.max_strain:
            problems.append(f"belt clip: {strain:.1%} strain at full opening, limit {p.clip.max_strain:.0%}")
    cl, cr = p.cable_bay
    if cr - cl < p.shell.cable_bay_min:
        problems.append(f"cable bay is {cr - cl:.1f} mm wide, needs {p.shell.cable_bay_min:.1f} mm")
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
    print(f"envelope: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm (with back mount and controls)")
    print(f"shell: {p.shell.width:.1f} x {p.shell.height:.1f} x {p.depth:.1f} mm")
    cl, cr = p.cable_bay
    print(f"lower bay: {p.bay[0]:.1f} x {p.bay[1]:.1f} mm, cable bay: {cr - cl:.1f} mm wide")
    if p.back_mount == "clip":
        print(f"belt clip: {clip_strain(p):.1%} strain at full opening for a {p.clip.belt_max} mm belt")
    for name, part in parts.items():
        print(f"  {name:12s} volume {part.volume / 1000:6.2f} cm3")

    problems = check(parts, p)
    for msg in problems:
        print("FAIL", msg)

    # Remove exports of parts that this revision no longer has, so that an old
    # mesh cannot go to the print service by mistake. Only our own files go.
    for old in [*out.glob("tnd01_*.stl"), *out.glob("tnd01_*.step")]:
        old.unlink()

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
