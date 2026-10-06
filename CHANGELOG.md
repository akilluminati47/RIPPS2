# RIPPS2 changelog

## Build 86 (testing), changes since build 85

### Memory Files: the CARD MANAGER
- **Square on a memory card** in the drive list opens the CARD MANAGER (as Square on the internal HDD opens the HDD MANAGER); a card image (VMC) has it in its Triangle actions. Every save with what it takes, the space left, and the card tools:
  - **Delete** a save.
  - **Back up the card to a VMC** on a drive (`VMC/CARD1-01.bin` and on): a blank 8 MB card image with every folder on the card copied in, the way Memory Files copies saves. The card stays as it is.
  - **Write a card image's saves to memory card 1 or 2.** A save already on the card is left as it is.
  - **Erase every game save**, keeping the folders that are not saves: boot loaders (BOOT, PS2BBL, FMCB, OSDMENU), SYS-CONF, APPS, RIPPS2, POPSTARTER and the folder RIPPS2 was started from.
  - **Format the card** (never the card RIPPS2 was started from).
- Delete, erase and format each take two screens, and the last one only START gets past.

### Neutrino
- The automatic `-logo` is sent first, right after `neutrino.elf`, NHDDL's order (for FifthFox's iLink test; Neutrino reads every option before it acts, so it is not a fix in itself).

## Build 85 (testing), changes since build 84

### PS1 games on a real console
- **A launch report.** Just before POPSTARTER or Ember takes over, RIPPS2 writes what it is about to do to `mc0:/RIPPS2/LAUNCH.TXT`: the file it is starting (its size and CRC, which tell which version it is), its arguments, Sony's POPS files or Ember's BIOS beside it, both cards' POPSTARTER folders, and the settings that steer it. A PS1 game that will not start says nothing on screen, and PCSX2 starts them fine, so this file is how a tester can show us what the console saw: open it in Memory Files, or post a photo.
- **POPS files, asked about first.** On USB, iLink, MX4SIO, exFAT HDD and MMCE, a POPSTARTER launch without POPS.ELF and POPS_IOX.PAK (the PS1 emulator from your own console) in the game's POPS folder now says so before anything is written, instead of going to a black screen. START launches anyway.

### Video modes
- **The 704-wide modes draw in one pass**, 16-bit like the HD modes. They were the last on gsKit's two-pass hires renderer, the one RIPPS2's towers overran in HD: confirming one, or letting the prompt time out, could freeze the console. The list no longer says HIRES.

### Launch Disc
- The CD player's button hints stay inside the TV-safe area; CLOSE no longer sits at the screen's edge (and a tight row says COPY for COPY TO AUDIO).

## Build 84 (testing), changes since build 83

### From RiptOPL
- **RiptOPL's latest** (33 commits, to e74ddce) is merged in. For PS1 games: the memory card's POPSTARTER folder is only made when there are modules to put in it, and never by just looking (an empty one was being made on every PS1 launch); PS1 "missing" messages name the file they looked for. Also: cheats on both cores, a VMC created on a game's first launch, Neutrino's argument preview, PS1/PS2 list labels you can turn off (Interface), and fixes for MX4SIO ZSO games.

## Build 83 (testing), changes since build 82

### Star your games
- **Favorite is now Star.** R3's hint says Star, and the list it fills is **Starred Games**: the source, its Pop In toast, L3's caption and the Settings rows. Only the words change; your starred games and settings carry over.

### YOUR ACCOUNT
- **Laid out like a RetroAchievements profile.** Unlocked, games and mastered across the top with one bar for everything; each game's count beside its name in the list; the chosen game's card with its unlocked / total, a bar, and Mastered, % complete or Not started. Long titles scroll and messages wrap, so nothing is cut off.
- Fixed: the card showed leftover text after a short title (KATAMARI DAMACY NTS 5 GAMES...), and the big total drew as a broken block.

### Any theme, any font
- **List titles sit in the middle of the highlight bar**, whatever font a theme uses: RIPPS2 measures the font's own centerline instead of a nudge tuned to its own face. Adapt's bar no longer rides above its titles, and your own themes need no adjusting.

### RIPgrid (theme pack)
- The covers sit a little lower and smaller, so the chosen one clears the category bar and the PS2 mark and the rest never touch it; the hints (list and info page), tooltips and YOUR ACCOUNT use RIPPS2 Sleek's lowercase face.

## Build 82 (testing), changes since build 81

### HD text fixed
- **720p and 1080i text is the right size again.** Since build 75 drew those modes 640 wide for the GS to stretch, the fonts took the pixel shape upside down: text came out four times too wide at 720p (two and a quarter at 1080i) and spilled over every panel. Now it matches 480p, as it should.

### RIPgrid
- **Turn the case over.** Hold the right stick to one side for 2 seconds and the chosen case flips to its back cover, the way you lean. It stays turned on the grid when you move on and when you come back; hold again to turn it home. The back cover is asked for as soon as the front is in, and the flip waits for it.
- **Pages slide.** The grid moves by whole pages now, and a new page slides in as the old one slides away, eased like RIPFLOW's carousel (off when Coverflow's animation speed is 0).
- Themes: a Grid's new `back_pattern` key picks what a turned case shows (`COV2`, the back cover, unless a theme says otherwise; `SCR` puts a screenshot there; `0` turns the flip off). The back covers get a cache of their own, a page and two deep.

### Theme pack
- **RIPPS2-themes for build 82**: everything since the build 80 pack in one download. Adapt's case shows the front, then the back; its info page sits opposite the list; Adapt Rx keeps its side bar on the left, and both keep the disc under LAUNCH DISC; RIPgrid is set in RIPPS2 Sleek with the Grunge theme's button glyphs; every image is an 8-bit PNG.

### US spellings
- What the menus say is in US English: canceled (the CD copy too), color, license, behavior, center.

## Build 81 (testing), changes since build 80

### Game list
- **Source Name: Pop In is now a toast.** The source's name is no longer drawn over the list: it plays in the middle of the page the way L3 names the list, in the same big letters, the whole name in capitals (ALL GAMES, HDD GAMES, BDM GAMES; the GAMES tells it apart from L3's ALL). It comes on the first list after boot, whenever the source changes and when you come back to Storage from another tab, then holds and fades. Closing an info page or Settings does not repeat it. Themes with `source_name=pop` (Adapt, Adapt Rx, RIPgrid) get it too, so their static source line is gone.
- Long names (UDPFSBD GAMES) close their letters up to stay on screen.
- **One big face for the view word, on every theme**: L3's ALL / PS1 / PS2 and the Pop In toast both draw in RIPPS2 Sleek Bold at 64 px (they used to take a theme's `font14`), RIPFLOW included, so they look and move the same everywhere. A theme without a `font14` of its own also gets that face for the Achievements page's big numbers, instead of its small text font.

### Themes set the look, you keep the last word
- **A theme can now choose Colors and More for itself** in its `conf_theme.cfg`: `color_theme` (RIPPS2, Ember, Blood, Ectoplasm, Amethyst, Bone), `category_bar` and `button_hints` (shown, fade, hidden), `dpad_glyphs` (hidden, shown, fade_in, fade_out), `category_order` (launch_disc_first, memory_files_first), and `source_name` (shown, fade, hidden as well as pop). No rebuild of the ELF: any theme folder can do it.
- **Your settings always win.** RIPPS2 now remembers which Colors and More rows you have changed. A theme's choice shows only on a row you have never touched that is still at its default, so anything you pick, the default included, stays yours on every theme. Colors and More shows what is in effect.
- **RIPFLOW puts Memory Files first** on the category bar, unless you have picked an order.

## Build 80 (testing), changes since build 79

### STATUS
- **A new STATUS page** on the START menu, where Achievements was: the homebrew RIPPS2 carries (Neutrino 1.8.0, POPSTARTER, Ember Beta-2, BIBLE), each under its own name, with where it is installed now, a way to install RIPPS2's copy, and its settings from around the menus (Neutrino's, PS1 Settings, POPSTARTER's network files, MANAGE for the boot loader).

### Achievements
- **Achievements moved to Settings**, the last page after Audio Settings.
- **YOUR ACCOUNT**, its last row: every game you have checked, from every drive, with what your RetroAchievements account has unlocked (a bar per game, your totals, mastered games), as xeRAbora reported it at each game's last CHECK GAME SUPPORT. Opens with START, closes with BACK or START, and lets go of its list when it closes. Counts are kept from this build's checks on; xeRAbora versions that do not send the unlocked count show the total only.
- **Badges** stay on by default: they cost nothing until TELEMETRY is on and xeRAbora answers on your PC (then a quick file check per game when a list refreshes, in the background). The page says so.

### Settings
- **Network**: RIPPS2's rows (NBD server, Cover Art) under their own RIPPS2 header; the RA switches left for the Achievements page; a clear row before OK.
- **Colors and More**: Source Name sits under the D-pad glyphs; the Color Theme heads the colour pickers.

### Game list
- **Source Name: Pop In**: the source's name rises in letter by letter, the way L3's view word does, when the page opens or the source changes. Themes can make it their default (`source_name=pop`).
- **Coverflow and Grid themes: Circle cycles the sources** (Cross, with Circle to select), since every arrow browses games there; the hint row says Source. Inside a folder it climbs out first; on the info page it is still Back.
- **Grid**: with tilt on, only the chosen cover tips with the right stick.

## Build 79 (testing), changes since build 78

For the reworked Adapt, Adapt Rx, RIPgrid and RIPgrid Rx themes (RIPPS2-themes kit).

### Switch themes with SELECT
- **Hold SELECT for 4.2 seconds** on the game list and RIPPS2 steps to the next theme, once per hold, and remembers it. A shorter press still refreshes the list, when you let go; a hold that switched the theme does not refresh.
- The Theme setting's tip says so.

### Grid
- **No stock disc or case**: each cover eases in as its art arrives. A game with no cover shows as a clear glass tile with its name.
- **The selection breathes**: a soft glow in the theme's selection colour swells and eases under a crisp frame.

### Glass and art
- **Clear glass**: a theme can give a panel one even tint (`tint`, `tint_color`) and drop its frame (`frame=0`), for a full-screen frosted layer or a side bar.
- The frost **eases in with the art** under it instead of appearing at once.
- **`widecrop`**: on a 16:9 picture, a theme's background art shows its middle three quarters (a zoom) instead of stretching; frosted glass over it follows.
- Page morphs use the first framed glass panel, so frameless layers don't count.

## Build 78 (testing), changes since build 77

For the new themes: Adapt, Adapt Rx, RIPgrid and RIPgrid Rx (in the RIPPS2-themes kit).

### Theme engine
- **Grid** element: the game list as a page of covers in rows (columns, rows and spacing set by the theme). Left / Right step one cover, Up / Down one row, and past the top or bottom row a new press switches drive.
- **Frosted glass**: `blur=1` on a glass panel softens the game's own background art behind it, made again as you move between games.
- **`towers=0`**: a theme can keep the pillars off the game pages (its own colour shows where there is no art); Settings still show the pillars behind glass.

## Build 77 (alpha), changes since build 76

### Neutrino is built in
- **RIPPS2 carries Neutrino 1.8.0** (rickgaiser's PS2 device emulator, AFL-3.0), unmodified. When a game starts through Neutrino and there is no Neutrino where RIPPS2 looks, it asks: install it **on the game's drive** or **on memory card 1 or 2**, your pick. Then the game starts.
- Your own Neutrino always comes first (the path in Settings, the game's drive, the memory cards). Network game sources offer the memory cards.
- The copy is checked: an install cut short is never taken for a complete one.

## Build 76 (alpha), changes since build 75

### Guard rails (nothing on screen changes)
- **Every build now runs RiptOPL's 34 host checks** on RIPPS2's patched tree, plus RIPPS2's own: HD modes stay single-pass, every drawn shape checks the draw queue, All Games and Favorites never free a list under a reader, the AUDIO search order, BIBLE's HDD fallback and the quiet-boot marker. Where RIPPS2 differs from RiptOPL on purpose, `elf/tests/expected_failures.txt` says why; anything else that breaks fails the build.
- **A new compiler warning in a RIPPS2 file fails the build.**

## Build 75 (alpha), changes since build 74

### 720p and 1080i, drawn in one pass
- **HD is drawn the way 480p is**: one full frame, every animation at full detail, 60 fps. It used to be drawn three times over in bands from a small buffer (gsKit's "hires" mode), which is what crashed. Now RIPPS2 draws a 640-wide frame and the PS2's own video output stretches it to 1280 or 1920 wide, with all 720 lines kept (1080i: 540 per field, as before).
- Nothing is simplified for HD, and the towers stay alive behind every prompt.

### Booting from the HDD
- **The boot sound starts right away**, before the HDD's drivers come up to read your settings. If you turned the boot sound off, RIPPS2 leaves a small `RIPPS2/QUIETBOOT` marker on memory card 1 so it stays quiet then too.

### Neutrino (from RiptOPL)
- **Show Launch Arguments** (Settings > Game Launching > Neutrino Defaults): see every argument Neutrino will get before a launch, and go back if it looks wrong.

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
