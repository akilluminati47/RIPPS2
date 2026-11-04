# Builds 140 and 141: BIBLE's settings on one page with a tip on every row, launch keys chosen from your drives, the sounds sorted out, a timeline for L1 and R1 in the video player. The new pages have only run in the lab, so tell us what breaks.

## Get it
- **RIPPS2.elf**, **RIPPS2-languages.zip** and **RIPPS2-themes.zip** are attached below, or from the [release page](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.4.1-beta). What's new, with pictures: [1.4.1](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.4.1-beta) and [1.4.0](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.4.0-beta).

## New
- **BIBLE's Settings page** (Manage, with BIBLE on a card): a page like Settings, a tip on every row, the cursor stays put, Sky Color and Boot Sound, and the file written once and safely when you leave.
- **Launch Keys**: each button's name and ten paths, chosen with the Memory Files browser, typed, or one of BIBLE's commands, with arguments.
- **Sounds**: each one ends on its own silent block as it loads. The boot sound comes in with the towers, and the rest load ahead of the drive jobs.
- **Set Metadata (Rename)**: one name on every row, a page like Settings, the file name first, and a tip saying what a rename does. A PS1 game's art and settings go with it.
- **Video player**: L1 and R1 move a marker on a timeline. A tap is 10 s, a hold runs, and it jumps once when you let go.
- **DIAG.TXT** ends with a trace of every sound and who asked for it.

## Test list
- Manage with BIBLE on your card: do the rows and tips read right, and does the cursor stay on its row?
- Change Background and Power-on Wait, leave the page, power on. Did BIBLE take them?
- Pick a Sky Color by name, power on. Is the splash that colour?
- Launch Keys: choose a program for a button, power on holding it. Does it start?
- Choose a program on USB, MMCE, MX4SIO or the HDD: is the path right, and does the tip match your BIBLE build?
- Hold L2 + R2 at power on: does BIBLE's page match what you set?
- Add an argument to a path. Does the program get it?
- Your notes in PS2BBL.INI: are they still there after a change?
- Boot with your usual drives: is the boot sound there with the towers, and whole?
- Press confirm and switch categories, then let each sound finish. Does anything play after it?
- Does the music start once at boot?
- Set Metadata (Rename) on a PS2 game, a PS1 game and an app: does the tip fit, and is it right?
- Rename a PS1 game that has art. Is the art still there afterwards?
- On a long film, tap R1 quickly many times, then hold it far in and let go. Does it jump once and keep playing?

## Report
Say your console model and what you did, and attach your `DIAG.TXT`: STATUS > SAVE DIAGNOSTICS, or it saves itself when a game or a video starts from a drive.
