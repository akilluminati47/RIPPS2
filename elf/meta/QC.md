# RIPPS2 metadata DB: QC notes (first 11 entries)

Checked 2026-10-01. Every value in `db/<GAMEID>.cfg` is listed below with where it was verified. Descriptions are original text; their facts come from the same sources.

Common sources (one URL per game, linked in each table):

- MC = Metacritic game page (critic Metascore for the PS2 version)
- GF = GameFAQs PS2 release data page (serial, region date, publisher, local players)
- WP = English Wikipedia article (infobox and body)
- GB = Giant Bomb wiki page
- ADM = PlayStation fan wiki, "List of PlayStation 2 games with alternative display modes": https://playstation.fandom.com/wiki/List_of_PlayStation_2_games_with_alternative_display_modes
- DISC = read-only inspection of the user's own ISO in `B:\Emulation\PlayStation\PCSX2\_games` (SYSTEM.CNF, menu and options text strings). Nothing was run or modified.

Rating scale: 90+ = 5, 80-89 = 4, 70-79 = 3, 60-69 = 2, below 60 = 1.

## SLUS_206.42 Auto Modellista

MC https://www.metacritic.com/game/auto-modellista/ , GF https://gamefaqs.gamespot.com/ps2/547928-auto-modellista/data , WP https://en.wikipedia.org/wiki/Auto_Modellista , GB https://giantbomb.com/wiki/Games/Auto_Modellista

| Field | Value | Source |
|---|---|---|
| Developer | Capcom Production Studio 1 | WP, GB (MC and GF just say Capcom) |
| Publisher | Capcom | WP, GF (US row), MC |
| Release | 2003-03-25 | WP, GF (SLUS-20642), MC |
| Players | 2 | GF (1-2 local, up to 8 online), DISC (1P and 2P wheel calibration) |
| Vmode | ntsc | SLUS serial, DISC SYSTEM.CNF VMODE = NTSC |
| Aspect / Scan | s / 480i | DISC: the full options help text lists sound, screen position, camera, language etc. with no aspect or progressive setting; not on ADM |
| Rating | 2 (Metascore 66) | MC |

## SLUS_210.50 Burnout 3: Takedown

MC https://www.metacritic.com/game/burnout-3-takedown/ , GF https://gamefaqs.gamespot.com/ps2/919649-burnout-3-takedown/data , WP https://en.wikipedia.org/wiki/Burnout_3:_Takedown , GB https://giantbomb.com/wiki/Games/Burnout_3_Takedown

| Field | Value | Source |
|---|---|---|
| Developer | Criterion Games | WP, MC, GF |
| Publisher | EA Games | GF (US row), MC, GB (WP: Electronic Arts, the parent) |
| Release | 2004-09-07 | GF (SLUS-21050), MC, GB. WP says 8 September 2004 (outvoted 3 to 1) |
| Players | 2 | GF (1-2 local, up to 6 online), WP (two-player crash modes) |
| Vmode | ntsc | SLUS serial, DISC VMODE = NTSC |
| Aspect / Scan | w / 480p | ADM (16:9 yes, 480p yes via X+Triangle at boot), DISC (menu text "ASPECT RATIO 4:3 16:9" and "480p (Progressive Scan)") |
| Rating | 5 (Metascore 93) | MC |

## SLES_510.61 Grand Theft Auto: Vice City (Debug Build 2002-10-01)

Hidden Palace https://hiddenpalace.org/Grand_Theft_Auto:_Vice_City_(Oct_1,_2002_prototype) , WP https://en.wikipedia.org/wiki/Grand_Theft_Auto:_Vice_City , GF https://gamefaqs.gamespot.com/ps2/561545-grand-theft-auto-vice-city/data

| Field | Value | Source |
|---|---|---|
| Title | debug build label | per brief |
| Developer | Rockstar North | WP, GF |
| Release | 2002-10-01 (build date) | per brief; Hidden Palace gives compile date 1 Oct 2002 22:34:23 |
| Players | 1 | WP (single-player), GF (1 player) |
| Vmode | pal | DISC: SYSTEM.CNF says VMODE = PAL, disc only carries VCPAL.PSS / VICEPAL.PSS movies and the ELF only references the PAL movie; Hidden Palace calls it a PAL prototype (serial SLES-51061). The "(NTSC)" in the file name is wrong |
| Aspect | w | DISC: the build's own AMERICAN.GXT has the display menu entry "Wide Screen :" (key FED_WIS) next to Brightness, Trails and Subtitles; retail VC has 16:9 per ADM. Not confirmed by running the build |
| Scan | 480i | DISC: no progressive text anywhere in the build; retail VC has no 480p per ADM |
| Publisher, Rating | omitted | per brief (unreleased build) |

## SLUS_210.08 Katamari Damacy

MC https://www.metacritic.com/game/katamari-damacy/ , GF https://gamefaqs.gamespot.com/ps2/918766-katamari-damacy/data , WP https://en.wikipedia.org/wiki/Katamari_Damacy , GB https://giantbomb.com/wiki/Games/Katamari_Damacy

| Field | Value | Source |
|---|---|---|
| Developer | Namco & Now Production | WP infobox and GB credit Namco; WP development section says Namco brought in Now Production to build it; MC and GF credit Now Production |
| Publisher | Namco Hometek | WP (NA publisher); GF and MC say Namco |
| Release | 2004-09-21 | WP, GF (SLUS-21008), MC |
| Players | 2 | GF (1-2), WP (split-screen two-player mode) |
| Vmode | ntsc | SLUS serial, DISC VMODE = NTSC |
| Rating | 4 (Metascore 86) | MC |
| Aspect, Scan | omitted | Not on ADM and community widescreen hacks exist, but menus are image-based so the disc could not confirm, and one web 480p list contradicts the others |

## SCUS_971.99 Ratchet & Clank

MC https://www.metacritic.com/game/ratchet-clank/ , GF https://gamefaqs.gamespot.com/ps2/561107-ratchet-and-clank/data , WP https://en.wikipedia.org/wiki/Ratchet_%26_Clank_(2002_video_game) , R&C wiki https://ratchetandclank.fandom.com/wiki/Ratchet_%26_Clank_(2002_game) , Insomniac post https://www.facebook.com/insomniacgames/posts/-nov-4-2002-ratchet-clank-first-debuted-23-years-ago-today-on-playstation-2-/1234050822085539/

| Field | Value | Source |
|---|---|---|
| Developer | Insomniac Games | WP, MC, GF |
| Publisher | Sony Computer Entertainment America | GF (SCEA, US row), MC |
| Release | 2002-11-04 | Insomniac's own anniversary post, GF (SCUS-97199), MC, R&C wiki. WP says Nov 6 and GB says Nov 5 (outvoted) |
| Players | 1 | WP, GF |
| Vmode | ntsc | SCUS serial, DISC VMODE = NTSC |
| Aspect / Scan | s / 480i | DISC: options text (effects volume, music volume, stereo/mono, camera speed, PAL 60Hz prompt) has no 16:9 or progressive entry, while the sequels' discs do; not on ADM (its sequels are) |
| Rating | 4 (Metascore 88) | MC |

## SCUS_972.68 Ratchet & Clank: Going Commando

MC https://www.metacritic.com/game/ratchet-clank-going-commando/ , GF https://gamefaqs.gamespot.com/ps2/914659-ratchet-and-clank-going-commando/data , WP https://en.wikipedia.org/wiki/Ratchet_%26_Clank:_Going_Commando , GB https://giantbomb.com/wiki/Games/Ratchet_And_Clank_Going_Commando

| Field | Value | Source |
|---|---|---|
| Developer | Insomniac Games | WP, MC, GF |
| Publisher | Sony Computer Entertainment America | GF (SCEA), MC |
| Release | 2003-11-11 | WP, GF (SCUS-97268), MC, GB. Note: this ISO is v2.00 (Greatest Hits reprint, GF lists 2004-09-08); the original release date is used |
| Players | 1 | WP, GF |
| Vmode | ntsc | SCUS serial, DISC VMODE = NTSC |
| Aspect / Scan | w / 480p | ADM (16:9 vert-, 480p yes), DISC ("16:9 (widescreen)" and "Progressive Scan" menu text) |
| Rating | 5 (Metascore 90) | MC |

## SCUS_973.53 Ratchet & Clank: Up Your Arsenal

MC https://www.metacritic.com/game/ratchet-clank-up-your-arsenal/ , GF https://gamefaqs.gamespot.com/ps2/919902-ratchet-and-clank-up-your-arsenal/data , WP https://en.wikipedia.org/wiki/Ratchet_%26_Clank:_Up_Your_Arsenal , R&C wiki https://ratchetandclank.fandom.com/wiki/Ratchet_%26_Clank:_Up_Your_Arsenal , GB https://giantbomb.com/wiki/Games/Ratchet_And_Clank_Up_Your_Arsenal

| Field | Value | Source |
|---|---|---|
| Developer | Insomniac Games | WP, MC, GF |
| Publisher | Sony Computer Entertainment America | GF (SCEA), MC |
| Release | 2004 (year only) | Day is disputed: WP and R&C wiki say 2004-11-02, GF and MC say 2004-11-03, GB shows both. Year is certain |
| Players | 4 | GF (1-4 local, 8 online), R&C wiki (up to four-player split screen) |
| Vmode | ntsc | SCUS serial, DISC VMODE = NTSC |
| Aspect / Scan | w / 480p | ADM (16:9 vert-, 480p yes), DISC (options "16:9 (WIDESCREEN)", "PROGRESSIVE SCAN") |
| Rating | 5 (Metascore 91) | MC |

## SCPS_150.13 Poinie's Poin (Japan: POINIE'S POIN)

GF https://gamefaqs.gamespot.com/ps2/475153-poinies-poin/data , JA WP https://ja.wikipedia.org/wiki/%E3%83%9D%E3%82%A4%E3%83%8B%E3%83%BC%E3%83%9D%E3%82%A4%E3%83%B3 , GAME Watch https://game.watch.impress.co.jp/docs/20020903/poi.htm

| Field | Value | Source |
|---|---|---|
| Title | Poinie's Poin | GF, cover title POINIE'S POIN (Japanese title is katakana, not ASCII) |
| Developer | Alvion | JA WP, GF |
| Publisher | Sony Computer Entertainment | JA WP, GF (SCEI), GAME Watch |
| Release | 2002-09-26 | GF (SCPS-15013), GAME Watch announcement (Sept 26 release). JA WP infobox says 2002-02-26, which contradicts its own Sept 2002 citations and looks like a typo |
| Players | 1 | JA WP (1 player), GF |
| Vmode | ntsc | SCPS serial, DISC VMODE = NTSC |
| Aspect, Scan | omitted | No source found; disc text is packed so menus could not be checked |
| Rating | omitted | No Metacritic page (metacritic.com/game/poinies-poin returns 410 Gone) |

## SLUS_202.14 State of Emergency

MC https://www.metacritic.com/game/state-of-emergency/ , GF https://gamefaqs.gamespot.com/ps2/478094-state-of-emergency/data , WP https://en.wikipedia.org/wiki/State_of_Emergency_(video_game) , GB https://giantbomb.com/wiki/Games/State_of_Emergency , Game Developer (VIS port write-up) https://www.gamedeveloper.com/production/porting-a-ps2centric-game-to-the-xbox-a-case-study-of-state-of-emergency

| Field | Value | Source |
|---|---|---|
| Developer | VIS Entertainment | WP, MC, GF |
| Publisher | Rockstar Games | WP, GF (US row), MC |
| Release | 2002-02-12 | WP, GF (SLUS-20214), MC, GB |
| Players | 1 | GF (PS2: 1 player; Xbox: 1-4), Game Developer article (PS2 was single-player only, multiplayer added for Xbox) |
| Vmode | ntsc | SLUS serial, DISC VMODE = NTSC |
| Aspect | w | DISC: options menu text "video: widescreen" (not on ADM, which is incomplete) |
| Scan | 480i | DISC: the video options hold only the widescreen toggle, no progressive text on disc; not on ADM |
| Rating | 3 (Metascore 71) | MC |

## SLUS_216.33 Aqua Teen Hunger Force Zombie Ninja Pro-Am

MC https://www.metacritic.com/game/aqua-teen-hunger-force-zombie-ninja-pro-am/ , GF https://gamefaqs.gamespot.com/ps2/938725-aqua-teen-hunger-force-zombie-ninja-pro-am/data , WP https://en.wikipedia.org/wiki/Aqua_Teen_Hunger_Force_Zombie_Ninja_Pro-Am , Gaming Nexus review https://www.gamingnexus.com/Article/1731/Aqua-Teen-Hunger-Force-Zombie-Ninja-Pro-Am

| Field | Value | Source |
|---|---|---|
| Developer | Creat Studios | WP, MC, GF |
| Publisher | Midway | WP (Midway Games), GF, MC |
| Release | 2007-11-05 | WP, GF (SLUS-21633), MC |
| Players | 2 | GF (1-2 local), Gaming Nexus (two-player golf), DISC (score screen has only Player 1 and Player 2 labels) |
| Vmode | ntsc | SLUS serial, DISC VMODE = NTSC |
| Aspect / Scan | s / 480i | DISC: the options table in the game scripts holds only voice, music and effect volume plus vibration; not on ADM |
| Rating | 1 (Metascore 37) | MC |

## SLUS_212.30 We Love Katamari

MC https://www.metacritic.com/game/we-love-katamari/ , GF https://gamefaqs.gamespot.com/ps2/921111-we-love-katamari/data , WP https://en.wikipedia.org/wiki/We_Love_Katamari , GB https://giantbomb.com/wiki/Games/We_Love_Katamari

| Field | Value | Source |
|---|---|---|
| Developer | Namco & Now Production | WP and GB credit Namco; MC and GF credit Now Production |
| Publisher | Namco Hometek | WP (NA publisher); GF and MC say Namco |
| Release | 2005-09-20 | WP, GF (SLUS-21230), MC |
| Players | 2 | GF (1-2), WP (two-player co-op and versus) |
| Vmode | ntsc | SLUS serial, DISC VMODE = NTSC |
| Rating | 4 (Metascore 86) | MC |
| Aspect, Scan | omitted | Same as Katamari Damacy: not on ADM, community widescreen hack exists, but no direct confirmation either way |
