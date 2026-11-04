# Build 141: BIBLE's Settings page and launch keys (plan, 2026-11-04)

Base: build 140 (7a15c7b, draft v1.4.0-beta pinned to 32dcc41).

The user, 11/04: "the bible manage menu should be like the update we did for the rename matching the rest of the settings
layouts, this enhances it and allows tooltips to display", and: "make the builds test and no console testing in these
releases just post what you have after 141+ to discord and the repo releases". So 140 and 141 go out after the lab, and the
notes say the new pages have not been on a real PS2.

## What it does

1. **Manage's BIBLE menu is a Settings page** (`ripps2Page` in `ripps2edit.c`): the Set Metadata (Rename) look, Roboto, a title
   with its line, label left, value right, the chosen row's tip above the hints.
2. **The cursor stays on its row.** The caller keeps it, so a change never sends it to the top.
3. **Changes are made in memory and written once when the page closes.** Left and Right never wait on the card.
4. **Safe write** (the spec's temporary file): `PS2BBL.TMP`, read back whole, then it takes the old file's name. If the power goes
   between those two steps, the next visit names the temporary file back.
5. **Sky Color** (`BIBLE_COLOR`): Follow Color Theme (key out) or any Color Theme's sky, with a swatch of the three colours.
6. **Boot Sound** in the page: the same setting as Audio, closed the same way.
7. **Launch Keys**: a page of 17 buttons, then a page per button with its name and ten paths. A path comes from the real Memory
   Files browser (`ripps2FilesPick`), typed on the keyboard, or from BIBLE's commands, with arguments per path. New lines go after
   the button's own lines.

## Facts from BIBLE's source that shaped it

- With a settings file, a button with no lines starts nothing: the built-in paths load only when no file is found.
- A file with no paths at all puts BIBLE in its rescue mode (`LoaderRunEmergencyMode`), so the last path cannot be cleared.
- ARG_ lines repeat: BIBLE hands over one argument per line, in file order.
- BOOT LOCK holds `NAME_AUTO` and `LK_AUTO_E1`, so those rows only show while it is on.
- `EJECT_TRAY` opens the tray when a disc launch finds none. `OSDHISTORY_READ` is parsed and nothing reads it, so its tip says it
  changes nothing.
- A card's BIBLE reaches `mmce?:` only in its MMCE build, `mx4sio:` only in its MX4SIO build, and neither `hdd0:` nor `ata:`. The
  row's tip says so instead of leaving it to fail at power on.

## Not in this build

- BIBLE's RAM hand-off on the user's SD2PSX path: a fix means a BIBLE re-sign.
- Nothing here has run on a real PS2.
