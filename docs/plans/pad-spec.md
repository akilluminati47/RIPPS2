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
- Next (phase 2): the block into ee_core's config and PADEMU's arguments, `usb_probe` taking the profiles' IDs, the generic
  path in the IRX through `padTranslate`, and the setup screen (press each button, saved as a profile). Hardware testers
  with copy DS3s, 8BitDo pads and arcade sticks, each asked to send their `.pad`.
