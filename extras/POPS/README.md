# POPSTARTER's in-game reset pictures, in RIPPS2's look

`IGR_BG.TM2`, `IGR_YES.TM2` and `IGR_NO.TM2` replace the pictures POPSTARTER shows when you press the in-game reset
combo in a PS1 game: the "quit the game?" panel and its YES / NO buttons. These are drawn with RIPPS2's own in-game menu
renderer (the same font, colours and panel as RIPPS2's in-game menu) over black, at the size and button places
POPSTARTER expects.

To use them, copy the three files into your `POPS` folder, beside `POPSTARTER.ELF`. Move your old ones somewhere safe
first if you want to keep them. POPSTARTER itself is not changed: only its pictures are.

They are made by `tools/pops-igr/make_igr.py` (RIPPS2 build 126).
