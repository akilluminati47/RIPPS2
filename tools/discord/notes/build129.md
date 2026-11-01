# Build 129: USB pads RIPPS2 did not know. Set one up on the PS2, and it steers the menu and plays in games.

## Get it
- [Download the latest RIPPS2.elf](https://github.com/akilluminati47/RIPPS2/releases/latest/download/RIPPS2.elf) (or the smaller [RIPPS2-lite.elf](https://github.com/akilluminati47/RIPPS2/releases/latest/download/RIPPS2-lite.elf)), [RIPPS2-languages.zip](https://github.com/akilluminati47/RIPPS2/releases/latest/download/RIPPS2-languages.zip) and the [theme pack](https://github.com/akilluminati47/RIPPS2-themes/releases/latest/download/RIPPS2-themes.zip), edition 128 (unchanged)

## New
- **Set Up A USB Pad** (Settings > Controllers): plug the pad in, let go, press each button and push each stick as RIPPS2 asks (SELECT on your PS2 pad skips one), try it live, save. RIPPS2 writes `PADS/VVVV_PPPP.pad` beside itself.
- **A profiled pad steers the menu**, from boot and as soon as you save it.
- **It plays in games** with the Pad Emulator on: RIPPS2 checks your profiles as the game starts and hands them to PADEMU. Nothing is read from a file during the game.
- **A button map per game**: `PADS/GAMES/<game ID>.pad` (`cross=circle`, `select=none`) moves buttons for that game, on every USB pad.
- **My Pads** checks every profile and says what is wrong with any it refuses.
- Every new line translated in all 32 languages.

## Test list
- **Set Up A USB Pad** with a pad RIPPS2 did not know (a copy DS3, an 8BitDo, an arcade stick, any USB gamepad): does it find the pad? Does every button and stick get found?
- **Try it** at the end: does what you hold match the buttons you pressed? Sticks the right way round?
- **After saving**, does the pad move the menu (d-pad, Cross, Circle, START)?
- **In a game** with the Pad Emulator on for that pad's port: does the game see every button and both sticks?
- **A d-pad that is a hat** (most generic pads) and one that is four buttons: both right?
- **Analog triggers** (L2 / R2 that are axes): found as L2 / R2 and pressed past half in game?
- **SELECT skips** a button you do not have; does the saved file say `none` for it?
- **Back out** halfway (Circle): nothing written, and your old profile still works?
- **Set up the same pad twice**: is the first file kept as `.bak`?
- **A game map**: put `cross=circle` in `PADS/GAMES/<the game's ID>.pad`: swapped in that game only?
- **Your DualShock 3 / 4 and the ShanWan copy** still work in the menu and in games as before?
- **USB storage beside the pad**: games from USB still load with the pad plugged in?
- **My Pads** after setting one up: listed as OK with its name?
- **Send us your `.pad`** files (with the pad's name) so other people with the same pad can use them.

## Report
Please [open an issue on GitHub](https://github.com/akilluminati47/RIPPS2/issues) with your **console model**, the **pad** (its name and the VVVV_PPPP of its file), your **boot loader**, where RIPPS2 starts from, your **DIAG.TXT** (STATUS > SAVE DIAGNOSTICS), the **.pad** RIPPS2 wrote, and a **photo** of anything odd. Thanks to ripto, nuno6573, zackcage6, eliminator1403, FifthFox, Mr.sus.60, lukeatmynose and ahavasi for the reports that got us here, to DarkNerdShawny for opening issues on GitHub, and to everyone testing RIPPS2 on Discord and opening issues on GitHub: be like them. Special thanks to all the YouTube love as well: glad to help however you reach me.
