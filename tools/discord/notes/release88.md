## Kill it: RIPPS2 build 88 (alpha)

**Pause it, rip it, back it up.** Five builds since 83: your console's own sounds ripped by RIPPS2 on the console, an in-game menu, a memory card manager, RiptOPL's latest, and a launch report for the PS1 games that will not start on real hardware.

**[Download RIPPS2.elf](https://github.com/akilluminati47/RIPPS2/releases/download/v0.0.88-alpha/RIPPS2.elf)**, and the **[theme pack](https://github.com/akilluminati47/RIPPS2-themes/releases/latest)** if you like (unchanged since build 83).

### New in 88: your console's own sounds
- **Audio settings > BIOS Sounds > Rip.** RIPPS2 reads the menu sounds from the BIOS of the console it runs on and writes them into your `AUDIO` folder as its sounds: cursor, confirm, cancel, pages in and out, category, messages, disc, error, save, drive in and out, random. Each one is played the way the console plays it (its envelope, its volume, a little of the hall the browser runs under its menus). No PC, no files passed around. It asks first, because files of those names in `AUDIO` are replaced.
- Boot and game launch stay as they are (on the console those are system music, not menu sounds). Consoles from SCPH-30000 on carry the sounds this way; the first models (BIOS 1.00) are told so.
- **Music** plays the track called Menu first when you have not picked one (`bgm_03 Menu.ogg` in a pack that has it).

### New in 87: an in-game menu (turn it on to test)
- **Settings > General > In-Game Menu.** With it on, **L1+L2+R1+R2+SELECT+START** pauses the game under a plain panel instead of leaving it at once: **Resume**, **Achievements** (SpiritofRA for the game you are in: your unlocks and whether tracking is on) and **Exit Game** (your Exit To path: RIPPS2, the boot lock's loader or the browser; it takes a second press).
- For games RIPPS2 starts with its own loader. Neutrino games keep the old combo for now. PCSX2 cannot show the menu (it has no data breakpoints), so it is off until real consoles have shown it safe.

### New in 86: the CARD MANAGER
- **Square on a memory card** in Memory Files (or Triangle on a card image): every save with its size, **delete**, **back up the card to a VMC**, **write a VMC's saves to card 1 or 2**, **erase every game save** (boot loaders and system folders kept) and **format** (never the card RIPPS2 runs from). Destructive steps take two screens, the last one START only.
- Neutrino gets its automatic `-logo` first, NHDDL's order.

### New in 85: PS1 on real consoles, 704-wide modes, CD hints
- **A launch report**: just before POPSTARTER or Ember takes over, RIPPS2 writes `mc0:/RIPPS2/LAUNCH.TXT` (what it starts, its size and CRC, its arguments, the files beside it). If a PS1 game will not start on your console, open it in Memory Files and post a photo.
- POPSTARTER launches without Sony's `POPS.ELF` and `POPS_IOX.PAK` say so first, instead of a black screen.
- The 704-wide video modes draw in one pass (they could freeze the console). The CD player's hints stay on screen.

### New in 84: RiptOPL's latest
- 33 upstream commits: POPSTARTER's memory card folder only made when needed, PS1 messages that name the missing file, cheats on both cores, a VMC made on a game's first launch, Neutrino's argument preview, list labels you can turn off, MX4SIO ZSO fixes.

### Your sounds
**[The sound map](https://github.com/akilluminati47/RIPPS2#the-sound-ripps2-was-made-with)** shows every event's sound. BIOS Sounds > Rip fills the menu sounds on the console; **[RIPPS2 Audio Studio](https://github.com/akilluminati47/RIPPS2/tree/main/tools/audio-studio)** does the rest on your PC (boot, launch, music).

Full list: [CHANGELOG.md](https://github.com/akilluminati47/RIPPS2/blob/main/CHANGELOG.md). Alpha: keep your usual loader close by.
