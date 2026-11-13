"""Render preview images of the TND-01 belt enclosure.

Usage (from the repository root):
    .venv/bin/python enclosure/render.py [--out renders]

Writes PNG previews for docs with VTK (pyvista, off-screen): flat shading in
the Ink Industrial palette plus black feature lines, on an off-white paper
background. Not a photoreal render.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402
from build123d import Pos  # noqa: E402

from params import Tnd01Params  # noqa: E402
from tnd01_belt import build  # noqa: E402

PALETTE = {
    "front_shell": (0.17, 0.17, 0.16),
    "back_cover": (0.25, 0.27, 0.21),
    "key_step": (0.42, 0.42, 0.40),
    "key_next": (0.42, 0.42, 0.40),
    "key_ack": (0.42, 0.42, 0.40),
    "key_request": (0.42, 0.42, 0.40),
    "wheel": (0.42, 0.42, 0.40),
    "talk_button": (0.42, 0.42, 0.40),
}
PAPER = (0.95, 0.94, 0.91)
INK = (0.06, 0.06, 0.06)


def to_mesh(part, tol=0.03):
    verts, faces = part.tessellate(tol, 0.15)
    v = np.array([[p.X, p.Y, p.Z] for p in verts])
    f = np.hstack([np.full((len(faces), 1), 3), np.array(faces)]).ravel()
    return pv.PolyData(v, f).clean()


def render(parts, path, direction, explode=None, title=None, size=(1600, 1200)):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background(PAPER)
    pl.enable_anti_aliasing("ssaa")
    meshes = []
    for name, part in parts.items():
        if explode and name in explode:
            part = Pos(*explode[name]) * part
        mesh = to_mesh(part)
        meshes.append(mesh)
        pl.add_mesh(mesh, color=PALETTE[name], smooth_shading=False, ambient=0.35,
                    diffuse=0.75, specular=0.05)
        pl.add_mesh(mesh.extract_feature_edges(28, boundary_edges=False, non_manifold_edges=False),
                    color=INK, line_width=1.6)
    merged = pv.merge(meshes)
    center = np.array(merged.center)
    d = np.array(direction, dtype=float)
    d /= np.linalg.norm(d)
    pl.camera.focal_point = center
    pl.camera.position = center + d * merged.length * 2.2
    pl.camera.up = (0, 1, 0)
    pl.camera.view_angle = 24
    pl.reset_camera_clipping_range()
    if title:
        pl.add_text(title, position=(40, size[1] - 70), font_size=16, color=INK, font="courier")
        pl.add_text("UNIT TND-01 / BELT MODULE / REV 0.3", position=(40, size[1] - 105),
                    font_size=9, color=(0.35, 0.35, 0.35), font="courier")
    pl.screenshot(str(path))
    pl.close()
    print("wrote", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="renders")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    parts = build(Tnd01Params())
    render(parts, out / "tnd01_front.png", (-0.55, 0.45, 1.0), title="TND-01  FRONT")
    render(parts, out / "tnd01_back.png", (0.6, 0.35, -1.0), title="TND-01  BACK")
    explode = {
        "back_cover": (0, 0, -24),
        "key_step": (0, 0, 12), "key_ack": (0, 0, 12), "key_request": (0, 0, 12), "key_next": (0, 12, 0),
        "wheel": (-16, 0, 0), "talk_button": (0, 14, 0),
    }
    render(parts, out / "tnd01_exploded.png", (-0.8, 0.5, 0.75), explode=explode, title="TND-01  EXPLODED")


if __name__ == "__main__":
    main()
