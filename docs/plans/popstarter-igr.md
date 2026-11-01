# POPSTARTER's in-game reset: RIPPS2's buttons and words (plan, not built)

The user, 11/01: POPSTARTER's IGR should take **X to select and O to go back**, and read like RIPPS2's own in-game menu
exit flow (EXIT GAME, confirmed twice). Build 126 replaced only POPSTARTER's three pictures (`IGR_BG.TM2`,
`IGR_YES.TM2`, `IGR_NO.TM2`, made by `tools/pops-igr/make_igr.py`, shipped in `extras/POPS`).

## What the pictures can and cannot do

- POPSTARTER is closed (krHACKen's binary). Its IGR prompt is its own code: which buttons move between YES and NO,
  which one confirms, whether O cancels, and that one confirm on YES quits. None of that is in the TM2 files.
- The pictures are a 400 x 260 background (static: it does not change with the selection) and two 74 x 34 buttons
  (YES and NO, each drawn highlighted or not as POPSTARTER chooses). So the words can match RIPPS2 exactly, but
  a second confirm cannot be added, and a button POPSTARTER does not read cannot be made to work by a picture.

RIPPS2's flow for comparison (ee_core/src/igrmenu.c): EXIT GAME shows "LEAVE THE GAME FOR / RIPPS2 / UNSAVED PROGRESS
IS LOST", the hint line "(X) SELECT (O) RESUME"; the first X arms it ("PRESS (X) AGAIN TO LEAVE"), the second leaves.

## Plan

1. **Measure POPSTARTER's prompt on the console** (no build). The lab cannot: POPSTARTER.ELF is packed (no readable
   text, checked 11/01 on the user's SD2PSX copy, 167,700 bytes), and the user's POPS reads the SD2PSX through renamed
   MMCE drivers (usbd.irx.mmce, usbhdfsd.irx.mmce), which PCSX2 does not emulate. The user opens a POPS game, presses
   the IGR combo and notes: which of YES / NO is lit first, what Left / Right / Up / Down do, what X does on NO and on
   YES, what O / Triangle / START do, and whether the prompt closes by itself. The SD2PSX still has POPSTARTER's
   original 2018 pictures, so this measures POPSTARTER itself.
2. **If POPSTARTER already reads X = confirm and O = back** (or Left/Right + X with O closing): pictures only, a new
   `make_igr.py` set:
   - the background in RIPPS2's exit page words: "EXIT GAME", "LEAVE THE GAME FOR THE PS2 BROWSER" (or what
     POPSTARTER returns to), "UNSAVED PROGRESS IS LOST", and RIPPS2's hint line with the real glyphs, "(X) SELECT
     (O) RESUME";
   - the two buttons renamed to RIPPS2's rows, "EXIT GAME" and "RESUME", the highlighted look as RIPPS2's selected row;
   - "confirmed twice" as near as the pictures allow: if NO / RESUME is highlighted first, moving to EXIT GAME and
     pressing X is the two steps, and the EXIT GAME button's highlighted picture reads "(X) TO LEAVE" like the armed
     line. Same sizes and TIM2 layout as now; the user's own set kept in the holding folder when RIPPS2 copies them.
3. **If POPSTARTER reads other buttons** (O does nothing, or confirm is a different button): pictures cannot fix that.
   Options, in the order I would take them:
   - a. **Words that tell the truth**: the pictures above, but the hint line shows POPSTARTER's real buttons. Ships
     now, no risk.
   - b. **Ember for PS1 games that need it**: Ember runs under RIPPS2's own in-game menu (X / O, EXIT GAME twice);
     the PS1 flow (build 126, PS1 Duplicates) already lets the user prefer Ember per title.
   - c. **Patch POPSTARTER in memory at launch** (RIPPS2 loads POPSTARTER.ELF, changes its button test, jumps to it;
     the file on the drive is never changed and nothing of POPSTARTER is shipped). Needs reverse engineering a closed
     binary, works only for the POPSTARTER versions we fingerprint (by size and hash), and must fall back to the plain
     launch on any other. Not without the user's go-ahead: it is a third party's closed program.
4. Lab check of whatever is built (the prompt open, each button, quit and resume) before it goes in a release; the
   real-hardware check goes on the testers' list.

Waiting on the user before step 2 or 3 is built. Step 1 (measuring) needs the user's POPS files on the lab image.
