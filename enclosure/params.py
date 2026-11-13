"""Parameters of the TND-01 belt module enclosure (concept B, stage 0).

All values are millimetres. Values marked "[?]" are placeholders until the
real board is measured with calipers; change them here, not in the model.

Coordinate system (as worn on the belt):
  X - width, left to right as the wearer looks down at the screen
  Y - height, up is toward the wearer's face
  Z - depth, +Z points away from the body (front face), Z = 0 is the back face
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Payload:
    """Stage 0 board: M5Stack StickS3, lying landscape (screen at the left end).

    Values marked "drawing" are read from the maker's model size drawing
    (K150-sticks3.pdf). Check them with calipers before the print.
    """

    length: float = 48.0  # along X, maker spec
    width: float = 24.0  # along Y, maker spec
    depth: float = 15.0  # along Z, maker spec
    clearance: float = 0.3  # per side
    # Screen bezel position on the board, measured from the left end.
    screen_offset: float = 3.8  # drawing
    screen_len: float = 26.3  # drawing, along X
    screen_h: float = 16.4  # drawing, along Y
    # StickS3 keys. Key A is on the front face, right of the screen. Key B is
    # on a long side and must face up (+Y); if it faces down on the real
    # board, turn the board and use display rotation 3 in the firmware.
    key_a_offset: float = 37.5  # drawing: centre of key A from the left end of the board
    key_b_offset: float = 24.0  # drawing: centre of key B from the left end of the board
    key_b_z: float = 7.5  # [?] centre of key B above the back face of the board
    # The right end of the board has the USB-C port (front) and the Grove
    # port (back), both centred along Y. Heights are above the back face.
    usb_z: float = 10.2  # drawing
    grove_z: float = 5.3  # drawing
    # Opening in the right wall for a USB-C plug body, not only the port.
    usb_plug_w: float = 12.5  # [?] along Y
    usb_plug_h: float = 7.0  # [?] along Z


@dataclass(frozen=True)
class DualButton:
    """M5Stack Unit Dual Button (U025), lying landscape in the lower bay,
    keys up (toward the front), keys at the left end, Grove port at the
    right end. Values from the maker's model size drawing (U025)."""

    length: float = 48.0  # along X
    width: float = 24.0  # along Y
    height: float = 15.0  # along Z, back face to the top of the key caps
    clearance: float = 0.3  # per side
    key_offsets: tuple = (11.0, 25.0)  # key centres from the left end, on the centre line
    key_d: float = 11.5  # key cap diameter


@dataclass(frozen=True)
class Shell:
    width: float = 68.0  # X; rev 0.3: 62 left no room for the top-left screw beside the moved pocket
    height: float = 62.0  # Y
    wall: float = 2.0
    left_wall: float = 7.6  # left of the payload pocket: room for the left screws
    right_wall: float = 2.4  # right of the cable bay
    top_wall: float = 3.0  # above the payload pocket
    front_wall: float = 2.2  # in front of the payload
    back_t: float = 3.0  # back cover thickness
    # Asymmetric corner cuts: top-left, top-right, bottom-right, bottom-left.
    corner_cuts: tuple = (7.0, 3.0, 7.0, 4.0)
    edge_chamfer: float = 1.0
    # The lower bay holds the Dual Button unit; its size comes from
    # DualButton. The cable bay at the right end holds both Grove plugs and
    # the short cable between them. The payload pocket moves left to make
    # room for it.
    rib: float = 2.0  # rib between the payload pocket and the lower bay
    cable_bay_min: float = 8.0  # [?] Grove plug length plus cable bend
    cable_bay_above: float = 6.0  # cable bay top above the pocket centre line
    # Back cover screws: M2 x 16 (or longer) self-tapping into the front shell.
    screw_inset: float = 5.6  # rev 0.3: 4.6 cut the screw heads open on the 7 mm corner cuts
    screw_clear_d: float = 2.4
    screw_pilot_d: float = 1.7
    screw_head_d: float = 4.0
    screw_head_depth: float = 1.4


@dataclass(frozen=True)
class Controls:
    """One part for each firmware key: STEP (key A), NEXT (key B),
    ACK and REQUEST (Dual Button unit). Design review rev 0.1, R1."""

    key: float = 8.0  # square key cap
    key_travel_hole: float = 8.4
    key_proud: float = 2.0  # how far the cap stands above the front plate
    dual_gap: float = 0.2  # free gap between the ACK / REQUEST caps and the Dual Button keys
    pusher_w: float = 9.0  # NEXT pusher on the top face, over StickS3 key B
    pusher_d: float = 6.0
    pusher_h: float = 3.0
    legend_size: float = 2.6  # engraved key function names
    # Placeholders from rev 0.1, off until they have electronics behind them
    # (design review R1, R5). The wheel waits for the desk test; the talk
    # button waits for the voice unit (stage 1).
    wheel: bool = False
    talk: bool = False
    wheel_d: float = 14.0
    wheel_w: float = 6.0
    wheel_proud: float = 3.0  # how far the wheel sticks out of the left side
    talk_w: float = 12.0
    talk_d: float = 7.0
    talk_h: float = 3.5
    talk_x: float = 16.0  # talk button position on the top face


@dataclass(frozen=True)
class Plates:
    thickness: float = 1.2  # raised armour plates on the front
    lower_thickness: float = 1.5
    # The visor hid the top screen line from a server who looks down at the
    # belt (design review R3). Off; kept for comparison renders.
    visor: bool = False
    visor_len: float = 34.0
    visor_reach: float = 7.0
    visor_t: float = 1.6
    visor_tilt_deg: float = 25.0
    engrave_depth: float = 0.4
    label_size: float = 4.2


@dataclass(frozen=True)
class BeltClip:
    """Spring clip on the back cover, as on a hand-held radio. The tongue
    hangs down from a root block at the top; the belt goes between the
    tongue and the cover from below. To take the unit off the belt, pull
    the flared tip out with a finger and lift.

    Print the back cover in nylon (PA12, MJF or SLS): standard SLA resin
    breaks at about 2 % strain. build.py checks the strain at full opening.
    """

    width: float = 30.0  # X
    length: float = 46.0  # Y, from the top of the root block to the tip
    thickness: float = 2.6  # tongue
    root_h: float = 8.0  # Y, root block that joins the tongue to the cover
    gap: float = 2.0  # tongue to cover with no belt; a 4 mm belt preloads it
    ridge_h: float = 1.0  # catch on the inner face near the tip, holds the belt bottom edge
    ridge_w: float = 2.5
    flare: float = 3.0  # tip bends away from the cover: lead-in and finger grip
    flare_len: float = 7.0
    belt_max: float = 4.5  # [?] thickest belt the clip must take
    max_strain: float = 0.02  # limit for the check in build.py
    edge_fillet: float = 0.8


@dataclass(frozen=True)
class BeltLoop:
    """Webbing loop on the back (rev 0.3): the belt runs along X through it.
    Off since the belt clip; kept for comparison."""

    width: float = 42.0  # X
    height: float = 32.0  # Y, outer
    depth: float = 5.5  # Z, outer
    slot_h: float = 26.0  # Y, for 25 mm webbing
    slot_t: float = 3.5  # Z
    bridge_t: float = 1.6  # outer bridge thickness


@dataclass(frozen=True)
class Tnd01Params:
    payload: Payload = field(default_factory=Payload)
    dual: DualButton = field(default_factory=DualButton)
    shell: Shell = field(default_factory=Shell)
    controls: Controls = field(default_factory=Controls)
    plates: Plates = field(default_factory=Plates)
    loop: BeltLoop = field(default_factory=BeltLoop)
    clip: BeltClip = field(default_factory=BeltClip)
    back_mount: str = "clip"  # "clip" (take off at any time) or "loop" (webbing loop)

    @property
    def pocket(self):
        p = self.payload
        return (p.length + 2 * p.clearance, p.width + 2 * p.clearance, p.depth + 0.4)

    @property
    def bay(self):
        d = self.dual
        return (d.length + 2 * d.clearance, d.width + 2 * d.clearance)

    @property
    def pocket_x(self):
        """The pocket and the lower bay sit near the left wall."""
        return -self.shell.width / 2 + self.shell.left_wall + self.pocket[0] / 2

    @property
    def cable_bay(self):
        """X range of the cable bay, right of the pocket and the lower bay."""
        left = self.pocket_x + max(self.pocket[0], self.bay[0]) / 2
        return left, self.shell.width / 2 - self.shell.right_wall

    @property
    def depth(self):
        return self.shell.back_t + self.pocket[2] + self.shell.front_wall

    @property
    def pocket_center_y(self):
        return self.shell.height / 2 - self.shell.top_wall - self.pocket[1] / 2
