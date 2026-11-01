<p align="center"><img src="https://raw.githubusercontent.com/akilluminati47/RIPPS2/v1.2.8-beta/media/ripps2-test-me.png" alt="RIPPS2: Rip it, build 128"></p>

## Rip it: RIPPS2 v1.2.8 beta (builds 126 to 128)

**[Download RIPPS2.elf](https://github.com/akilluminati47/RIPPS2/releases/download/v1.2.8-beta/RIPPS2.elf)** (one file, 2,737 KB) and put it in place of your old one. Your settings stay where they were. New: **[RIPPS2-lite.elf](https://github.com/akilluminati47/RIPPS2/releases/download/v1.2.8-beta/RIPPS2-lite.elf)** (2,193 KB), the same RIPPS2 without the programs it carries for BIBLE (PS2BBL) and Neutrino. **[RIPPS2-languages.zip](https://github.com/akilluminati47/RIPPS2/releases/download/v1.2.8-beta/RIPPS2-languages.zip)** puts RIPPS2 in your language (33 of them, every new line translated). The **[theme pack](https://github.com/akilluminati47/RIPPS2-themes/releases/latest)** is edition 128.

**Two things to do once:** rip your sounds again (Audio settings > BIOS Sounds) for the right pitch, and build your ART Pack again (Settings > Game Sources > Cache > ART Pack) for the faster PS1 art.

### Sound
- **The BIOS menu sounds at the console's own pitch.** The browser plays its menu sounds against 44.1 kHz, not 48: the rips were 8.8% high. Measured against the BIOS's own playback, they now match. The menu music was already right.
- **Boot Sound: Off, On or On (fast).** On (fast) keeps the boot sound on the memory card RIPPS2 starts from, read before any drive is up, so it plays as the pillars rise. STATUS shows where it comes from, with a row to set it up. It plays with Sound Effects off too.
- A rip now refreshes Fast Boot's copy beside RIPPS2, and a deleted AUDIO folder no longer loops the load.

### Storage and the info pages
- **PS1 art from an ART Pack as fast as PS2 art**, its other names (the disc ID, XX.<name>.ELF) looked up in the pack, in memory.
- **The list page's art fades in as one** on every theme. **RIPPS2's info page turns the cover to its back** and home with the screenshots. The info pages' **rating stars are RIPFLOW's size** on every theme.
- **List Title and Description** (Settings > Interface), **PS1 Duplicates** (Ember or POPSTARTER when you have both), **conf_apps.cfg names** for POPStarterGameInstaller's numbered games, **sizes on MMCE**.
- **Starting a drive for a launch** shows an estimate and waits longer, so a Manual HDD works on the first press.

MEDIA_STORAGE

### Getting around
- **The sidebar's flow:** Circle opens the drawer of the page you are on, Left folds it to the icons, Circle again closes it. Select and Back hints while it has the pad, on every page.
- **RIPFLOW:** L2 / R2 step the covers as L1 / R1 do, Up / Down tip the case, the right stick turns it over.
- **Tooltips stay 6.9 s.** Set Metadata names the library and the file on its top line.

MEDIA_NAV

### In a game
- **CHEATS in the in-game menu** (Settings > General > In-Game Menu > Cheats), by NathanNeurotic: each of a game's cheats on or off while you play, applied on RESUME.
- **POPSTARTER's in-game reset pictures in RIPPS2's look**: [extras/POPS](https://github.com/akilluminati47/RIPPS2/tree/main/extras/POPS), copy them into POPS beside POPSTARTER.ELF.

MEDIA_GAME

### Controllers: .pad
- RIPPS2 leads **.pad**, one text file a USB pad, named by its ID ([the format](https://github.com/akilluminati47/RIPPS2/blob/main/docs/plans/pad-spec.md)), with a reference reader any launcher can use. **Settings > Controllers > My Pads** checks yours. PADEMU reads them in a later build: send us your pad's file.

### From RiptOPL
- The ShanWan PS3 copy pad, Neutrino's SMB backend, faster BDM VMC saves, Jak and Daxter defaults, the .hack IOP fix, MX4SIO writes a sector at a time.

### Fixed
- A Neutrino install on a memory card gets an icon (the browser called its folder corrupted data).

[Everything in this release](https://github.com/akilluminati47/RIPPS2/blob/main/CHANGELOG.md)
