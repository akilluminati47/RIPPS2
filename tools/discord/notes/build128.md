# Builds 126 to 128: the BIOS sounds at the console's own pitch, PS1 art as fast as PS2's, the new sidebar flow, CHEATS in the in-game menu and a lite ELF.

## Get it
- [Download the latest RIPPS2.elf](https://github.com/akilluminati47/RIPPS2/releases/latest/download/RIPPS2.elf) (or the smaller [RIPPS2-lite.elf](https://github.com/akilluminati47/RIPPS2/releases/latest/download/RIPPS2-lite.elf), without PS2BBL and Neutrino), [RIPPS2-languages.zip](https://github.com/akilluminati47/RIPPS2/releases/latest/download/RIPPS2-languages.zip) and the [theme pack](https://github.com/akilluminati47/RIPPS2-themes/releases/latest/download/RIPPS2-themes.zip), edition 128
- **Rip your sounds again** (Audio settings > BIOS Sounds) for the right pitch, and **build your ART Pack again** for the faster PS1 art.

## New
- **The BIOS sounds at the console's own pitch**: the rips were 8.8% high. The menu music was already right.
- **Boot Sound: Off, On, On (fast)**: On (fast) keeps the boot sound on the memory card RIPPS2 starts from, so it plays with the pillars. STATUS says where it comes from.
- **PS1 art from an ART Pack as fast as PS2 art**, its other names looked up in the pack.
- **The list page's art fades in as one** on every theme; RIPPS2's info page turns the cover to its back with the screenshots.
- **The sidebar**: Circle opens it on the page you are on, Left or Circle folds it to the icons, Circle again closes it. Select and Back hints while it has the pad.
- **RIPFLOW**: L2 / R2 step the covers, Up / Down tip the case.
- **CHEATS in the in-game menu** (Ripto's): turn a game's cheats on and off while you play.
- **Stars on the info pages** at RIPFLOW's size; **tooltips stay 6.9 s**; **sizes on MMCE**.
- **List Title and Description**, **PS1 Duplicates** (Ember or POPSTARTER when you have both), and **conf_apps.cfg names** for POPStarterGameInstaller's numbered games.
- **Starting a drive for a launch** shows an estimate and waits longer, so a Manual HDD works on the first Cross.
- **.pad**: RIPPS2's format for any USB pad, one text file each; Settings > Controllers > My Pads checks yours.
- **POPSTARTER's in-game reset pictures** in RIPPS2's look (extras/POPS in the repo).
- **A Neutrino install on a memory card** gets an icon (no more "corrupted data").

## Test list
- **Rip the sounds again**: do cursor, confirm and back now match the browser's pitch?
- **Boot Sound On (fast)** with RIPPS2 on a memory card: does the boot sound start with the pillars?
- **Enter a menu** (START, Triangle, Square): one sound each time, or still two? Which menu?
- **Random game (L2 + R2)** many times: does any beep keep ringing?
- **Save a game's settings**: the quick save sound, every time?
- **Delete one sound** from AUDIO and rip again: is it back after a reboot (Fast Boot on and off)?
- **PS1 art** from an ART Pack built with this build: as quick as PS2 art? VCD on MMCE with art on the HDD too?
- **Change themes** a few times from the theme list with art.tar on MMCE: does every page and the cover flip still work?
- **RIPFLOW**: hold the right stick: does the case turn to its back? L2 / R2 and Up / Down?
- **The sidebar** on Adapt and RIPPS2: Circle, Left, Circle: does it go where you expect, shown and hidden?
- **HDD on Manual**: launch a game from All Games or the HDD page: does it start on the first Cross? Is the estimate close?
- **CHEATS in the in-game menu** on a game with a .cht: turn one off and on, RESUME: does it hold?
- **MMCE**: are the sizes there on the info page?
- **The MMCE file browser**: does launching an ELF from it work? Can you paste into an MMCE boot card?
- **IGR in Fatal Frame 3 (SLUS_212.44)** at the title screen: menu or reset?
- **A video** that stopped at "opening video": does it play now? Please send the file's details (codec, size).
- **Ember**: cycling games, are your controllers kept?
- **Your USB pad**: write a .pad for it (docs/plans/pad-spec.md) and check it in My Pads; send it to us.
- **RIPPS2-lite.elf**: everything works the same, and BIBLE / Neutrino installs say they need the full ELF?

## Report
Please [open an issue on GitHub](https://github.com/akilluminati47/RIPPS2/issues) with your **console model**, your drives, your **boot loader**, where RIPPS2 starts from, your **DIAG.TXT** (STATUS > SAVE DIAGNOSTICS) and a **photo** of anything odd. Thanks to ripto, nuno6573, zackcage6, eliminator1403, FifthFox, Mr.sus.60, lukeatmynose and ahavasi for the reports that got us here, to DarkNerdShawny for opening issues on GitHub, and to everyone testing RIPPS2 on Discord and opening issues on GitHub: be like them. Special thanks to all the YouTube love as well: glad to help however you reach me.
