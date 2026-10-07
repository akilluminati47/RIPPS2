# Build 88: your console's own sounds ripped by RIPPS2, an in-game menu to test, the CARD MANAGER, RiptOPL's latest, and a launch report for PS1 games.

## Your console's sounds (88)
- **Audio settings > BIOS Sounds > Rip** writes the menu sounds from your own console's BIOS into `AUDIO` as RIPPS2's sounds (13 of them), and they play at once. Boot and launch stay as they are. **Music** plays a track called Menu first.

## In-game menu (87, off until you turn it on)
- **Settings > General > In-Game Menu.** Then **L1+L2+R1+R2+SELECT+START** in a game pauses it under **Resume / Achievements / Exit Game**. Exit takes two presses and goes where Exit To points (RIPPS2, boot lock, browser). Not for Neutrino games yet. PCSX2 cannot show it: consoles only.

## CARD MANAGER (86)
- **Square on memory card 1 or 2** in Memory Files: delete saves, back up the card to a VMC, write a VMC's saves back, erase game saves, format (never the card RIPPS2 runs from).

## PS1 and video (84, 85)
- RiptOPL's latest merged. A PS1 launch writes `mc0:/RIPPS2/LAUNCH.TXT`; missing POPS files are flagged before launch. The 704-wide modes draw in one pass. CD player hints stay on screen.

## Test list
1. **BIOS Sounds > Rip**: 13 sounds written, playing right away? Your console model?
2. After the rip, do cursor, confirm, cancel, page in and out sound like your console's own browser?
3. With `bgm_03 Menu.ogg` in AUDIO and no track picked, does Menu play first?
4. **In-Game Menu on**, a game from USB or HDD, then L1+L2+R1+R2+SELECT+START: does the panel show over the frozen game?
5. **Resume**: does the game carry on cleanly (picture, sound, controls), with no stray button press?
6. While paused: is the sound silent, looping, or still playing?
7. **Achievements** page: are the numbers right for a tracked game?
8. **Exit Game**, twice: do you land on your Exit To (RIPPS2, boot lock, browser)?
9. With the menu on, does any game fail to start or act up? Turn it off, try again, and name the game.
10. **CARD MANAGER**: delete one save, back up a card to a VMC, write the VMC back to the other card.
11. **Erase every game save** on a spare card: boot loaders and system folders kept?
12. A PS1 game that will not start: open `mc0:/RIPPS2/LAUNCH.TXT` in Memory Files and post a photo.
13. No POPS files: does the warning come up before the launch?
14. Video mode **704x480p** or **704x576**: confirm it and let the prompt time out. Any freeze?
15. **Launch Disc** with an audio CD: are all the button hints on screen, CLOSE included?
16. Neutrino games over **iLink** (FifthFox): do they boot now?

## Report
Post here with your **console model**, the device the game ran from, the game, and a **photo** of anything odd.
