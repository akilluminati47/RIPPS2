# Build 140: the sounds sorted out, Set Metadata (Rename) on every row, and a timeline for L1 and R1 in the video player.

## Get it
- **RIPPS2.elf** and **RIPPS2-languages.zip** are attached below, or from the [release page](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.4.0-beta).

## New
- **Sounds**: each one now ends on its own silent block as it loads, so nothing should play on after it. The boot sound comes in with the towers, and the rest load ahead of the drive jobs.
- **Set Metadata (Rename)**: one name on every row, a page like Settings, the file name first, and a tip saying what a rename does. A PS1 game's art and settings go with it.
- **Video player**: L1 and R1 move a marker on a timeline. A tap is 10 s, a hold runs, and it jumps once when you let go.
- **Manage's BIBLE menu**: Stop Disc at Launch and four more rows.
- **DIAG.TXT** ends with a trace of every sound and who asked for it.

## Test list
- Boot with your usual drives: is the boot sound there with the towers, and whole?
- Press confirm and switch categories, then let each sound finish. Does anything play after it?
- Tap and hold L2 + R2 for a random game, with music on and off. Any ringing?
- Scroll the list while the loading icon shows. Any sound you did not press for?
- Does the music start once at boot?
- Open Set Metadata (Rename) on a PS2 game, a PS1 game and an app. Does the tip fit, and is it right?
- Rename a PS1 game that has art. Is the art still there afterwards?
- Rename a PS2 game. Is its art still there?
- Set Metadata (Rename) on a starred game and on Favorites: does the tip say why not?
- On a long film, tap R1 quickly many times. Does it jump once and keep playing?
- Hold R1 far into a film and let go. Then hold again and press cancel.
- Stop Disc at Launch Off in Manage's BIBLE menu: is the boot faster, and how much?

## Report
Say your console model and what you did, and attach your `DIAG.TXT`: STATUS > SAVE DIAGNOSTICS, or it saves itself when a game or a video starts from a drive.
