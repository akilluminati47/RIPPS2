# Build 132: Pass B, RIPFLOW and the RIPPS2 info page (plan, 2026-11-02)

The user's notes (11/02), with their answers the same day:
1. "Idle on game for 4.2 seconds fade with cover timing to square info n triangle settings glyphs flank instead of
   the x and o and stays until game change (upgrades flank hints)". The cover timing = the screenshots' fade (the
   same clock).
2. "Info page categories fade instead of hidden for ripflow in sync with screen shot fade". Categories = the bar's
   LAUNCH DISC / STORAGE / MEMORY FILES: on RIPFLOW's info page they should fade as their setting says, not be gone.
3. "Ripps2 info have arts on top of the glass in the viewport for full color". Arts = the BG art and the SCRn
   slideshow in the info page's viewport: they look tinted. The logo, drawn after the glass, looks right.

## What is there now

- **Flank hints** (themes.c, the MenuText drawing, `hints_flank=1` in misc/theme_coverflow.cfg): either side of the
  source name, Cross RUN on the left and Circle SOURCE on the right (BACK on the info page), at Source Name's alpha.
- **The bar on an info page**: menusys.c `menuRenderInfo` never draws it ("the info page gives the whole screen to
  the game's art panel"). On the list page it follows Category Bar: Shown / Fade When Idle / Hidden
  (`ripps2CatBarAlpha`).
- **The RIPPS2 info page** (elf/theme/conf_theme.cfg): info1 (BG) and info2 / info3 (SCRn) fill the viewport
  (14,40 448x336), then info4 (Ripps2PanelGlass) is drawn over the same rect: its tint and frost go over the art.

## The change

1. **Flank hints turn into Square INFO / Triangle OPTIONS** (every theme with hints_flank, RIPFLOW first). With the
   selection on one game for 4.2 s, the two flank hints cross-fade, over the screenshots' fade time (SLIDE_FADE_S),
   from Cross RUN / Circle SOURCE to Square INFO / Triangle OPTIONS, and stay until the selection moves, when they
   fade back the same way. While they flank, Square and Triangle leave the hint row at the bottom (as RUN does now).
   Only on a list page with a game under the cursor. Triangle keeps its hint row word, OPTIONS.
2. **The bar on RIPFLOW's info page.** menuRenderInfo draws the bar on a theme that asks for it (a new
   `info_catbar=1`, set in theme_coverflow.cfg), at its setting's alpha: Shown stays, Fade When Idle fades,
   Hidden stays gone. Coming onto the info page it fades in over the screenshots' fade time, so it moves with them.
3. **The RIPPS2 info page's art over the glass.** In conf_theme.cfg the glass goes first and the BG and SCRn boxes
   after it, so they show at full colour; the glass's frame is drawn again over the art's edge (a frame-only
   glass, or a key on the glass element, whichever the code takes more simply), so the viewport keeps its border.
   The logo and the rest stay as they are.

## Lab, then CI, then push

- RIPFLOW: rest on a game 5 s (the flank turns at 4.2 s), move (it turns back); hint row without Square / Triangle.
- RIPFLOW info page with Category Bar on Shown, Fade When Idle, Hidden.
- RIPPS2 theme info page: a game with BG and screenshots, grabbed beside build 131's to compare the colour.
- Tiled grabs for the user. CI, push to main; release only on the user's word.

## Lab results (11/02, PCSX2, NTSC, CI run 41511627073 for 2ef0e0a)

- RIPFLOW (Source Name Shown): a START row keeps RUN / SOURCE after 5 s; State of Emergency shows INFO / OPTIONS by
  4.8 s; a move back cross-fades to RUN / SOURCE (media/b132/ripflow-flank.jpg). The first take showed no source
  name: the reel card's ripps2_srcname=3 (Pop In) leaves the flank hints out by design.
- RIPFLOW info page: the bar fades in (0.4 s dim, 2 s full) at Shown (media/b132/new-02-ripflow-info-bar.jpg).
- RIPPS2 info page, 131 against 132: BG art and screenshots brighter above the title, text band as before
  (media/b132/info-bg-131-vs-132.jpg, info-scr-131-vs-132.jpg).
