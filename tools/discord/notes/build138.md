# Build 138: BIBLE boots on a real PS2. Signed by akilluminati47, bound to an SD2PSX by RIPPS2 itself, recognized as BIBLE.

## Get it
- **RIPPS2.elf** and **RIPPS2-languages.zip** are attached below, or from the [release page](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.3.8-beta). BIBLE rides inside RIPPS2.elf: nothing else to download.
- SD2PSX owners: a **ready BIBLE BOOT card** is on [BIBLE's release page](https://github.com/akilluminati47/BIBLE/releases/latest).

## Tested on a real PS2 (SCPH-39001, USA, SD2PSX in slot 0)
- BIBLE signed by akilluminati47 (kelftool), bound to the SD2PSX BOOT card by KELFBinder, then by **RIPPS2's own Manage**: both boot BIBLE, and BIBLE starts RIPPS2 from the SD card.
- Manage shows the card as **BIBLE (MMCE build)**.
- The premade SD2PSX BOOT card boots BIBLE, then RIPPS2.

## Fixed
- **BIBLE's MMCE and MX4SIO builds** (in 1.3.4 to 1.3.6) stopped on a black screen at power on: fixed and signed again.
- **Manage's bind** boots KELFBinder's own IOPRP image now, so an SD2PSX logs in and takes the bind.
- **BIBLE is told by its own bytes**, not its icon: a KELFBinder install shows as BIBLE, with its build.

## Test list
- **Manage on a genuine memory card**: does the console bind BIBLE, and does it start RIPPS2 at power on?
- **Manage on an SD2PSX or MemCard PRO 2 BOOT card**: does the bind take?
- **Power on after the bind**: BIBLE's splash, then RIPPS2?
- **Manage after the bind**: does the card say BIBLE (and its build)?
- **The premade SD2PSX BOOT card** on your SD2PSX: BIBLE, then RIPPS2?
- **A PAL or Japanese console**: does BIBLE start from its region folder?
- **BIBLE with MX4SIO** (RIPPS2 on the MX4SIO card): does it start RIPPS2?
- **BIBLE's settings file** (SYS-CONF/PS2BBL.INI): do VIDEO_MODE, BIBLE_INFO and BIBLE_GLYPHS change the splash?
- **L2 + R2 at power on**: the launch keys page?
- **TRIANGLE + CROSS at power on**: the video mode page?
- **A refused bind**: does the message say what happened, and DIAG.TXT the steps?
- **Your language**: is Manage's BIBLE line translated?

## Report
Please [open an issue on GitHub](https://github.com/akilluminati47/RIPPS2/issues) with your **console model**, **your card** (genuine, SD2PSX, MemCard PRO 2), a photo of anything odd and your **DIAG.TXT** (STATUS > SAVE DIAGNOSTICS).
