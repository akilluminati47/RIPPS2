# Build 133: Pass C, themes (plan, 2026-11-02)

The user's notes (11/02):
1. RIPGRID L1/R1: "the same as l2/r2 pages of the grids games specific for grid sidebar".
2. "Make Adapt and legacy themes default the favorite star to right side", and "make the star on the right side
   mean all the way not end of characters".
3. "Adapt and ripgrid to use sky of theme choice instead of flat bg colors for smoother transitions to storage,
   create a vignette (rip it directly from the sky so it blends) for the upper and lower matching the skys so it can
   be applied to the main page of ripgrid and adapt over the game bg art under the glyphs etc."

## What is there now

- **RIPGRID's shoulder buttons** (menusys.c menuHandleInputMain / menuShoulderKeys): RIPGRID sets
  `page_buttons=l2r2`, so L2 / R2 turn the grid a page of covers (menuGridPage). With the sidebar on, L1 / R1 turn
  pages only when Page Buttons is not L2 / R2, so on RIPGRID they do nothing; with it off they change category.
- **The star** (themes.c drawItemsList): Starred Games Star (Theme / Left / Right / Hidden, Hidden until R3's hold)
  or, on Theme, the list's `<name>_star` key, LEFT when a theme has none. Right puts the star just after the title
  (`textEndX + 4`).
- **Flat backgrounds**: a theme with `towers=0` (RIPGRID, Adapt, Adapt Rx) fills its empty backdrop with bg_color
  (themes.c thmDrawEmptyBackdrop). Storage's sky is a three-colour gradient (ripps2bg.c drawSky: top, horizon at
  y 290, floor) in the Color Theme in effect (ripps2ui.c ripps2BibleSky works the colours out; a Color Sweep moves
  them).

## The change

1. **RIPGRID with the sidebar: L1 / R1 page the grid as L2 / R2 do** (menuGridPage, a page of covers, the cursor
   keeping its place). Only on a grid with the sidebar on; RIPGRID without the sidebar keeps L1 / R1 on the
   categories, other themes as they are.
2. **The star.**
   - Right means the row's right edge: the star sits at the end of the row's width, and a long title stops short
     of it (its fit room shrinks by the star), so the stars line up in a column on the right.
   - Every theme RIPPS2 does not build in (Adapt, Adapt Rx, a theme made for OPL) defaults to Right when its list
     has no `_star` key. RIPPS2, RIPFLOW and RIPGRID keep theirs (Left). The setting still overrides.
3. **The sky on Adapt and RIPGRID.**
   - Where a towers=0 theme filled bg_color, it draws Storage's sky instead (the same gradient, in the Color Theme
     in effect, following a Color Sweep), so going between a game page and Storage, Launch Disc or Memory Files no
     longer jumps from a flat colour to the sky.
   - **A sky vignette** on those themes' main page, over the game's background art and under everything after it
     (glyphs, text, hints): a band at the top from the sky's top colour fading to clear, and one at the bottom from
     its floor colour, taken from the same three colours so it blends. Drawn by RIPPS2 right after the main page's
     background art, so Adapt needs no new theme pack.

## Lab, then CI, then push

- RIPGRID, Category Layout Sidebar: R1 and L1 each turn a page; L2 / R2 as before; sidebar off, L1 / R1 categories.
- The star on Right: a short and a long title, RIPPS2 and Adapt; Adapt on Theme shows Right.
- RIPGRID and Adapt: a game with no BG art (the sky), a game with BG art (the vignette), Storage and back, with two
  Color Themes. Grabs tiled for the user. CI, push to main; release only on the user's word.
