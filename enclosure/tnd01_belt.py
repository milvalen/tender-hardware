"""TND-01 belt module enclosure, concept B with the talk button of concept A.

Ink Industrial design language: asymmetric faceted shell, overlapping armour
plates with exposed screws, a visor over the screen, stencil-style markings,
one accent part (the talk button).

Parts:
  front_shell  - main body with payload pocket, lower bay, plates and visor
  back_cover   - screwed lid with the webbing belt loop
  key_step / key_ack / key_request - key caps (convex, flat, ribbed)
  wheel        - thumb wheel cap on the left side
  talk_button  - accent talk button on the top face

Stage 0 keys, wheel and talk button are form placeholders: the electronics
behind them (a snap-in Grove module in the lower bay) are not chosen yet.
"""
from build123d import (
    Align,
    Axis,
    Box,
    Cylinder,
    FontStyle,
    Location,
    Part,
    Polygon,
    Pos,
    Rot,
    Text,
    chamfer,
    extrude,
    fillet,
)

from params import Tnd01Params


def _outline(w, h, cuts):
    """Octagon-like outline with an individual cut on each corner."""
    tl, tr, br, bl = cuts
    x, y = w / 2, h / 2
    pts = [
        (-x + bl, -y), (x - br, -y), (x, -y + br), (x, y - tr),
        (x - tr, y), (-x + tl, y), (-x, y - tl), (-x, -y + bl),
    ]
    return Polygon(*pts, align=None)


def _screw_points(p: Tnd01Params):
    s = p.shell
    dx, dy = s.width / 2 - s.screw_inset, s.height / 2 - s.screw_inset
    return [(-dx, dy), (dx, dy), (dx, -dy), (-dx, -dy)]


def _key_xs(p: Tnd01Params):
    c = p.controls
    step = c.key + c.key_gap
    return [-step, 0.0, step]


def key_row_y(p: Tnd01Params):
    return p.pocket_center_y - p.pocket[1] / 2 - p.controls.key_row_from_pocket


def bay_center_y(p: Tnd01Params):
    s = p.shell
    top = p.pocket_center_y - p.pocket[1] / 2 - s.rib
    return top - s.bay_h / 2


def front_shell(p: Tnd01Params) -> Part:
    s, pay, pl, c = p.shell, p.payload, p.plates, p.controls
    d = p.depth
    body_h = d - s.back_t

    body = Pos(0, 0, s.back_t) * extrude(_outline(s.width, s.height, s.corner_cuts), body_h)
    front_edges = body.faces().sort_by(Axis.Z)[-1].edges()
    body = chamfer(front_edges, s.edge_chamfer)

    pw, ph, pd = p.pocket
    cy = p.pocket_center_y
    # Payload pocket and lower bay, open to the back.
    body -= Pos(0, cy, s.back_t + pd / 2) * Box(pw, ph, pd)
    body -= Pos(0, bay_center_y(p), s.back_t + pd / 2) * Box(s.bay_w, s.bay_h, pd)

    # Screen window through the front wall, with a shallow bevel recess.
    win_x = -pw / 2 + pay.clearance + pay.screen_offset + pay.screen_len / 2
    body -= Pos(win_x, cy, d - s.front_wall / 2) * Box(pay.screen_len, pay.screen_h, s.front_wall + 0.2)
    body -= Pos(win_x, cy, d - 0.4) * Box(pay.screen_len + 3, pay.screen_h + 3, 0.81)

    # USB-C port on the right wall, centred on the right end of the board.
    usb_z = s.back_t + pd / 2
    body -= Pos(pw / 2 + s.width / 4, cy, usb_z) * Box(s.width / 2, pay.usb_w, pay.usb_h)

    # Upper armour plate: frames the screen window, left side.
    up_l, up_r = -s.width / 2 + 2.5, win_x + pay.screen_len / 2 + 6
    up_b, up_t = cy - pay.screen_h / 2 - 3.5, s.height / 2 - 2.5
    upper = Polygon(
        (up_l + 3, up_b), (up_r, up_b), (up_r + 4, up_t - 6), (up_r - 2, up_t),
        (up_l + 6, up_t), (up_l, up_t - 6), (up_l, up_b + 3), align=None,
    )
    upper = Pos(0, 0, d) * extrude(upper, pl.thickness)
    upper -= Pos(win_x, cy, d + pl.thickness / 2) * Box(pay.screen_len + 3, pay.screen_h + 3, pl.thickness + 0.2)
    body += upper

    # Lower armour plate: carries the unit markings, overlaps the key row.
    ky = key_row_y(p)
    lo_t = ky - c.key / 2 - 2.0
    lo_b = -s.height / 2 + 3.0
    lo_l, lo_r = -s.width / 2 + 4.0, s.width / 2 - 2.5
    # Counter-clockwise, so the face normal is +Z and the plate extrudes outward.
    lower = Polygon(
        (lo_l, lo_b + 3), (lo_l + 3, lo_b), (lo_r - 5, lo_b), (lo_r, lo_b + 5),
        (lo_r, lo_t - 6), (lo_r - 9, lo_t), (lo_l, lo_t), align=None,
    )
    body += Pos(0, 0, d) * extrude(lower, pl.lower_thickness)
    lower_top = d + pl.lower_thickness

    # Engraved stencil-style markings on the lower plate.
    for text, y in (("UNIT TND-01", lo_t - 5.0), ("LOAD 3/4", lo_t - 11.0)):
        label = Text(text, font_size=pl.label_size, font_style=FontStyle.BOLD,
                     align=(Align.MIN, Align.CENTER))
        cut = Pos(lo_l + 7.5, y, lower_top - pl.engrave_depth) * extrude(label, pl.engrave_depth + 0.1)
        body -= cut

    # Exposed screw heads on the plates (dummy heads, M2 look).
    heads = [(up_l + 3.0, up_t - 3.0), (up_r - 1.0, up_b + 2.5),
             (lo_r - 3.5, lo_b + 4.0), (lo_l + 3.5, lo_t - 2.0)]
    for i, (hx, hy) in enumerate(heads):
        top = d + (pl.thickness if i < 2 else pl.lower_thickness)
        body -= Pos(hx, hy, top - 0.5) * Cylinder(2.0, 1.01)
        body += Pos(hx, hy, top - 0.2) * Cylinder(1.6, 1.6)
        body -= Pos(hx, hy, top + 0.4) * Box(2.4, 0.5, 0.6)

    # Visor over the screen: a plate that leaves the frame forward and tilts down.
    visor = Box(pl.visor_len, pl.visor_reach, pl.visor_t, align=(Align.CENTER, Align.MIN, Align.MIN))
    visor = Location((win_x, up_t - 1.0, d + pl.thickness - 0.5), (90 + pl.visor_tilt_deg, 0, 0)) * visor
    body += visor

    # Key holes from the front plate into the lower bay.
    for kx in _key_xs(p):
        body -= Pos(kx, ky, d) * Box(c.key_travel_hole, c.key_travel_hole, 2 * (s.front_wall + pl.lower_thickness) + 1)

    # Thumb wheel slot on the left wall, into the lower bay.
    wy = bay_center_y(p)
    slot_l, slot_r = -s.width / 2 - 1, -s.bay_w / 2 + 1
    body -= Pos((slot_l + slot_r) / 2, wy, s.back_t + pd / 2) * Box(slot_r - slot_l, c.wheel_d + 1, c.wheel_w + 1)

    # Talk button hole in the top wall.
    body -= Pos(c.talk_x, s.height / 2 - s.top_wall / 2, s.back_t + pd / 2) * Box(c.talk_w - 2, s.top_wall + 1, c.talk_d - 2)

    # Pilot holes for the back cover screws.
    for sx, sy in _screw_points(p):
        body -= Pos(sx, sy, s.back_t + 4) * Cylinder(s.screw_pilot_d / 2, 8)

    return body


def back_cover(p: Tnd01Params) -> Part:
    s, lp = p.shell, p.loop
    cover = extrude(_outline(s.width, s.height, s.corner_cuts), s.back_t)
    cover = chamfer(cover.faces().sort_by(Axis.Z)[0].edges(), 0.8)
    for sx, sy in _screw_points(p):
        cover -= Pos(sx, sy, s.back_t / 2) * Cylinder(s.screw_clear_d / 2, s.back_t + 1)
        cover -= Pos(sx, sy, s.screw_head_depth / 2) * Cylinder(s.screw_head_d / 2, s.screw_head_depth + 0.01)

    # Webbing loop on the back: the belt runs along X through the slot.
    loop = Pos(0, 0, -lp.depth / 2) * Box(lp.width, lp.height, lp.depth)
    loop = chamfer(loop.edges().filter_by(Axis.X).group_by(Axis.Z)[0], 1.2)
    slot_z = -lp.depth + lp.bridge_t + lp.slot_t / 2
    loop -= Pos(0, 0, slot_z) * Box(lp.width + 2, lp.slot_h, lp.slot_t)
    cover += loop
    return cover


def key_caps(p: Tnd01Params):
    """STEP (convex), ACK (flat), REQUEST (ribbed), seated in the key holes."""
    c, s, pl = p.controls, p.shell, p.plates
    ky = key_row_y(p)
    top_z = p.depth + pl.lower_thickness + c.key_proud
    stem = s.front_wall + pl.lower_thickness + 1.0
    caps = []
    for i, kx in enumerate(_key_xs(p)):
        cap = Pos(0, 0, -(stem + c.key_proud) / 2) * Box(c.key, c.key, stem + c.key_proud)
        if i == 0:
            cap = fillet(cap.faces().sort_by(Axis.Z)[-1].edges(), 1.8)
        elif i == 2:
            for gy in (-2.2, 0.0, 2.2):
                cap -= Pos(0, gy, -0.3) * Box(c.key + 1, 0.8, 0.8)
        caps.append(Pos(kx, ky, top_z) * cap)
    return caps


def wheel(p: Tnd01Params) -> Part:
    c, s = p.controls, p.shell
    faceted = Cylinder(c.wheel_d / 2, c.wheel_w)
    for k in range(18):
        a = 360 / 18 * k
        faceted -= Rot(0, 0, a) * Pos(c.wheel_d / 2 + 0.25, 0, 0) * Box(1.2, 1.2, c.wheel_w + 1)
    faceted -= Cylinder(1.5, c.wheel_w + 1)
    x = -s.width / 2 - c.wheel_proud + c.wheel_d / 2
    return Pos(x, bay_center_y(p), s.back_t + p.pocket[2] / 2) * faceted


def talk_button(p: Tnd01Params) -> Part:
    c, s = p.controls, p.shell
    cap = Box(c.talk_w, c.talk_h, c.talk_d, align=(Align.CENTER, Align.MIN, Align.CENTER))
    cap = chamfer(cap.edges().group_by(Axis.Y)[-1], 1.4)
    stem = Box(c.talk_w - 2.4, s.top_wall + 0.5, c.talk_d - 2.4, align=(Align.CENTER, Align.MAX, Align.CENTER))
    return Pos(c.talk_x, s.height / 2, s.back_t + p.pocket[2] / 2) * (cap + stem)


def build(p: Tnd01Params | None = None) -> dict:
    p = p or Tnd01Params()
    step, ack, request = key_caps(p)
    return {
        "front_shell": front_shell(p),
        "back_cover": back_cover(p),
        "key_step": step,
        "key_ack": ack,
        "key_request": request,
        "wheel": wheel(p),
        "talk_button": talk_button(p),
    }
