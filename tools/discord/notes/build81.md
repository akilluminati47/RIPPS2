# Build 81: the source name as a toast, themes that pick their own colours (you still win), and the sound RIPPS2 was made with.

## The source name, as a toast
- With **Source Name: Pop In** (Colors and More, and the Adapt family's default) ALL GAMES, HDD GAMES and the rest play big in the middle of the page, like L3's ALL, on boot, on a source change and on coming back to Storage, then fade. The static line over the list is gone, and L3's ALL / PS1 / PS2 now plays in the same big Sleek face on every theme.

## Themes pick their look, you keep the last word
- A theme's `conf_theme.cfg` can now set Colors and More: colour theme, category bar, hints, glyphs, category order, source name. Anything **you** change in Colors and More stays yours on every theme.
- **RIPFLOW** puts Memory Files first unless you picked an order. **Adapt / Adapt Rx**: the disc sits right under LAUNCH DISC (Rx moves LAUNCH DISC to the right), side bar on the left (re-download the [theme pack](https://github.com/akilluminati47/RIPPS2-themes/releases/latest)).
- Make your own: [RIPPS2-themes](https://github.com/akilluminati47/RIPPS2-themes), everything is a theme key, no rebuild.

## Fill your AUDIO folder
- The [sound map](https://github.com/akilluminati47/RIPPS2#the-sound-ripps2-was-made-with) lists the sound for every event (Sony's PS2 sounds, a Nintendo track to browse by). [RIPPS2 Audio Studio](https://github.com/akilluminati47/RIPPS2/tree/main/tools/audio-studio) rips them from **your own** console's BIOS dump: copy its `AUDIO` folder beside `RIPPS2.elf`.

## Lighter
- Every built-in and theme image is now an 8-bit palette PNG: a quarter of the VRAM, a smaller ELF.

## Test list
- **Adapt or RIPgrid**: does the source toast play on boot, on Left / Right (or Circle on RIPgrid) and coming back from Launch Disc? Big and centred, not a small line?
- **Adapt / Adapt Rx**: is the disc right under LAUNCH DISC on 4:3 and 16:9? Side bar on the left in both?
- **RIPFLOW**: Memory Files on the left of the bar? Then pick Launch Disc First in Colors and More: does it stay that way after a reboot?
- **Colors and More**: change a row on one theme, switch themes with a SELECT hold: does your pick stay?
- **Sounds**: rip your BIOS with Audio Studio following the sound map: does every event play?

## Report
Post here with your **console model**, video mode (4:3 or 16:9), which theme, and a **photo** of anything odd.
