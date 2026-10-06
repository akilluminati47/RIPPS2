# Handoff: build 80 (cloud session, 2026-10-06) to the local session

The cloud session got build 80 done, the theme pack, the dead-elf mark and the elf shelf on the
website. It **can't** create GitHub releases, post to Discord, capture reels, or test on a PS2. Those
are below for you, in order.

## Where things stand

- **RIPPS2** (this repo, `main`):
  - **Builds 78, 79 and 80 are pushed.** CI is green on build 80 (`10384a7`): the ELF build plus 43 host tests.
  - **Patch series:** RiptOPL `65d4b89` + `elf/patches/0050...0080`. `tools/dev/regen_patch.sh` refolds the last patch from your RiptOPL clone.
  - **Release prep:** `9b3d9d0` added the dead-elf mark, the README for build 80 ("Kill it: build 80", "Since the build 66 reel"), and the release and Discord notes.
  - **Website:** `14a7a64` and `ca88e9f` changed the web mockup. It lands on **Storage**, which now shows the **elf shelf** (`elfshelf.js`). GitHub Pages deploys from `main`.
- **RIPPS2-themes** (github.com/akilluminati47/RIPPS2-themes, `main`): Adapt, Adapt Rx and RIPgrid for build 80. The repo also holds the kit: `tools/check_theme.py`, `tools/preview_theme.py`, `tools/gen_adapt_family.py` (it writes all three configs), `docs/THEME_KEYS.md` and `AGENTS.md`.
- **Neutrino / iLink research** for FifthFox: `docs/plans/neutrino-ilink-logo.md`.

## To do locally, in order

### 1. Releases (the cloud session gets HTTP 403 on these)

**RIPPS2:**
- Tag `v0.0.80-alpha` on `main`, with the title "Kill it: RIPPS2 build 80 (alpha)".
- Body: `tools/discord/notes/release80.md`.
- Attach the ELF as exactly `RIPPS2.elf`; the README's download link points at that name.
- Get the ELF from the "Build RIPPS2.elf" CI run for `10384a7` (or any later green run), or build it with `elf/build.sh`.

**RIPPS2-themes:**
- Tag `v80`, with the title "RIPPS2 themes for build 80".
- Attach `RIPPS2-themes-build80.zip`, made from `themes/`: `cd themes && zip -r ../RIPPS2-themes-build80.zip thm_* README.md`.
- Body, in brief: unzip into `THM`; pick a theme in Settings > Interface > Theme or hold SELECT for 4.2 s; Adapt / Adapt Rx and RIPgrid as in the README; delete any old `thm_RIPgrid Rx`; needs build 80.

### 2. Discord post (the webhook hook)

- **Rotate the webhook first.** Its URL was pasted into an earlier chat, so treat it as exposed: make a new one in Discord and keep it out of every file.
- **Then run:**
  `RIPPS2_DISCORD_WEBHOOK=<new url> python tools/discord/make_test_embed.py --build 80 --notes tools/discord/notes/build80.md --release https://github.com/akilluminati47/RIPPS2/releases/tag/v0.0.80-alpha --attach RIPPS2.elf RIPPS2-themes-build80.zip --post`
- **What the script builds:** the banner (`test-me-80.png`, with the dead elf beside "Test me | Build 80") and the author icon (`ripps2-icon.png`, the dead elf on a dark tile). Audio Studio keeps its own bar icon.
- **Webhook avatar:** set it in Discord to `assets/ripps2-deadelf.png` (or `media/ripps2-deadelf-256.png`) so every post wears the mark.

### 3. The build 80 reel

- **Use your local reel script** (it was never committed) and follow **`media/REEL-build80.md`**: 10 beats, same capture, music bed and title cards as the build 66 reel.
- **Must-have beat:** in Colors and More, step the Color Theme RIPPS2 > Ember > Blood > Ectoplasm > Amethyst > Bone with the towers in view, then **back to RIPPS2 blue** before leaving the page.
- **Title-card art:** the dead-elf renders are in `assets/` and `media/deadelf/` (main, low, top, blue hat, gold rim; SVG in `assets/ripps2-deadelf.svg`). Re-render any angle with `media/deadelf/scene.html` (usage in its header comment).
- **After uploading,** update README lines 9-11: point "Watch the build 66 reel" and the poster image (`media/ripps2-b66-poster.png`) at the build 80 reel and a new `media/ripps2-b80-poster.png`.

### 4. README and website check

- With the releases up, confirm every README link resolves: download, theme pack, what's new, Discord invite (good for October 2026).
- **Open akilluminati47.github.io/RIPPS2 on a real GPU and a phone.** The cloud session only saw it in a software renderer. Check:
  - **Storage on load:** the plank, three hats in their puddles, and the caption showing the theme name.
  - **Middle hat:** it turns toward the pointer (faster the nearer the pointer is), and moving the pointer up and down lifts and drops its tip on a spring.
  - **Cycling:** a click or tap on a neighbour, or on the shelf beside the middle hat, or Left / Right, brings that hat to the middle.
  - **Launch Disc** still shows the console and blasts the towers; a click on a hat must not blast them.
  - **A faint dark speckle at the green hat's tip** was seen in the software render. If it shows on a GPU, raise `key.shadow.normalBias` or lower `bumpScale` further in `elfshelf.js`.
  - **Frame rate** on phones: the pixel ratio is capped at 1.75.
- `vendor/addons/objects/Reflector.js` is vendored but not used yet. It could give the puddles true reflections on desktop, as the icon render has, if performance allows.

### 5. Hardware testing (build 80 test list in `tools/discord/notes/build80.md`)

**Areas still unconfirmed on hardware:**
- SELECT hold-to-cycle;
- Adapt on 4:3 and 16:9, with the case reflection and the one-plane info tilt;
- RIPgrid: Circle cycles sources, and only the chosen cover tilts;
- START > STATUS: detection and installs;
- Achievements > Your account (counts fill in only from build 80 checks onward);
- Source Name Pop In;
- the Network page.

**Open asks to testers:**
- A **photo of the Network page "big gap"**. The cloud session couldn't find its cause in the dialog layout (hidden rows take no height). It added a RIPPS2 header and a blank row before OK, and moved the RA switches to Achievements.
- **FifthFox:** confirm whether the logo theory is "logo before the mode arguments" or "after the compatibility modes" (the 10-02 notes say after). Then run the A/B test in the plan.

### 6. Next code work, if you want it

- **Patch 0081:** a per-game Neutrino "Launch Arguments" preview, plus `-logo` emitted first. The steps, files, risks and host test are in `docs/plans/neutrino-ilink-logo.md`.
- **STATUS gaps:**
  - Ember installs only to `mass0:/EMBER`.
  - POPSTARTER installs only to `mass0:/POPS`, so no HDD (`pfs0:`) or MMCE targets yet.
  - Neutrino detection doesn't look on HDD or MMCE.
- **YOUR ACCOUNT** shows only what CHECK GAME SUPPORT has saved (`RA/<serial>.inf`). A real account view, with profile, points and recent unlocks, needs a new request in xeRAbora on the PC side; the console's protocol (`src/ranet.c`, RAP1/RAQ1/RAG1) has none.

## House rules (as used all along)

- **Each build is its own commit on `main`**, as akilluminati47 <acaradimos@gmail.com>, ending with the `Co-Authored-By` / `Claude-Session` trailers. No model names anywhere else in the repo.
- **Never write the Discord webhook into a file.**
- **Theme configs** come from `tools/gen_adapt_family.py` (in RIPPS2-themes); run the checker and previewer before calling a theme done.
- **New engine keys** go in `docs/THEME_KEYS.md` there with the build they landed in.
- **Host tests:**
  - Run with `python elf/tests/run_host_tests.py <patched riptopl dir>`, or use `elf/build.sh --prepare-only` first.
  - New RIPPS2 tests go in `elf/tests/test_ripps2_*.py`.
  - CI fails on a new warning in `src/ripps2*.c`.
