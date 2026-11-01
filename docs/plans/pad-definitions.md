# Pad definitions: any USB pad in PADEMU from a text file

Source: the OPL help channel thread (sushi's fake DS3 2563:0575, the "external descriptors" idea).
Goal: a pad that PADEMU does not know works after the user drops one small text file on the card,
or after they make that file on the PS2 itself by pressing buttons. No SDK, no rebuild, no hex.

## What the user does (the whole point)

1. Plug the pad in. Open **Settings > Controllers > Set Up A USB Pad**.
2. RIPPS2 shows the pad's name and id ("USB Gamepad 2563:0575, not set up").
3. It asks for one button at a time on a big PS2 pad picture: "Press CROSS", "Press CIRCLE" ...
   "Push the left stick RIGHT" ... Skip with SELECT on the PS2 pad / a short wait; Back redoes the last one.
4. It shows the result live (the picture lights up as they press) and asks "Save?". Saved.
5. Optional: in a game's Pad settings, **Button Map** swaps buttons for that game only.

Nobody ever opens the file unless they want to share it. Shared files go in a database
(like the widescreen patch archive), one file per pad, named by its id.

## Files

```
mc?:/RIPPS2/PADS/2563_0575.cfg      one per pad (VID_PID), made by the helper or downloaded
mc?:/RIPPS2/PADS/GAMES/SLUS_123.45.cfg   optional per-game button map
```

Plain `key=value`, the same style as OPL's `.cfg` files, so other launchers can read it too.
Comments start with `#`. Example made by the helper:

```
# USB Gamepad (made by RIPPS2)
name=USB Gamepad
vid=2563
pid=0575
report=27            # bytes in one input report (helper fills this in)
offset=0             # first byte of button data (the DS3 driver assumes 2; this pad uses 0)
cross=b0.1           # byte 0, bit 1 is pressed
circle=b0.2
square=b0.0
triangle=b0.3
l1=b0.4
r1=b0.5
l2=b0.6
r2=b0.7
select=b1.0
start=b1.1
l3=b1.2
r3=b1.3
dpad=hat2            # byte 2 is a hat (0-7 = N,NE,E..., 8/15 = centre); or up=b.. down=b.. style
lx=a3                # byte 3, 0-255 axis, 128 centre
ly=a4
rx=a5
ry=a6
rumble=off           # off | ds3 (send the DS3 rumble packet) ; fakes often hang on it
led=off
init=off             # off | ds3 (send the 0xF4 enable packet)
```

Per-game map: `cross=circle`, `circle=cross` ... (PS2 button = PS2 button, applied after translation).

## How it reaches the game

PADEMU runs inside the game and cannot read the card then. So RIPPS2 reads the files **before**
launch and packs them into a small binary table that rides to PADEMU the way PadEmuSettings already does:

- `src/` (EE): parse every `PADS/*.cfg` (max 4 pads) + the game's map into `struct pad_def_blob`
  (fixed 4 x 40 bytes: vid, pid, report len, offset, 16 button refs {byte, bit}, hat byte,
  4 axis bytes, flags rumble/led/init) + 16-byte game remap. ~180 bytes.
- `ee_core` coreconfig: add `u8 PadDefs[180]` (watch the ee_core stack floor and the hunt list;
  it is config data, not stack). `iopmgr.c` appends it to `args_for_pademu` (8 -> 188 bytes).
- `modules/pademu` `_start`: if argv length > 8, copy the table.
  - `usb_probe`: accept a VID/PID from the table as well as the Sony ones.
  - `usb_connect`: type `GENERIC`; epCount from the interface; out endpoint optional.
  - `usb_config_set`: send F4 init / LED only if the def says so (fakes hang: the thread's "blocked
    magic packets").
  - `readReport`: `GENERIC` -> `translate_pad_generic(data, def, &pad->ds2)` in ds34common.c
    (bits to active-low DS2 buttons, hat to d-pad, axes copied, pressure = 0xFF when pressed),
    then the game remap, then `padMacroPerform` as today.
  - Rumble: only `rumble=ds3` sends; otherwise ignored.
- BT pademu: out of scope (BT pads need pairing, different path).

## The helper (EE side, in the menu)

The ELF already has USB HID access through its own pad stack? No: the menu uses padman + the
ds34usb rumble calls. The helper needs raw reports, so it loads a tiny `padlearn` mode of the same
usb_pademu.irx (argv flag) that exposes `pademu_get_raw(port, buf, 64)` through the existing
export table. The helper then:

1. Reads the idle report a few times (baseline; axes that jitter are marked noise).
2. For each prompt, waits for a report that differs from baseline: one bit flip = button,
   a byte that leaves its centre by > 64 = axis (direction gives sign), a byte that moves
   0..7/8 with the d-pad = hat. Pressure bytes (change smoothly with a button) are ignored.
3. Writes the `.cfg`. Live preview uses `translate_pad_generic` itself, so what the user sees is
   exactly what the game gets.

## Lab and hardware

PCSX2 cannot pass a random USB pad to PADEMU, so the lab covers the parser, the menu helper (fed a
recorded report file through a debug flag) and the blob reaching ee_core (EE SIO log). Real tests need
testers with fake DS3s, 8BitDo, guitar adapters: a "Test me" list with "send your .cfg" as an item.

## Open questions for the user

- File extension: `.cfg` (other apps can share it) or `.rip`? Plan says `.cfg`.
- Guitar Hero guitars that "bug OPL": a separate fix (the GH type path), not this feature.
- The DS2 that disconnects in GT4 from HDD: separate issue, not this feature.
