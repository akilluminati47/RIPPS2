## Kill it: RIPPS2 build 81 (alpha)

**RIP PS2, the ELF killer.** ELF-sufficient, never ELF-destructive: your other ELFs stay safe on the [shelf](https://akilluminati47.github.io/RIPPS2/), they just get a well-earned rest.

**[Download RIPPS2.elf](https://github.com/akilluminati47/RIPPS2/releases/download/v0.0.81-alpha/RIPPS2.elf)**, the **[theme pack](https://github.com/akilluminati47/RIPPS2-themes/releases/latest)** (Adapt, Adapt Rx, RIPgrid), and **[theme it yourself](https://github.com/akilluminati47/RIPPS2-themes)**: everything below is a theme key, no rebuild.

### New in 81
- **The source name as a toast.** With Source Name on Pop In (the Adapt family's default), ALL GAMES, HDD GAMES and the rest play big in the middle of the page, like L3's ALL, on boot, on a source change and on coming back to Storage, then fade. No more static line over the list.
- **Themes choose their own Colors and More** in `conf_theme.cfg`: colour theme, category bar, hints, D-pad glyphs, category order, source name. **Your settings always win**: a theme's choice only shows on a row you have never changed.
- **RIPFLOW puts Memory Files first** on the category bar, unless you picked an order.
- **Adapt Rx keeps its side bar on the left**: the list and the case swap sides, with even spacing (theme pack updated).
- **Lighter on the GS**: every built-in image and every theme pack image is an 8-bit palette PNG, a quarter of the VRAM; the ELF is 53 KB smaller.

### Your sounds
RIPPS2 was voiced with Sony's own PS2 sounds and a Nintendo track to browse by. None of it ships, but **[the sound map](https://github.com/akilluminati47/RIPPS2#the-sound-ripps2-was-made-with)** shows every event's sound, and **[RIPPS2 Audio Studio](https://github.com/akilluminati47/RIPPS2/tree/main/tools/audio-studio)** rips them from your own console's BIOS into an `AUDIO` folder beside `RIPPS2.elf`.

Full list: [CHANGELOG.md](https://github.com/akilluminati47/RIPPS2/blob/main/CHANGELOG.md). Alpha: keep your usual loader close by.
