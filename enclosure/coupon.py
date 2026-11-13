"""Tolerance coupons: small test parts that go in the same print order as the
enclosure. They show which gaps the print service really gives, so the next
revision can use measured gaps instead of guesses.

coupon_sla (SLA resin, as the front shell and the key caps):
  - window at the payload pocket size: the StickS3 and the Dual Button unit
    must slide in (both are 48 x 24 mm by the maker drawings)
  - 5 square key holes with 0.10 to 0.30 mm gap per side around a key cap;
    try the spare key caps in them. The model uses Controls.key_travel_hole
  - 5 screw pilot bosses, 1.5 to 1.9 mm, for the M2 self-tapping screws.
    The model uses Shell.screw_pilot_d
  - the engraving depth at 0.3, 0.4 and 0.5 mm, each label cut to its own depth
coupon_pa12 (PA12 nylon, as the back cover):
  - a 10 mm wide strip of the real belt clip profile: bend it, cycle it, or
    break it without harm to the back cover
  - 3 screw clearance holes, 2.2 to 2.6 mm, with the screw head recess.
    The model uses Shell.screw_clear_d

Each label gives the value in hundredths of a millimetre per side for the key
holes and in tenths of a millimetre for the holes ("17" = 1.7 mm).
"""
from dataclasses import replace

from build123d import Box, Cylinder, Part, Pos

from params import Tnd01Params
from tnd01_belt import _engrave, belt_clip

KEY_GAPS = (0.10, 0.15, 0.20, 0.25, 0.30)  # per side
PILOTS = (1.5, 1.6, 1.7, 1.8, 1.9)
CLEARS = (2.2, 2.4, 2.6)
ENGRAVE_DEPTHS = (0.3, 0.4, 0.5)


def coupon_sla(p: Tnd01Params) -> Part:
    s, c, pl = p.shell, p.controls, p.plates
    t = 2.0  # plate
    key_t = s.front_wall + pl.lower_thickness  # key holes go through the real wall depth
    pw, ph, _ = p.pocket
    width = pw + 8.0
    rim = 4.0
    key_pitch = width / len(KEY_GAPS)

    # Rows from the top: window, key holes, pilot bosses, engraving.
    win_y = 0.0
    strip_half = (c.key_travel_hole + 3.0) / 2  # raised strip that carries the key holes
    key_y = win_y - ph / 2 - rim - strip_half - 0.5
    # Labels go on the thin plate, never under the raised strip: an engraving
    # there would be a closed void inside the part.
    key_label_y = key_y - strip_half - 2.0
    boss_y = key_label_y - 6.0
    boss_label_y = boss_y - 4.6  # below the boss, inside the plate
    eng_y = boss_label_y - 6.0
    top, bottom = win_y + ph / 2 + rim, eng_y - 3.5
    height = top - bottom
    cy = (top + bottom) / 2

    body = Pos(0, cy, t / 2) * Box(width, height, t)
    body -= Pos(0, win_y, t / 2) * Box(pw, ph, t + 1)
    body = _engrave(body, f"POCKET {p.payload.clearance * 100:.0f}", 0, win_y - ph / 2 - rim / 2, t,
                    c.legend_size, pl.engrave_depth)

    # Key holes: a raised strip at the real wall depth.
    body += Pos(0, key_y, key_t / 2) * Box(width - 2.0, 2 * strip_half, key_t)
    for i, gap in enumerate(KEY_GAPS):
        x = -width / 2 + key_pitch * (i + 0.5)
        hole = c.key + 2 * gap
        body -= Pos(x, key_y, key_t / 2) * Box(hole, hole, key_t + 1)
        body = _engrave(body, f"{gap * 100:.0f}", x, key_label_y, t, c.legend_size, pl.engrave_depth)

    # Screw pilot bosses, as deep as the real pilot holes.
    boss_h = 8.0
    boss_pitch = width / len(PILOTS)
    for i, d in enumerate(PILOTS):
        x = -width / 2 + boss_pitch * (i + 0.5)
        boss = Pos(x, boss_y, t + boss_h / 2) * Cylinder(d / 2 + 1.6, boss_h)
        boss -= Pos(x, boss_y, t + boss_h / 2 + 0.5) * Cylinder(d / 2, boss_h)
        body += boss
        body = _engrave(body, f"{d * 10:.0f}", x, boss_label_y, t, c.legend_size, pl.engrave_depth)

    # Engraving depth: each label is cut to the depth it names.
    eng_pitch = width / len(ENGRAVE_DEPTHS)
    for i, depth in enumerate(ENGRAVE_DEPTHS):
        x = -width / 2 + eng_pitch * (i + 0.5)
        body = _engrave(body, f"{depth:.1f}", x, eng_y, t, pl.label_size, depth)
    return body


def coupon_pa12(p: Tnd01Params) -> Part:
    s, c = p.shell, p.clip
    strip = 10.0
    width = strip + 14.0
    length = c.length + 4.0
    # Base plate as thick as the back cover; the clip hangs on its back face.
    base = Pos(0, -length / 2 + 2.0, s.back_t / 2) * Box(width, length, s.back_t)
    clip_p = replace(p, clip=replace(c, width=strip))
    from tnd01_belt import clip_top_y  # noqa: PLC0415 - same Y frame as the real cover
    shift = 0.0 - clip_top_y(clip_p)
    body = base + Pos(0, shift, 0) * belt_clip(clip_p)

    # Screw clearance holes with the head recess, in a column beside the clip.
    x = strip / 2 + 3.5
    for i, d in enumerate(CLEARS):
        y = -6.0 - 12.0 * i
        body -= Pos(x, y, s.back_t / 2) * Cylinder(d / 2, s.back_t + 1)
        body -= Pos(x, y, s.screw_head_depth / 2) * Cylinder(s.screw_head_d / 2, s.screw_head_depth + 0.01)
        body = _engrave(body, f"{d * 10:.0f}", -x, y, s.back_t, p.controls.legend_size, p.plates.engrave_depth)
    return body


def build_coupons(p: Tnd01Params | None = None) -> dict:
    p = p or Tnd01Params()
    return {"coupon_sla": coupon_sla(p), "coupon_pa12": coupon_pa12(p)}
