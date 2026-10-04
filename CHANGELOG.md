# RIPPS2 changelog

## Build 66 (alpha), changes since build 55

### Launch Disc
- **START LASER** (was START DISC). The drive is read once after boot and again when you close the tray, so moving between tabs never waits on the disc.
- **CD player:** put in an audio CD and press START LASER. A panel opens on the page, with the tabs still on top:
  - Cross plays and pauses, Square stops, Up / Down pick a track, Left / Right skip, L1 / R1 jump 10 seconds, Circle closes.
  - Triangle copies the picked track into the AUDIO folder as music, named on the keyboard.
- **The towers become a spectrum analyser** while a CD plays. Low notes stand on the left, high notes on the right, and the last second of music rolls back across the field. Hits send a ring of light back from the front; the loudest moments fire the launch beams. The right stick turns the view (slowly and steadily) and zooms.
- **DVD video** starts the player straight away (no ESR question). A disc with no DVD video on it, or one for another DVD region, says it is not compatible instead of hanging. ESR-patched games start through your own ESR.

### Sound and music
- **One AUDIO folder** beside RIPPS2.ELF holds your own sounds and music:
  - **RiptOPL's sound names:** `boot`, `cancel`, `confirm`, `cursor`, `message`, `transition`, `bd_connect`, `bd_disconnect` (.adp files).
  - **RIPPS2's new events:** `page_in`, `page_out`, `error`, `save`, `launch`, `disc`, `random`.
  - **Music:** bgm files in name order (`bgm_01 Title.ogg`, `bgm_02 Title.ogg`...).
  - Anything you leave out plays RIPPS2's own sound.
- **Settings > Audio Settings > Music** picks the track.
- **The boot sound plays as the towers rise**, plays out, and hands over to the music.
- **The music plays on every tab.** The CD player takes over only while it plays.
- New sounds for going into and out of pages, errors, saves, game launches, a disc going in and the random game pick.

### Storage
- **Settings saves no longer get stuck** behind background loading. A save goes to the front of the queue; if the background worker still does not pick it up, RIPPS2 saves it directly. The message then says what the worker was doing: send us a photo of it.
- Storage is home: the background drive checks slow down on the other tabs and pause while a CD plays or the file browser is in a drive.
- **L2 + R2** picks a random game on the info page too.
- Game art and the info page slideshow fade in instead of popping.
- Long descriptions scroll slowly so you can read them all.

### Settings
- **BOOT LOCK** (General & System, above IGR Path): with PS2BBL or PS2BBL Extended installed, the console starts straight into RIPPS2. Off puts back what PS2BBL started before. Turning it on fills an empty IGR Path with RIPPS2's path. Hold a PS2BBL hotkey at power on to reach anything else.

### Memory Files
- **EDIT** is the first action on a file and opens the text editor.
- Cleaner grid icons (the exit door and power symbol redrawn).

### Look
- The PS2 mark is thicker and drawn from the SVG. While something loads, it breathes in the corner (the swirl is gone). It flies smoothly between the tabs, with the coin flip end to end.
- **RIPPS2 Sleek:**
  - True lowercase on the keyboard and in typed text.
  - A flagged 1 (no more I/1 mix-ups).
  - Clean letter shapes: no nubs on R, no stray corners on the diagonals.
- Towers are drawn with softer, steadier edges for CRTs; the orbs' plasma tails grow out of the orb.
- Error messages put BACK where every other screen does.
- **About** shows the build number, and credits PS2BBL and the CD player.

### Known issues and asks
- If a settings save still shows "device busy", or "Settings saved ... (SAVED DIRECTLY: ...)", please send a photo: it says what the background worker was doing.
- If an audio CD says its table of contents could not be read, please send a photo: the message carries the disc's own bytes.
- The CD player's sound can only be checked on a console (PCSX2 cannot play audio CDs from images).
- BOOT LOCK needs PS2BBL already installed; writing its config can only be checked on a console.
