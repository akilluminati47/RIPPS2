# Build 139: BIBLE, set up from RIPPS2. Manage opens a BIBLE menu, carries BIBLE's update (signed by akilluminati47), and the boot sound comes in with RIPPS2's first frame.

## Get it
- **RIPPS2.elf** and **RIPPS2-languages.zip** are attached below, or from the [release page](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.3.9-beta). BIBLE rides inside RIPPS2.elf: nothing else to download, no KELFBinder needed.

## New
- **Manage's BIBLE menu** (Settings > General > Boot Loader > Manage, with BIBLE on a card): **UPDATE BIBLE** binds the new BIBLE over an older one, in place; **Background** (Auto, Sky, Black), **Splash**, **Button Glyphs**, **Info Line**, **Power-on Wait**, **Video Mode**, **Widescreen**; **EDIT BIBLE'S SETTINGS FILE** for the rest.
- **BIBLE's update** (signed by akilluminati47): the black background for anything but RIPPS2, RIPPS2 first in its defaults, and the boot sound read during its splash.
- **The boot sound from BIBLE**: Boot Sound On (fast) keeps boot.adp beside BIBLE's settings; BIBLE hands it to RIPPS2 in memory, so it plays with RIPPS2's first frame, even from an SD2PSX. STATUS says "handed over by BIBLE".
- **Older BIBLE builds** (1.3.4 to 1.3.8) are recognized: "BIBLE (MMCE build, older)".

## Tested
- **On a real PS2** (SCPH-39001, USA, SD2PSX BOOT card in slot 0): Manage said UPDATE BIBLE for the BIBLE 1.3.8 had bound, the update bound BIBLE 3282396, and at power on BIBLE's splash, then RIPPS2.
- **In the lab**: the BIBLE menu changes one line of BIBLE's settings file; RIPPS2 took the boot sound BIBLE handed over in memory, and STATUS said so.

## Test list
- **Manage with an older BIBLE on your card**: does it say UPDATE BIBLE, and does the update bind?
- **Power on after the update**: BIBLE's splash, then RIPPS2?
- **Manage after the update**: does the card say BIBLE (MMCE build) or (memory card build), not older?
- **Background: Black**: is the splash black at the next power on?
- **Background: Auto**: your RIPPS2 sky when BIBLE starts RIPPS2?
- **Splash, Button Glyphs, Info Line**: does the splash change as chosen?
- **Power-on Wait**: does a button held at power on still pick its entry?
- **Video Mode 720p or 1080i**: does BIBLE's splash come up in it?
- **Boot Sound On (fast)** (Audio settings): is boot.adp written to SYS-CONF on the BOOT card?
- **The next power on**: does the boot sound play with RIPPS2's first frame, and does STATUS say "handed over by BIBLE"?
- **Boot Sound Off**: is SYS-CONF/boot.adp gone, and is the boot faster?
- **EDIT BIBLE'S SETTINGS FILE**: does it open, and do your own notes survive a menu change?
- **A genuine memory card or a MemCard PRO 2**: does the update bind and boot?
- **A PAL or Japanese console**: does BIBLE start from its region folder?
- **Your language**: are the BIBLE menu's words translated?

## Report
Please [open an issue on GitHub](https://github.com/akilluminati47/RIPPS2/issues) with your **console model**, **your card** (genuine, SD2PSX, MemCard PRO 2), a photo of anything odd and your **DIAG.TXT** (STATUS > SAVE DIAGNOSTICS).
