# RIPPS2 build 126: where we stand, and the Halloween worklist

## Context

This session's last memory was build 115; the user is now on **v1.2.5-beta (build 125), released 10/30**
(ps2-pillars `main` 275f5b6, RiptOPL clone at patch 0125, nothing uncommitted for RIPPS2). Other sessions shipped
1.1.5, 1.1.7, 1.1.8, 1.2.1, 1.2.4 and 1.2.5 in between. The user's Halloween notes (10/31) plus tester ahavasi's
report on 125 are the input for build 126. This plan records the standing state from the other sessions'
memories and turns the notes into an ordered worklist.

## Where we stand (from memories / plans)

- **Released:** v1.2.5-beta (build 125: video player, .tar blue folder, HD cover download, settings cache, RIPFLOW
  five covers on 16:9, boot holds a disk theme's sky). Themes rolling release = edition 122. Media Studio released
  separately (tag `media-studio`).
- **Open PR:** NathanNeurotic **#6 "Build 126: CHEATS in the in-game menu"** (patch 0126 on b125, 203 host tests
  pass, not console-tested). User decision: **merge it first**.
- **Open threads from earlier rounds** (still not done per memories): BIBLE fork waiting on the user's signing and
  "release" word; BIBLE hand-off still shows black ~6 s; APA RIPSHOT deferred; issue #3 open until confirmed;
  MMCE RIPSHOT / SD2PSX audio only host-tested; Discord invite link expires end of October (needs a new link in
  every README); `.pad` HID profiles handoff to Ripto (docs/plans/handoff.md) is tracked, not in 126.
- **"TnA's artifact" = the USB pad definitions proposal (RIPPS2 leads it)** (claude.ai/artifact/6tzQva9..., brief in
  ps2-pillars docs/plans/handoff.md): `.pad` plain-text HID profiles, recommended Option A (the front end packs the
  profile and hands ~180 bytes to PADEMU), a Controllers page with Set Up A USB Pad / My Pads, per-game Button Map.
  Official OPL is adopting it (TnA); not in RIPPS2 yet.
- **RiptOPL moved today (10/31)** on rebuild/main: #1195 ShanWan PS3 clone pad (2563:0575) in menu and games, a port
  of freergam3r's drivers (Fgr-35/Modified-drivers-for-usb-controller-in-opl), NOT hardware-tested; #1196 Neutrino
  SMB backend; #1201 faster BDM VMC saves + Jak and Daxter defaults; #1197 704-wide HIRES modes in a 4:3 safe area;
  #1198 CDVDMAN streaming callback; #1192. RIPPS2 still pins 65d4b89 (+ earlier merges). freergam3r's caveats: no PS
  button on that pad, menu sticks were locked to stop endless scrolling (right stick only horizontal in the menu),
  tested on a 90k PAL; DS3/DS4 regression check pending with a friend's pads.
- **Promises already made to ahavasi:** hint/tooltip box 4.2 s -> **6.9 s**; a PS1 workflow (POPSTARTER vs Ember
  choice in one flow); video freeze at "opening video" to look at; IGR on Fatal Frame 3 (SLUS_212.44) title screen
  resets instead of opening the menu.
- **This session's leftovers** (harmless): `ripps2-lab/inis/PCSX2.ini.before-t115r4`, `memcards/RIPPS2-T115.ps2`,
  `memcards/RIPPS2-MP3.ps2`, `ripps2-test/t115r4/` (offer to move to the B: holding folder).

## Build 126 worklist (in order)

Patch numbering: 0126 = Ripto's cheats patch (renumber only if needed); the notes go in 0127 (one patch, several
rounds, regen with `tools/dev/regen_patch.sh`), unless the user wants them folded into 126.

### Round 0: merge PR #6
- Rebase onto main (it sits on b125's 14adac2; main has the merge db69c6b), apply patch 0126 in the RiptOPL clone,
  CI green, lab: In-Game Menu > Cheats on, a game with a .cht, toggle, RESUME. Merge the PR.

### Round 0b: RiptOPL backend fixes only (the user, 10/31: no GUI, we are our own tangent)
- No wholesale merge. Port backend commits from rebuild/main as patch 0127's first part: #1195 ShanWan PS3 clone
  pad (ds34usb + pademu), #1198 CDVDMAN streaming callback, #1201 BDM VMC saves + Jak and Daxter defaults,
  #1196 Neutrino SMB backend, #1173 .hack IOP overrun pads, #1175 BGM stop on a stream with no audio; check each
  against RIPPS2's code first (some may touch GUI files: take only the backend part).
- CI green; lab: boot, a game launch, Neutrino; the clone pad and DS3/DS4 regression go on the hardware Test me
  list. Check pad.c's analog re-ask doesn't fight the clone pad (ANALOG mode button, no PS button).

### Round 1: crashes, hangs and audio (highest risk first)
1. **Deleted AUDIO folder = load loop that blocks the pad** (SFX off doesn't help; going back to an HDD art.tar
   froze it). Start at `sound.c` sfxInit / `audioLateTick` (sound.c ~1223) and the `while (... !sfxReady[id])` wait
   (~1130); a missing set must end the load, not retry every frame.
2. **Hang at boot on the list, pad dead** after the user's settings change (sounds and art.tar missing); likely the
   same path as 1 plus the art.tar read. Reproduce in the lab with the user's settings shape.
3. **Theme change kills it** (flip case / theme background missing, then death): unload the old theme fully before
   loading the new one; keep the shared caches (list caches, art.tar, cfg.tar index) loaded across the change.
4. **Audio bugs:** menu sound plays twice; the random game sound's beep keeps ringing; save sound sometimes the
   wrong (not the quick) one; ripped BGM "wind" runs on (ask testers to delete old rips first, verify the 125
   ripper); a re-rip must add a single missing sound; boot sound plays when ON even with SFX off.
   Audit tool: list what's in the MMCE AUDIO folder and render each to WAV on the PC (BIOS sound harness in
   scratchpad style, `-DRIPPS2_BIOSSND_HOST_TEST`) so the user can hear the rips.
5. **SFX pitch higher than the BIOS's own** (boot menu, card browser, clock): find the sample-rate/pitch used when
   ripping (`ripps2biossnd.c`) vs the BIOS's playback rate and match.
6. **Neutrino / BBL injection:** "memory card showed corrupted data when ELF was injected to boot card"; check
   where the injection writes and the card's icon/FAT; for a "lite" ELF drop Neutrino and BBL injection gracefully.
7. **MMCE file browser launching broke**; **can't paste into MMCE boot cards** (look at uLE's mcpaste approach).
8. ahavasi: **video freeze at "opening video"** (an AVI SMS plays; ask for the file or test a non-Media-Studio AVI);
   **IGR on Fatal Frame 3** title screen resets (check the IGR hook vs that game's pad/IOP use).

### Round 2: art speed and fades
1. **PS1/VCD and ELF art slower than PS2 art** (VCD on MMCE, art on HDD art.tar; Celebrity Deathmatch): store the
   art key / game ID in the list caches (RIPPS2.LST / sbSnap) so a VCD's ID is never read from the file again; the
   ART Pack authority list (RIPPS2ART.LST) has "no PS1 rows" today, add PS1 and app keys.
2. **Fades must not delay loading** but keep the synced fade; make **every theme** use the sync fade for ICO/COV/BG
   (Adapt showed them separately).
3. **Size column:** MMCE and APA show sizes; "0 MB" PS1 rows are POPS ELFs (expected), see Round 4.
4. **RIPPS2 info page:** cover to back cover fade on the screenshot timing.

### Round 3: navigation and UI
1. **New sidebar flow (the user's spec, 10/31):**
   - On a main page, **Circle opens the sidebar expanded on the drawer of the page/drive you are on** (Storage on
     its current source), whether the sidebar is shown or hidden.
   - From that expanded drawer, **Left or Circle collapses the bar to the icon highlights** (the current
     category's icon lit), so nobody walks the open Storage drawer to reach the other categories.
   - **Hidden sidebar only:** at the icons, Left or Circle again closes the bar completely and the highlight goes
     back to the list where you were. A shown sidebar stays at the icons (Adapt's behaviour).
   - Code: `ripps2side.c` ripps2SidebarInput / sbFocus states (1 = icons, 2 = drawer), ripps2SidebarOpen,
     ripps2SidebarHidden, and the Circle handler in menusys.c (`ripps2SidebarOpen(ripps2SidebarHidden() ? 0 : 1)`).
2. **Select / Back glyph hints** on the sidebar and info page while highlighting.
3. **RIPFLOW:** L2/R2 keyed like L1/R1 (not end of pages) in default mode; vertical tilt in default sources mode too;
   cover flip bug after using the theme list with MMCE art.tar (flip works again on later tries: find the state).
4. **Stars on info pages too small:** match the Adapt update's size, padding right on every info page.
5. **Tooltip hold 4.2 -> 6.9 s** (`dia.c` DIA_TIP_HOLD_S).
6. **CFG title and description toggle** for all themes, off by default on RIPPS2's own theme.
7. **Set Metadata (Rename):** the top line above the fields shows the library name and the file name, both filled.
8. **Starting a drive:** an estimated time with the pillars; launching from the list with the HDD on Manual must
   work first time (keep Manual, user decision).
9. **Sky hand-off:** keep the pillars flowing into the theme (no categories/list until the theme is up), instead
   of the BIBLE sky.
10. **Fast Boot boot sound:** a third Audio setting "On (fast)" when Fast Boot's copy is in RIPPS2's AUDIO (or put it
    on the boot card beside the ELF); show it in **STATUS** too (SOUNDS section: where the fast boot sound is, with
    a row to set it up there), set up wherever it makes sense; audit the Fast Boot tooltip.

### Round 4: PS1 workflow (the promise to ahavasi)
- One PS1 flow: a filter to hide POPS ELFs when the same title has an Ember-runnable image; read art both ways
  (XX.<name>.ELF POPS name and Ember name), Ember-named wins; let the user choose POPSTARTER IGR vs Ember per game.
- POPStarterGameInstaller numbered names: read titles from `conf_apps.cfg` (already parsed in appsupport.c /
  config.c) for those entries.
- Ember: controllers forgotten when cycling (user's note): check pad state across Ember launches.
- **POPSTARTER's IGR pictures** (`IGR_BG.TM2`, `IGR_YES.TM2`, `IGR_NO.TM2` in POPS): remake them in RIPPS2's
  in-game menu look over a black background (POPSTARTER is closed, so only its pictures change). Make them with
  a PC script (TIM2 writer, same size/format as the originals, checked against the user's set), and offer them in
  the PS1 flow (copy into POPS beside POPSTARTER.ELF, keeping the originals in a holding folder).

### Round 5: Controllers / .pad (TnA's artifact), phase 1 start
- **We lead `.pad` (the user, 10/31).** RIPPS2 defines the format, the packed block and the IRX interface; we
  publish the spec (docs/plans/pad-spec.md + the reference parser) for RiptOPL / OPL / TnA to adopt, not the other
  way round. Keep the agreed OPL-thread points from docs/plans/handoff.md (generic names, VID_PID file names, INI
  sections, lookup order, composite devices) as our starting decisions.
- RIPPS2 side first: Settings > Controllers page, My Pads list (built-in Sony pads + files in `RIPPS2/PADS`), `.pad`
  INI parser and validator on the EE, per-game `PADS/GAMES/<ID>.pad` Button Map row in the Pad Emulator dialog.
- Option A hand-off to PADEMU (packed definition): we write the IRX side too (in RIPPS2's patch series, offered
  upstream to RiptOPL), starting from belek666's modularPademu split; the setup screens (detect, rest check, learn,
  test, save) drive from the PS2 pad in port 1.
- **"Packed definition" is not a problem, it's the safe path:** the EE reads the text `.pad` (easy, any drive),
  checks it, and turns it into a small fixed binary block (~180 bytes) that rides into the game the way PADEMU's
  settings already do, so the IOP never parses text or opens files mid-game (Option B's hang risk). The only
  roadbump is keeping one layout across RIPPS2, ee_core and the IRX: since we lead, we fix and version it in our
  spec (a version byte first) and others build to it.
- If the round runs long, ship 126 without it and carry it to 127.

### Round 6: release
- Strings: `python elf/lang/ripps2lang.py extract ../RiptOPL`, translate with a tools/lang126 kit (copy of
  tools/lang115 flow), 32 languages.
- CHANGELOG, README size (measure the ELF in PS2 KB), tools/discord/notes/build126.md with the tester line,
  release v1.2.6-beta (full, RIPPS2.elf), Discord only on the user's word, psx-place drafts for the user.
- Reply to ahavasi's points in the notes.

## Verification

- CI (`build-elf.yml`: build + host tests) green on every push; update tests that pin old anchors.
- Lab (ps2bg.ps1, background) per round: delete-AUDIO repro, theme switching loop, boot with missing sounds/tar,
  sidebar/RIPFLOW key flows with grabs, art timing with a VCD + art.tar disk image, DIAG.TXT lines.
- PC harnesses: BIOS sound renders for pitch and the rip audit; MP3/WAV readers as before.
- Hardware items (MMCE browser, MMCE paste, Fatal Frame 3 IGR, injection on a boot card) go to the user's
  Test me list.

## Progress (10/31 night, usage limit)
Done on b126: 0126 (PR #6 cheats), 0127 (RiptOPL backend picks, CI green), 0128 part 1 (sidebar flow, 6.9 s tooltips, boot sound without SFX, RIPFLOW L2/R2 + tilt, Set Metadata top line, deleted-AUDIO search fix in 0127; CI green). In progress, NOT CI-run or lab-checked: rating stars 143 x 18 (RIPPS2 conf_theme.cfg, RIPGRID misc cfg, Adapt generator edited in RIPPS2-themes but not regenerated or committed), a literal NUL in sound.c written as an escape. Answers: stars = rating stars at RIPFLOW size; lite ELF = a second smaller ELF without the carried Neutrino/PS2BBL. Next: lab-check the stars per theme, then Round 1 (theme-change crash, audio bugs, lab repro of the re-rip), Round 2 (art speed).

## Progress (11/01 early morning)
On b126, patch 0128 (CI per push):
- SFX pitch: the browser plays menu sounds against 44.1 kHz; rbsRender and Media Studio render_osd scale by 44100/48000
  (measured x0.916 before, x1.000 after; the menu music already matched at 0 cents). Old rips need ripping again.
- RIPGRID stars x=1; List Title and Description setting (RIPPS2 theme list_cfg_text=0); sidebar Select/Back hints on the
  info page and the Launch Disc / Memory Files pages; Boot Sound Off / On / On (fast) (card copy, STATUS row + action);
  a launch's drive start waits 75 s with an estimate bar (Manual HDD second-Cross bug); list-page art fades as one;
  info cover turns to COV2 on the shots' time (back=COV2); boot holds the pillars for a disk theme; PS1 art aliases in
  the pack + PS1 rows in RIPPS2ART.LST (rebuild the pack); MMCE size by lseek, no "0 MiB"; PS1 Duplicates setting;
  conf_apps.cfg names for numbered PS1 rows; a rip refreshes Fast Boot's copy; POPSTARTER IGR TM2s in extras/POPS.
- Lab (debug build t126d): every menu asks one sound (Z1); 7 theme switches + RIPFLOW round trip stable on HDD art.tar
  (T1/T2): the MMCE art.tar theme-change death stays a hardware item.
Still open: the hang at boot with sounds and art.tar missing (needs the user's settings), random-game beep, save sound,
Neutrino/BBL injection, MMCE browser launch and paste, video freeze, FF3 IGR, Ember controllers when cycling, RIPFLOW
right-stick flip after the tilt change (lab next), lite ELF, .pad, translations, release, reel.
