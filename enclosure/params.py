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
    """Stage 0 board: M5Stack StickS3, lying landscape (screen at the left end)."""

    length: float = 48.0  # along X, maker spec
    width: float = 24.0  # along Y, maker spec
    depth: float = 15.0  # along Z, maker spec
    clearance: float = 0.3  # per side
    # Screen position on the board, measured from the left end of the board.
    screen_offset: float = 3.0  # [?]
    screen_len: float = 26.0  # [?] window length along X
    screen_h: float = 15.0  # [?] window height along Y
    # StickS3 keys. Key A is on the front face, right of the screen. Key B is
    # on a long side and must face up (+Y); if it faces down on the real
    # board, turn the board and use display rotation 3 in the firmware.
    key_a_offset: float = 38.0  # [?] centre of key A from the left end of the board
    key_b_offset: float = 30.0  # [?] centre of key B from the left end of the board
    key_b_z: float = 7.5  # [?] centre of key B above the back face of the board
    # USB-C port, centred on the right end of the board.
    usb_w: float = 11.0  # [?] along Y
    usb_h: float = 5.5  # [?] along Z


@dataclass(frozen=True)
class Shell:
    width: float = 62.0  # X
    height: float = 62.0  # Y
    wall: float = 2.0
    top_wall: float = 3.0  # above the payload pocket
    front_wall: float = 2.2  # in front of the payload
    back_t: float = 3.0  # back cover thickness
    # Asymmetric corner cuts: top-left, top-right, bottom-right, bottom-left.
    corner_cuts: tuple = (7.0, 3.0, 7.0, 4.0)
    edge_chamfer: float = 1.0
    # Lower bay: free space under the payload for the M5Stack Dual Button unit
    # (ACK and REQUEST keys, Grove port) in stage 0.
    bay_w: float = 44.0
    bay_h: float = 20.0
    rib: float = 2.0  # rib between the payload pocket and the lower bay
    # Back cover screws: M2 x 16 (or longer) self-tapping into the front shell.
    screw_inset: float = 4.6
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
    key_row_from_pocket: float = 8.0  # ACK / REQUEST row centre below the payload pocket
    dual_pitch: float = 14.0  # [?] distance between the 2 Dual Button keys
    dual_x: float = 0.0  # [?] centre of the Dual Button key pair
    dual_reach: float = 6.0  # [?] cap stem length inside the bay, down to the Dual Button keys
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
class BeltLoop:
    """Webbing loop on the back: the belt runs along X through the loop."""

    width: float = 42.0  # X
    height: float = 32.0  # Y, outer
    depth: float = 5.5  # Z, outer
    slot_h: float = 26.0  # Y, for 25 mm webbing
    slot_t: float = 3.5  # Z
    bridge_t: float = 1.6  # outer bridge thickness


@dataclass(frozen=True)
class Tnd01Params:
    payload: Payload = field(default_factory=Payload)
    shell: Shell = field(default_factory=Shell)
    controls: Controls = field(default_factory=Controls)
    plates: Plates = field(default_factory=Plates)
    loop: BeltLoop = field(default_factory=BeltLoop)

    @property
    def pocket(self):
        p = self.payload
        return (p.length + 2 * p.clearance, p.width + 2 * p.clearance, p.depth + 0.4)

    @property
    def depth(self):
        return self.shell.back_t + self.pocket[2] + self.shell.front_wall

    @property
    def pocket_center_y(self):
        return self.shell.height / 2 - self.shell.top_wall - self.pocket[1] / 2
