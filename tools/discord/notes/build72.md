# Ember rides inside RIPPS2, HDD programs start from the browser, the music stops stuttering, and Favorites shows your recent games. Real PS2s wanted: here is what to try.

## PS1 games
- **Ember is built in.** The first time you start an Ember game from a drive, RIPPS2 puts Ember in that drive's EMBER folder by itself (with its licence). Ember games show up even before Ember is there. Bring your own PS1 BIOS as EMBER/bios.bin.
- POPSTARTER still starts from your own copy, which RIPPS2 finds on your drives.
- **Ember Game Settings** save per game from Triangle, and PS1 rows explain their save-card menu (RiptOPL upstream).

## Memory Files
- **.elf and .ELF programs start from the internal HDD** too (it used to say "use the APPS page").

## Smoother
- **No more music stutter during big loads**: the music decoder takes the CPU first whenever its reserve runs low.
- The towers cost about half as much per frame (far towers drawn simpler, and simpler still while the PS2 is busy), so more frames stay at full speed.
- **One press, one sound**: a custom AUDIO pack no longer plays confirm, page in and page out on top of each other.

## Colors and More (Settings > Interface)
- **Source Name** (ALL GAMES, HDD GAMES...): Shown, Fade When Idle (with the category bar) or Hidden.
- **Show Recents** 0 to 9: your last launched games at the top of Favorites, newest first. 0 turns it off.
- Every button hint reads in lowercase, the save prompt and START menu included.

## Neutrino (RiptOPL upstream)
- Every Neutrino argument can be edited from the game's settings, with clearer video modes and a warning before the arguments get too long.

## Test list
- **Ember game on a drive without Ember:** does RIPPS2 install it and start the game? (BIOS in place.)
- **Ember Game Settings** from Triangle: change one, start the game. Did it stick?
- **An .elf on your internal HDD** from Memory Files: does it start?
- **Music on, then start your drives** or open a big list: any stutter left?
- **Leave Storage idle with music** for a few minutes: smooth frames?
- **Custom AUDIO pack:** open and close pages. One sound each time?
- **Show Recents 3**, launch three games, then open Favorites. Newest first?
- **Source Name: Fade When Idle**: does it fade with the category bar and come back on a press?
- **RIPFLOW** (Interface > Theme): covers only, sources on Up / Down. Still good?
- **Neutrino arguments** on a game: edit, launch. Does it behave?
- **HDD games** (APA): list, art, launch. Anything slower or broken?
- **Info page and back**, both themes: anything odd?
- **Save Settings** after changes: saved after a power cycle?
- **Overnight on Memory Files:** still smooth in the morning?

## Report
Post here with your **console model**, where your games live (USB, HDD, MX4SIO, MMCE, iLink, network) and a **photo** of anything odd.
