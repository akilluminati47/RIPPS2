# RIPPS2 changelog

## Build 74 (alpha), changes since build 73

### 720p and 1080i
- **No more crashes in the HD modes.** They draw into a quarter of the memory the other modes get, and a busy RIPPS2 frame (towers, orbs, glass) could write past it. Now the towers draw simpler in HD, and a frame that still runs out drops detail instead of the console.
- **The menu no longer starves the drives and the music in HD.** Switching to 720p or 1080i left the menu running above everything else for the rest of the session (a gsKit setting that was never undone); it is put back now.

### Storage
- **Fixed a hang on the info page** (All Games and Favorites): the page could read a list that was being rebuilt in the background just as the disc and cover came in. Both lists are now swapped in whole.

### Your AUDIO folder, wherever it is
- RIPPS2 looks for `AUDIO` beside itself first, then on the memory cards, every started drive (its top or its `APPS` folder) and the HDD's OPL folder (where its ART is). Start RIPPS2 from a memory card for a quick boot and keep the music on the HDD or a USB drive: it starts as soon as that drive is up.

### BIBLE on the internal HDD
- **Works on HDDs without a `__sysconf` partition** ("could not open __sysconf" in build 73): RIPPS2 goes on `__common` instead and the config on a memory card, which PS2BBL reads first anyway.
- **RIPPS2 on a memory card stays first**: when you install from a card or USB drive, PS2BBL starts that copy (quicker than the HDD) and the HDD copy is the fallback.
- Errors now say which partition and error code.

## Build 73 (alpha), changes since build 72

### Cover Art (Settings > Network, after NBD Server)
- **Download** fetches a cover for every PS2 game in your started lists that has none, straight from the PS2 over HTTPS (xlenore's ps2-covers, the collection ORBIT's launcher uses), into that drive's own ART folder. Covers you already have are never touched.
- Each one is decoded on the PS2 and saved the way OPL's art collections are: a 140x200, 256-colour PNG of about 20 KB.
- Under the hood: BearSSL 0.6 (MIT) for TLS, and RIPPS2's network module no longer drops the end of a reply it could not carry in one piece.

### PS1 games
- **POPSTARTER is built in too.** Your own copy always comes first (the path in Settings, the drive's POPS, APPS or top folder, a game's own `XX.<name>.ELF`, the memory cards). Only when there is none does RIPPS2 write the POPSTARTER it carries to the drive's `POPS` folder (`__common/POPS` on the HDD), then start the game. It never writes over a file that is there.
- **PS1 games start from Memory Files**: a `.VCD` in a drive's `POPS` folder shows as a disc, and Cross plays it the way Storage does (USB and MMCE).

### BIBLE on the internal HDD
- **Boot Loader > Manage** now offers the **internal HDD** beside the memory cards: PS2BBL 1.2.0's HDD build goes in the HDD's boot area, RIPPS2 is copied to `__sysconf`, and the console is set to start its HDD at power on, so a fat PS2 with the network adapter boots straight into RIPPS2 with no card at all.
- The HDD's old boot program is read out first and kept (`__sysconf/RIPPS2/MBR-BACKUP.KELF`); **Restore** in the same list puts it back.
- RIPPS2's HDD driver allows exactly those writes (the boot area inside `__mbr`, and its pointer). The partition table stays fenced.

### HDD Manager
- **Removing a partition works.** It always said COULD NOT REMOVE: the HDD driver refused every delete. It now lets a user's own partition go (two screens and START, as before). System partitions (`__` names), RIPPS2's settings home and the partition RIPPS2 started from still stay, and one in use says so.

## Build 72 (alpha), changes since build 70

### PS1 games
- **Ember is built in.** RIPPS2 carries Ember (Gageformer's PS1 emulator) unmodified. The first time you start an Ember game from a drive, it writes Ember and its licence into that drive's `EMBER` folder, then starts the game. Ember games are listed even before Ember is there. Bring your own PS1 BIOS as `EMBER/bios.bin`.
- POPSTARTER still starts from your own copy, which RIPPS2 finds on your drives.
- **Ember Game Settings** save per game from Triangle, and PS1 rows explain their save-card menu (from RiptOPL).

### Memory Files
- **.elf and .ELF programs start from the internal HDD** (APA) as well as every other drive.

### Smoother
- **The music no longer stutters through big loads**: the decoder takes the CPU first whenever its reserve runs low, and frames give way instead.
- **The towers cost about half as much per frame**: far towers are drawn simpler, and every tower simpler still for a moment while the PS2 is busy.
- **One press, one sound**: with a custom AUDIO pack, a press that opens or leaves a page plays the page's sound alone.

### Colors and More (Settings > Interface)
- **Source Name**: Shown, Fade When Idle (with the category bar) or Hidden.
- **Show Recents**: 0 to 9 of your last launched games at the top of Favorites, newest first (0 turns it off).
- Every button hint reads in lowercase: the save prompt, the START menu and message boxes too.

### Neutrino (from RiptOPL)
- Every Neutrino argument can be edited from the game's settings, video modes are explained, and RIPPS2 warns before the arguments get too long to pass.

### Under the hood
- RiptOPL's latest `rebuild/main` (31 commits, to dc6206f) is merged in.

## Build 70 (alpha), changes since build 66

### Boot Lock and BIBLE
- **Settings > General & System > Boot Loader > Manage** shows what each memory card starts at power on (PS2BBL, FMCB, OSDMenu).
- **BIBLE** is El Isra's PS2BBL 1.2.0, set up by RIPPS2: no wait at power on, RIPPS2 first. It installs on the card you pick; whatever was there before is kept in a backup folder, and CIRCLE at power on still starts it.
- **Boot Lock** only edits a real PS2BBL now (it finds one beside itself and in the system-update folder), and cleans up the file build 68 wrote for FMCB cards.

### Achievements (SpiritofRA)
- **Achievements** in the START menu (where Start NBD Server was): telemetry and badges, a PC link test, and RetroAchievements for the disc in the tray. The PC side is the xeRAbora client on your network.
- **NBD Server** moved to **Settings > Network**, with the same status screen.

### Controls
- **L1 / R1** switch Launch Disc, Storage and Memory Files from any of them, the info page included.
- **Left / Right** switch drives on Storage and orb formations on Memory Files.
- **Scrolling is Fast** by default.

### RIPFLOW (Settings > Interface > Theme)
- The built-in cover carousel, renamed from Coverflow: just the covers, the source at the bottom centre, its own Roboto type, and its console frame on every tab and on the info page, with the drive's icons kept.
- **Left / Right** run the covers (hold to scroll); **Up / Down** switch sources.

### Colors and More (Settings > Interface)
- **Color Theme** for all three tabs: RIPPS2, Ember, Blood, Ectoplasm, Amethyst, Bone.
- **D-pad Glyphs** beside drive and formation names: Hidden (the new default), Shown, Fade In, Fade Out.
- **Button Hints** and **Category Bar**: Shown, Fade When Idle, Hidden.
- **Category Order**: Memory Files first and Launch Disc last (made for RIPFLOW).

### Look and feel
- Tooltips and button hints read in lowercase, and tooltips fade away after 4.2 seconds. Menus keep their capitals.
- Many shorter tooltips.
- **720p and 1080i turn Widescreen on by themselves** (4:3 modes turn it off; you can still set it by hand), and the towers and orbs keep their shape in widescreen.
- The orbs and towers are much lighter on the PS2 (the busiest formations went from 23 ms a frame to 7), for a steadier 60 fps.
- Launching keeps the towers and the loading mark moving until the game takes over.

### Memory Files
- **Orbit Settings** (START grid): cycle, speed, path lines, height, and which formations are in use, all live.
- **HDD Manager** is Square on an APA hard drive: fast now, and removing a partition takes two screens.
- Drives have real names (USB, MX4SIO, iLink, exFAT HDD), and **START DRIVES** starts them whatever Storage's start modes say.
- **The orbs, towers and CD visualiser no longer break after 72 minutes**: leave it on overnight.
- Ember started from the file browser works.

### Storage
- Saves and launches go ahead of background work, and art and game details never wait behind the music.
- The All Games list loads once, and the info page's art, logo, disc and cover come in together.
- MMCE: START copies to a memory-card home.

### Discs and PS1
- The CD player takes any CD with sound tracks (CD-Extra, mixed mode, burned CDs).
- The POPSTARTER path fills itself in from a POPSTARTER.ELF on your drives (POPS, APPS or the drive's top, or a game's own POPS/XX.name.ELF).

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
