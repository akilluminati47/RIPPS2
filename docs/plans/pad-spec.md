# .pad: HID device profiles for PADEMU, format 1

Owner: RIPPS2 (akilluminati47). Status: format 1, frozen with RIPPS2 build 126 (2026-11-01).
Reference code: RiptOPL tree as patched by RIPPS2, `include/padfile.h` and `src/padfile.c` (AFL-3.0, plain C, no PS2
headers, no allocation). Tests: ps2-pillars `elf/tests/test_ripps2_pad.py`.

Any launcher, PADEMU build, setup app or PC tool may read and write these files. Please keep to this document so one
archive of profiles works everywhere. Changes go through a new format number; readers refuse a number they do not know.

## Files

| Path (beside the launcher's settings) | What |
|---|---|
| `PADS/VVVV_PPPP.pad` | One USB HID pad. `VVVV_PPPP` is its vendor and product ID in hex, upper case (`2563_0575.pad`). The name is the ID: the file does not repeat it. |
| `PADS/generic_gamepad.pad` | Fallback for any gamepad with no profile of its own (reserved; format 1 readers may ignore it). |
| `PADS/generic_keyboard.pad` | Fallback for keyboard-to-pad (reserved, as above). |
| `PADS/GAMES/<ELF name>.pad` | One game's button map (`SLUS_210.08.pad`). Applies to every pad, a real DualShock 2 included. |

Lookup for a connected pad: the exact `VVVV_PPPP.pad`, else a built-in decoder (the Sony pads), else the generic profile,
else "unsupported" with the pad's ID shown so the user can make a profile. A profile the reader refuses falls through to
the next step; it never blocks the pad and never reaches a game half read.

## Text format

ASCII, `key=value`, one per line, CRLF or LF. `#` starts a comment anywhere on a line. Blank lines are ignored. Keys and
values are case-insensitive. Lines are at most 159 characters. Sections in brackets group the keys for people:
`[Device]`, `[Buttons]`, `[Axes]`, `[Triggers]`, `[Mapping]`, `[Rumble]`. A reader does not depend on them: a key means the
same in any section, and a section it does not know is skipped with its keys. Unknown keys are ignored (that is how the
format grows without a new number). The last of a repeated key wins.

### Profile keys

| Key | Value | Default |
|---|---|---|
| `format` | `1` | 1 |
| `name` | Free text, for people and lists | none |
| `decoder` | `generic`, or a built-in decoder: `ds3`, `ds4`, `guitar_gh`, `guitar_rb` (pressure bytes, touchpad, frets) | generic |
| `report_id` | `none`, or a byte (decimal or `0x..`) the pad puts first in each report; it is skipped | none |
| `offset` | Bytes to skip before byte 0 of the map (0-255) | 0 |
| `cross` `circle` `square` `triangle` `l1` `r1` `l2` `r2` `select` `start` `l3` `r3` `up` `down` `left` `right` | `b<byte>.<bit>` (pressed = 1), `!b<byte>.<bit>` (pressed = 0), `a<byte>` (an axis pressed past half, for analog triggers), or `none`. Byte 0-31 after `offset`, bit 0-7 | none |
| `dpad` | `hat<byte>` (0-7 clockwise from up, anything else is the centre), `buttons` (use up/down/left/right) or `none` | none |
| `lx` `ly` `rx` `ry` | `a<byte>` (0-255, 128 centre), `a<byte>-` inverts, `none` (centred). Byte 0-126 | none |
| `deadzone` | Units round 128 that read as 128 (0-127) | 0 |
| `rumble` | `off`, `ds3`, `ds4` (the packet the pad understands) | off |
| `led` | `off`, `ds3`, `ds4` | off |
| `init` | `off`, `ds3` (send the DualShock 3 enable packet) | off |

A generic profile must map at least one button. `dpad=hat..` and up/down/left/right together is refused.

Example (a copy DualShock 3 that reports its buttons from byte 0):

```
# USB Gamepad (made by RIPPS2)
[Device]
format=1
name=USB Gamepad
decoder=generic
[Buttons]
square=b0.0
cross=b0.1
circle=b0.2
triangle=b0.3
l1=b0.4
r1=b0.5
l2=b0.6
r2=b0.7
select=b1.0
start=b1.1
l3=b1.2
r3=b1.3
[Axes]
dpad=hat2
lx=a3
ly=a4
rx=a5
ry=a6
deadzone=12
[Rumble]
rumble=off
led=off
init=off
```

### Game map keys

`<button>=<button>` with the button names above: the left side is what the pad pressed, the right side is what the game
gets. `<button>=none` makes the press reach nothing. Buttons not listed are themselves. `format=1` as above.

## The packed block (what PADEMU gets)

The launcher reads the text and checks it, then hands PADEMU one block of exactly **180 bytes**, the way PADEMU's
settings already reach it. PADEMU never parses text or opens a file while a game runs. All multi-byte fields are little
endian. The second byte after the magic is the format number: a reader refuses a block whose number it does not know.

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | `'P' 'D'` |
| 2 | 1 | Format (1) |
| 3 | 1 | Profiles in the block (0-4) |
| 4 | 4 x 40 | Profiles (below), unused ones zero |
| 164 | 16 | Game map: for DS2 button n, the button the game gets (0xFF itself, 0xFE nothing) |

One profile, 40 bytes:

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | VID |
| 2 | 2 | PID |
| 4 | 1 | Decoder: 0 generic, 1 ds3, 2 ds4, 3 guitar_gh, 4 guitar_rb |
| 5 | 1 | Report ID (used when flag 0x20 is set) |
| 6 | 1 | Offset |
| 7 | 1 | Flags: 0x01 rumble ds3, 0x02 rumble ds4, 0x04 led ds3, 0x08 led ds4, 0x10 init ds3, 0x20 report ID |
| 8 | 1 | Deadzone |
| 9 | 1 | D-pad hat byte, 0xFF none |
| 10 | 4 | LX, LY, RX, RY: the byte, 0x80 set = inverted, 0xFF none |
| 14 | 16 | Buttons in DS2 bit order (below): bits 0-4 the byte, bits 5-7 the bit; for an axis button the axis byte; 0xFF none |
| 30 | 2 | Mapped: bit n set when button n has a reference |
| 32 | 2 | Active low: bit n set when button n is pressed at 0 |
| 34 | 2 | From axis: bit n set when button n is an axis pressed at 0x80 or more |
| 36 | 4 | Zero (room for format 2) |

DS2 bit order (bit n of the button word the game reads, active low): 0 select, 1 l3, 2 r3, 3 start, 4 up, 5 right, 6 down,
7 left, 8 l2, 9 r2, 10 l1, 11 r1, 12 triangle, 13 circle, 14 cross, 15 square.

## Decoding a report (generic)

`padTranslate()` in the reference code is the definition: skip the report ID when the flag is set and the report starts
with it, then `offset`; each mapped button reads its bit (inverted when active low) or its axis (pressed at 0x80 or more);
the hat sets the d-pad (0 up, 1 up+right, 2 right, 3 down+right, 4 down, 5 down+left, 6 left, 7 up+left); axes read their
byte, invert if asked, and snap to 128 inside the deadzone; a byte past the report's end reads as released / centred.
Then the game map, then PADEMU's macros as today. Pressure bytes for a generic pad are 0xFF when pressed, 0 when not.

## Where RIPPS2 is with it

- Build 126: this format, the reference reader, packer and decoder, the host tests, and Settings > Controllers > My Pads,
  which lists the profiles on the card and says what is wrong with any it refuses.
- Build 129 (phase 2):
  - The launcher reads `PADS` and `PADS/GAMES/<game ID>.pad` as a game starts (`src/ripps2pads.c`), packs the block, and
    places it after PADEMU's eight bytes of settings below 0xD0000. ee_core passes 8 + 180 bytes and sets bit 19 of
    PadEmuSettings (`PADEMU_PROFILES_FLAG`) so PADEMU knows the block follows. No block (no profile, no map): PADEMU starts
    exactly as before.
  - PADEMU (`modules/pademu/padprofile.c`, `padfile.c` built with `PADFILE_DECODE_ONLY`) takes a non-Sony pad whose
    VID:PID a profile names as `GENERIC`: `init=ds3` sends the F4 packet, `rumble=ds3`/`led=ds3` send the DS3 output report,
    and nothing else is ever sent. The game map (`padApplyMap`) applies to every USB pad, Sony ones included.
  - The menu's USB driver (`modules/ds34usb`) reads the same block (RPC 10, `DS34USB_SET_PROFILES`), so a profiled pad
    steers the menu too, and hands Set Up A USB Pad a HID pad's raw reports (RPC 9, `DS34USB_GET_RAW`: 8 bytes of state
    and ID, then the report). While that screen is open it takes any HID pad that is not a boot keyboard or mouse.
  - Settings > Controllers > Set Up A USB Pad: plug the pad in, let go (a second and a half at rest measures the bytes
    that move on their own), press each button and push each stick as asked (SELECT on the PS2 pad skips one), try the
    result live, save. It finds a bit (`b`/`!b`), a hat (`dpad=hat<byte>`), an analog trigger (`a<byte>`) or a stick
    (`a<byte>`, `-` when it runs the other way), writes `PADS/VVVV_PPPP.pad` (an older file is kept as `.bak`, `.b01`...)
    and reads it back with the reference reader before anything is saved.
- Next: hardware testers with copy DS3s, 8BitDo pads and arcade sticks, each asked to send their `.pad`; a `report_id`
  pass for pads that send more than one report.
