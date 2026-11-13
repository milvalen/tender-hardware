"""Make the print package for an on-demand print service.

Usage (from the repository root):
    .venv/bin/python enclosure/package.py [--out out/print-package]

The script builds the enclosure, runs the same checks as build.py and writes
one folder and one zip file with:
  sla/    STL files for SLA resin (front shell, key caps, SLA test coupon)
  pa12/   STL files for PA12 nylon, MJF or SLS (back cover, PA12 test coupon)
  step/   one STEP file for each part, for services that take STEP
  parts.csv  part, material, quantity, volume, size and print notes
  ORDER.txt  what to ask the service for

The package is a DRAFT while the board or plug values are not measured
(Tnd01Params.measured, Plugs.measured). Do not order a draft package.
The script exits with status 1 and writes nothing if a check fails.
Output goes under out/ (ignored by Git).
"""
import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from build123d import export_step, export_stl  # noqa: E402

from build import check, check_plugs, clip_strain  # noqa: E402
from coupon import build_coupons  # noqa: E402
from params import Tnd01Params  # noqa: E402
from tnd01_belt import build  # noqa: E402

SLA = "SLA resin, black or dark grey"
PA12 = "PA12 nylon, MJF or SLS, dyed black"

# part: (material folder, material, quantity, note)
PLAN = {
    "front_shell": ("sla", SLA, 1,
                    "No supports on the front face or in the 0.4 mm engraving. Supports on the open back rim only."),
    "back_cover": ("pa12", PA12, 1,
                   "Solid part, not FDM. The belt clip tongue bends {strain} in use: no cracks."),
    "key_step": ("sla", SLA, 2, "1 spare. No supports on the top face."),
    "key_next": ("sla", SLA, 2, "1 spare. No supports on the top face."),
    "key_ack": ("sla", SLA, 2, "1 spare. No supports on the top face."),
    "key_talk": ("sla", SLA, 2, "1 spare. No supports on the ribbed top face."),
    "coupon_sla": ("sla", SLA, 1,
                   "Test part: key hole, pilot hole and engraving sizes. Same resin and settings as the front shell."),
    "coupon_pa12": ("pa12", PA12, 1,
                    "Test part: a strip of the belt clip and screw clearance holes. Same process as the back cover."),
}


def git_state() -> tuple[str, bool]:
    """Short commit hash and True if the working tree has changes."""
    root = Path(__file__).resolve().parent.parent
    try:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                              capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "enclosure"], cwd=root,
                               capture_output=True, text=True, check=True).stdout.strip() != ""
    except (OSError, subprocess.CalledProcessError):
        return "unknown", True
    return head, dirty


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/print-package")
    args = ap.parse_args()

    p = Tnd01Params()
    parts = build(p)
    coupons = build_coupons(p)

    problems = check(parts, p)
    plug_problems = check_plugs(parts, p)
    if p.plugs.measured:
        problems += plug_problems
    for msg in problems:
        print("FAIL", msg)
    if problems:
        print("no package: fix the failures first")
        return 1
    for name, part in coupons.items():
        if not part.is_valid or len(part.solids()) != 1:
            print(f"FAIL {name}: not one valid solid")
            return 1
    parts = {**parts, **coupons}
    missing = [n for n in parts if n not in PLAN]
    if missing:
        print("FAIL no print plan for:", ", ".join(missing))
        return 1

    head, dirty = git_state()
    reasons = []
    if not p.measured:
        reasons.append("board values are not measured (Tnd01Params.measured)")
    if not p.plugs.measured:
        reasons.append("plug sizes are not measured (Plugs.measured)")
    if dirty:
        reasons.append("enclosure/ has uncommitted changes")
    for msg in plug_problems if not p.plugs.measured else []:
        reasons.append(f"plug warning: {msg}")
    draft = bool(reasons)

    name = f"tnd01-rev{p.revision}-{head}" + ("-DRAFT" if draft else "")
    root = Path(args.out)
    folder = root / name
    if folder.exists():
        shutil.rmtree(folder)
    for sub in ("sla", "pa12", "step"):
        (folder / sub).mkdir(parents=True)

    rows = []
    for part_name, part in parts.items():
        sub, material, qty, note = PLAN[part_name]
        note = note.format(strain=f"{clip_strain(p):.1%}")
        part.label = part_name
        export_stl(part, str(folder / sub / f"tnd01_{part_name}.stl"))
        export_step(part, str(folder / "step" / f"tnd01_{part_name}.step"))
        bb = part.bounding_box().size
        rows.append({
            "part": part_name,
            "file": f"{sub}/tnd01_{part_name}.stl",
            "material": material,
            "quantity": qty,
            "volume_cm3": f"{part.volume / 1000:.2f}",
            "size_mm": f"{bb.X:.1f} x {bb.Y:.1f} x {bb.Z:.1f}",
            "note": note,
        })

    with open(folder / "parts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    sla_cm3 = sum(float(r["volume_cm3"]) * r["quantity"] for r in rows if r["file"].startswith("sla/"))
    pa_cm3 = sum(float(r["volume_cm3"]) * r["quantity"] for r in rows if r["file"].startswith("pa12/"))
    lines = [f"TND-01 enclosure rev {p.revision}, tender-hardware commit {head}", ""]
    if draft:
        lines += ["DRAFT - DO NOT ORDER:"] + [f"  - {r}" for r in reasons] + [""]
    lines += [
        "Units: millimetres. One STL file for each part; quantities are in parts.csv.",
        "",
        f"Order 1 - SLA resin, black or dark grey: sla/ ({sla_cm3:.1f} cm3 with spares)",
        "  - Keep the 0.4 mm engraving on the front shell sharp: no supports on the front face.",
        "  - Key caps: no supports on the top faces.",
        "  - coupon_sla is a test part: print it with the same resin and settings as the front shell.",
        "",
        f"Order 2 - PA12 nylon, MJF or SLS, dyed black: pa12/ ({pa_cm3:.1f} cm3)",
        "  - Not FDM nylon: the belt clip must be one solid part.",
        "  - coupon_pa12 is a test part: print it with the same process as the back cover.",
        "",
        "Both orders can go to one service if it prints SLA and MJF or SLS.",
        "Ask the service for the hole and gap tolerance of each process.",
    ]
    (folder / "ORDER.txt").write_text("\n".join(lines) + "\n")

    archive = shutil.make_archive(str(root / name), "zip", root_dir=root, base_dir=name)
    for r in rows:
        print(f"  {r['part']:12s} {r['material']:38s} x{r['quantity']}  {r['size_mm']} mm")
    if draft:
        print("DRAFT - do not order:")
        for r in reasons:
            print("  -", r)
    print(f"package: {folder}/")
    print(f"zip:     {archive}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
