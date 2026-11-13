"""TND-01 belt module enclosure rev 0.4, concept B.

Ink Industrial design language: asymmetric faceted shell, overlapping armour
plates with exposed screws, stencil-style markings. Orange stays on the
screen for alerts only, so no part of the shell is orange.

Rev 0.2 follows the design review of rev 0.1 (tender-vault
10-concept/design-review-rev-0-1.md): one part for each firmware key, each
with its function engraved next to it; no visor; no fixed battery marking;
the wheel and the talk button are off until electronics stand behind them.

Rev 0.3 fits the real Dual Button unit (48 x 24 x 15 mm with keys, maker
drawing U025): the lower bay is full size, the ACK and REQUEST caps sit over
its keys, and a cable bay at the right end holds the two Grove plugs. The
shell is 6 mm wider for it.

Rev 0.4 replaces the webbing loop with a spring belt clip, as on a
hand-held radio: the unit comes off the belt at any time.

Parts:
  front_shell  - main body with payload pocket, lower bay, cable bay and plates
  back_cover   - screwed lid with the spring belt clip (or the webbing loop)
  key_step     - convex cap over StickS3 key A, right of the screen
  key_next     - pusher on the top face over StickS3 key B
  key_ack / key_request - flat and ribbed caps over the Dual Button unit
  wheel, talk_button    - only when enabled in params.Controls
"""
from build123d import (
    Align,
    Axis,
    Box,
    Cylinder,
    FontStyle,
    Location,
    Part,
    Plane,
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


def _dual_xs(p: Tnd01Params):
    """X of the ACK and REQUEST keys: keys at the left end of the unit."""
    left = p.pocket_x - p.bay[0] / 2 + p.dual.clearance
    return [left + k for k in p.dual.key_offsets]


def _board_x(p: Tnd01Params, offset: float) -> float:
    """X of a point on the board, given its distance from the left end."""
    return p.pocket_x - p.pocket[0] / 2 + p.payload.clearance + offset


def key_a_pos(p: Tnd01Params):
    return _board_x(p, p.payload.key_a_offset), p.pocket_center_y


def key_b_pos(p: Tnd01Params):
    """X and Z of key B on the top side of the board."""
    return _board_x(p, p.payload.key_b_offset), p.shell.back_t + 0.2 + p.payload.key_b_z


def _engrave(body, text, x, y, top, size, depth, align=Align.CENTER):
    label = Text(text, font_size=size, font_style=FontStyle.BOLD, align=(align, Align.CENTER))
    return body - Pos(x, y, top - depth) * extrude(label, depth + 0.1)


def bay_center_y(p: Tnd01Params):
    top = p.pocket_center_y - p.pocket[1] / 2 - p.shell.rib
    return top - p.bay[1] / 2


def key_row_y(p: Tnd01Params):
    """The Dual Button keys are on the centre line of the unit."""
    return bay_center_y(p)


def front_shell(p: Tnd01Params) -> Part:
    s, pay, pl, c = p.shell, p.payload, p.plates, p.controls
    d = p.depth
    body_h = d - s.back_t

    body = Pos(0, 0, s.back_t) * extrude(_outline(s.width, s.height, s.corner_cuts), body_h)
    front_edges = body.faces().sort_by(Axis.Z)[-1].edges()
    body = chamfer(front_edges, s.edge_chamfer)

    pw, ph, pd = p.pocket
    cy, px = p.pocket_center_y, p.pocket_x
    bw, bh = p.bay
    by = bay_center_y(p)
    # Payload pocket, lower bay and cable bay, open to the back.
    body -= Pos(px, cy, s.back_t + pd / 2) * Box(pw, ph, pd)
    body -= Pos(px, by, s.back_t + pd / 2) * Box(bw, bh, pd)
    cl, cr = p.cable_bay
    c_top, c_bot = cy + s.cable_bay_above, by - bh / 2
    body -= Pos((cl + cr) / 2, (c_top + c_bot) / 2, s.back_t + pd / 2) * Box(cr - cl + 0.02, c_top - c_bot, pd)

    # Screen window through the front wall, with a shallow bevel recess.
    win_x = px - pw / 2 + pay.clearance + pay.screen_offset + pay.screen_len / 2
    body -= Pos(win_x, cy, d - s.front_wall / 2) * Box(pay.screen_len, pay.screen_h, s.front_wall + 0.2)
    body -= Pos(win_x, cy, d - 0.4) * Box(pay.screen_len + 3, pay.screen_h + 3, 0.81)

    # USB-C plug opening in the right wall, in line with the port.
    usb_z = s.back_t + 0.2 + pay.usb_z
    body -= Pos(cr + s.right_wall / 2, cy, usb_z) * Box(s.right_wall + 2, pay.usb_plug_w, pay.usb_plug_h)

    # Upper armour plate: frames the screen window and key A.
    ax, ay = key_a_pos(p)
    up_l, up_r = -s.width / 2 + 2.5, max(win_x + pay.screen_len / 2 + 6, ax + c.key / 2 + 3)
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
    legend_y = lo_t - 3.5

    # Engraved markings. The unit name only: a fixed battery value would be
    # false (design review R4). Key functions next to their keys (R2).
    upper_top = d + pl.thickness
    unit_y = (legend_y - c.legend_size / 2 + lo_b) / 2
    body = _engrave(body, "UNIT TND-01", lo_l + 7.5, unit_y, lower_top, pl.label_size,
                    pl.engrave_depth, Align.MIN)
    for text, kx in zip(("ACK", "REQ"), _dual_xs(p)):
        body = _engrave(body, text, kx, legend_y, lower_top, c.legend_size, pl.engrave_depth)
    body = _engrave(body, "STEP", ax, ay - c.key / 2 - 2.2, upper_top, c.legend_size, pl.engrave_depth)
    bx, bz = key_b_pos(p)
    body = _engrave(body, "NEXT", bx, up_t - 1.9, upper_top, c.legend_size, pl.engrave_depth)

    # Exposed screw heads on the plates (dummy heads, M2 look).
    heads = [(up_l + 3.0, up_t - 3.0), (up_r - 1.5, up_t - 4.0),
             (lo_r - 3.5, lo_b + 4.0), (lo_l + 3.5, lo_t - 2.0)]
    for i, (hx, hy) in enumerate(heads):
        top = d + (pl.thickness if i < 2 else pl.lower_thickness)
        body -= Pos(hx, hy, top - 0.5) * Cylinder(2.0, 1.01)
        body += Pos(hx, hy, top - 0.2) * Cylinder(1.6, 1.6)
        body -= Pos(hx, hy, top + 0.4) * Box(2.4, 0.5, 0.6)

    if pl.visor:  # off since rev 0.2 (design review R3)
        visor = Box(pl.visor_len, pl.visor_reach, pl.visor_t, align=(Align.CENTER, Align.MIN, Align.MIN))
        visor = Location((win_x, up_t - 1.0, d + pl.thickness - 0.5), (90 + pl.visor_tilt_deg, 0, 0)) * visor
        body += visor

    hole = c.key_travel_hole
    # Key A: through the upper plate and the front wall onto the board.
    body -= Pos(ax, ay, d) * Box(hole, hole, 2 * (s.front_wall + pl.thickness) + 1)
    # ACK and REQUEST: through the front wall into the lower bay.
    for kx in _dual_xs(p):
        body -= Pos(kx, ky, d) * Box(hole, hole, 2 * (s.front_wall + pl.lower_thickness) + 1)
    # Key B: through the top wall onto the side of the board.
    top_y = s.height / 2 - s.top_wall / 2
    body -= Pos(bx, top_y, bz) * Box(c.pusher_w - 1.6, s.top_wall + 1, c.pusher_d - 1.6)

    if c.wheel:
        wy = bay_center_y(p)
        slot_l, slot_r = -s.width / 2 - 1, px - bw / 2 + 1
        body -= Pos((slot_l + slot_r) / 2, wy, s.back_t + pd / 2) * Box(slot_r - slot_l, c.wheel_d + 1, c.wheel_w + 1)
    if c.talk:
        body -= Pos(c.talk_x, top_y, s.back_t + pd / 2) * Box(c.talk_w - 2, s.top_wall + 1, c.talk_d - 2)

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

    if p.back_mount == "loop":
        # Webbing loop on the back: the belt runs along X through the slot.
        loop = Pos(0, 0, -lp.depth / 2) * Box(lp.width, lp.height, lp.depth)
        loop = chamfer(loop.edges().filter_by(Axis.X).group_by(Axis.Z)[0], 1.2)
        slot_z = -lp.depth + lp.bridge_t + lp.slot_t / 2
        loop -= Pos(0, 0, slot_z) * Box(lp.width + 2, lp.slot_h, lp.slot_t)
        cover += loop
    else:
        cover += belt_clip(p)
    return cover


def clip_top_y(p: Tnd01Params) -> float:
    return p.shell.height / 2 - 2.0


def belt_clip(p: Tnd01Params) -> Part:
    """Side profile in the YZ plane, extruded along X. -Z is toward the body."""
    c = p.clip
    yt = clip_top_y(p)
    yb = yt - c.length  # tip
    yf = yb + c.flare_len  # flare starts
    inner, outer = -c.gap, -c.gap - c.thickness
    pts = [
        (yt, 0.0), (yt - c.root_h, 0.0), (yt - c.root_h, inner),
        (yf + c.ridge_w, inner), (yf + c.ridge_w / 2, inner + c.ridge_h), (yf, inner),
        (yb, inner - c.flare), (yb, outer - c.flare), (yf, outer), (yt, outer),
    ]
    profile = Plane.YZ * Polygon(*pts, align=None)
    clip = extrude(profile, c.width / 2, both=True)
    # Round the long edges so the clip does not cut the belt or the shirt.
    try:
        clip = fillet(clip.edges().filter_by(Axis.X), c.edge_fillet)
    except Exception:  # noqa: BLE001 - keep sharp edges if the kernel refuses
        pass
    return clip


def _cap(c, length, top):
    """Square cap that hangs down from its top face at z = 0."""
    cap = Pos(0, 0, -length / 2) * Box(c.key, c.key, length)
    if top == "convex":
        cap = fillet(cap.faces().sort_by(Axis.Z)[-1].edges(), 1.8)
    elif top == "ribbed":
        for gy in (-2.2, 0.0, 2.2):
            cap -= Pos(0, gy, -0.3) * Box(c.key + 1, 0.8, 0.8)
    return cap


def key_caps(p: Tnd01Params):
    """STEP (convex, key A), ACK (flat), REQUEST (ribbed). Each shape can be
    told apart by touch (P3)."""
    c, s, pl = p.controls, p.shell, p.plates
    pd = p.pocket[2]
    ax, ay = key_a_pos(p)
    a_top = p.depth + pl.thickness + c.key_proud
    a_len = a_top - (s.back_t + pd - 0.1)  # down to the front of the board
    step = Pos(ax, ay, a_top) * _cap(c, a_len, "convex")

    ky = key_row_y(p)
    d_top = p.depth + pl.lower_thickness + c.key_proud
    reach = pd - p.dual.height - c.dual_gap  # cap stem below the front wall, down to the keys
    if reach < 0:
        raise ValueError(f"lower bay is {-reach:.2f} mm too shallow for the Dual Button unit")
    d_len = c.key_proud + pl.lower_thickness + s.front_wall + reach
    ack, request = (Pos(kx, ky, d_top) * _cap(c, d_len, top)
                    for kx, top in zip(_dual_xs(p), ("flat", "ribbed")))
    return step, ack, request


def key_next(p: Tnd01Params) -> Part:
    """Pusher on the top face over StickS3 key B: a chamfered bar."""
    c, s = p.controls, p.shell
    bx, bz = key_b_pos(p)
    cap = Box(c.pusher_w, c.pusher_h, c.pusher_d, align=(Align.CENTER, Align.MIN, Align.CENTER))
    cap = chamfer(cap.edges().group_by(Axis.Y)[-1], 1.0)
    reach = s.top_wall + 0.1  # down to the side of the board
    stem = Box(c.pusher_w - 2.4, reach, c.pusher_d - 2.4, align=(Align.CENTER, Align.MAX, Align.CENTER))
    return Pos(bx, s.height / 2, bz) * (cap + stem)


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
    parts = {
        "front_shell": front_shell(p),
        "back_cover": back_cover(p),
        "key_step": step,
        "key_next": key_next(p),
        "key_ack": ack,
        "key_request": request,
    }
    if p.controls.wheel:
        parts["wheel"] = wheel(p)
    if p.controls.talk:
        parts["talk_button"] = talk_button(p)
    return parts
