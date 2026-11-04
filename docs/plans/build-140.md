# Build 140: boot time and the rest of the BIBLE menu (plan, 2026-11-03)

Status: plan only. Nothing here is built. Base: v1.3.9-beta, BIBLE 3282396.

## Already done in 139 (the 11/03 spec reads as if it were not)

BIBLE's `docs/boot-sound-handoff.md` still calls the RIPPS2 side "a later build", but 139 shipped most of it:

- `ripps2BibleArgs` at the top of `main`, with the CRC and header checks
- On (fast) writing to `<gBibleHome>boot.adp`, and Off or On removing it
- the STATUS wording ("handed over by BIBLE")
- a BIBLE menu with Manage as one item, and in-place INI edits (`blIniSet`)

Build 140 finishes what is left and updates that doc.

## 1. DISC_STOP: the biggest win

Lab finding, not yet measured on a real PS2. BIBLE to RIPPS2 loaded in:

| Setup | Loaded |
|---|---|
| 0 ms wait, `DISC_STOP = 0` | 4.2 s |
| 0 ms wait, default `DISC_STOP = 1` | 7.5 s |
| 6000 ms wait, default | 10.2 s |

The cost is `sceCdStop(); sceCdSync(0);` in BIBLE `src/elf.c:1055`: it holds about 3.6 s while the drive is still
starting. RIPPS2 never writes the key today, so everyone gets the default.

RIPPS2 side (no re-sign needed):
- Add a `DISC_STOP` row to `blSets` (`ripps2boot.c:2042`): Off / On, default On, with the help text below.
- Help text says the trade: "Off starts RIPPS2 about 3 s sooner. A disc in the tray keeps spinning."
- Fresh installs: `blBibleConfig` writes a value (the user's decision, see the end).

BIBLE side (needs the user's re-sign, so a separate BIBLE release, not in 140):
- Issue the stop without waiting for it at launch, when the launch is not disc-bound. `main.c:102` has the same sync in
  `StopDiscAttemptOnce`, so check it too. Test that the IOP reset after a pending stop is safe first.

Check: the 4.2 s must be timed on the SCPH-39001, including whether a disc in the tray changes it.

## 2. The late boot sound

### The cause is probably not audio start-up

The earlier note blames RIPPS2's audio start-up. The code points elsewhere: `sfxBootStart` runs on the main thread at the
end of `init()`, and `main` reaches `guiIntroLoop` (first "the menu is up") only after that. So audsrv is already up
when that line is logged, and the 2.6 s comes after it.

What fits the code:
1. `sfxBootEarlyWork` runs first on the IO worker, while audio is not up, so it only marks `SFX_EARLY_READ`.
2. `applyConfig` queues the drive jobs and the worker starts one.
3. `sfxBootStart` queues the upload with `ioPutRequestFront`, which goes ahead of waiting jobs but cannot interrupt the
   running one.

That is a hypothesis until step A proves it.

### Steps

A. Timing first: add DIAG lines at audio up, upload queued, upload start, upload end, and first play. One lab run gives
   the split. Also log the name of the job the worker was running if that is cheap.

B. Fix, if A confirms it: when the sound is already in RAM, `sfxBootEarlyWork` waits for audio before it returns (a
   semaphore signalled by `sfxBootStart`, 3 s timeout), then uploads at once. The drive jobs behind it wait a moment.
   This also keeps the worker off the RPC client while `applyConfig` calls audsrv, the hang from builds 119 and 121. Risk: anything
   on the main thread that waits on the IO worker before `sfxBootStart` would hit the timeout, so look for those and log
   a timeout.

C. If A shows the upload itself is slow (`audsrv_load_adpcm`, 368 KB), look at the transfer instead.

Target: the sound within a few frames of the towers, lab first, then the console.

### The hand-off did not happen on the user's console

`D:\APPS\DIAG.TXT` (build 139, hardware) says: `started by BIBLE (mc0:/SYS-CONF/), no boot sound handed over`, then ready
at 7.83 s, 4.46 s after the menu line. The file's date is not reliable, so it may predate the `boot.adp` copy.

Check before anything else: was `boot.adp` in SYS-CONF for that boot, is the AUTO key's first entry RIPPS2, and which
BIBLE build is bound? The plain PS2 build passes only `-bible-home` by design, and a card bound from it never
hands over. The lab take D result does not cover this path.

## 3. Log fixes

- `sound.c:934`: the blank "from". When no AUDIO folder was used, say what it was: "from BIBLE's RAM copy", "from the card
  copy", "from the theme", or "no files". Also seen as `sounds: 0 loaded in 4 ms from ` in the 137 log.
- "boot: the menu is up" prints twice, from `gui.c:5963` and `gui.c:5999`. The first is really the towers starting, which
  is how the sound got measured against the wrong moment. Rename the first to "boot: the towers are up".
- STATUS boot sound row is too wide (139 note).

## 4. The rest of the BIBLE menu

From the spec, not yet in `blSets`:

- Sky colour (`BIBLE_COLOR`)
- Boot sound (the same three choices as Audio)
- Disc and history: `EJECT_TRAY`, `OSDHISTORY_READ`, `APP_GAMEID`, `CDROM_DISABLE_GAMEID`
- Launch keys: a page per button with `NAME_<KEY>`, `LK_<KEY>_E1` to `E10` picked with the Memory Files browser, and
  `ARG_<KEY>_E<n>`, plus the L2 + R2 note
- `KEY_READ_WAIT_TIME` help: the boot sound's cost at 0 ms
- Atomic write: the spec asks for a temporary file renamed over the old one; check that `blWrite` does this

Launch keys is the largest piece and could become 141 if 140 should stay about boot time.
New strings go through the 32 languages (as `lang139.py` did).

## 5. Housekeeping

- Copy `race/timeline.py` from the last session's scratchpad to `tools/dev/race/`: the race tools use it and scratch
  does not last. Keep `swap_discord.py` too if it will be used again.
- Update BIBLE's `docs/boot-sound-handoff.md`: what 139 shipped, and `DISC_STOP`.
- Add `elf/tests/test_ripps2_build140.py`, as earlier builds did.

## Order

1. Check the console hand-off question. 2. DISC_STOP row. 3. Log fixes. 4. Timing lines and a lab run. 5. The sound fix.
6. Menu rows. 7. Launch keys, or move them to 141. 8. Console test, then release when the user says.

## Decided

The user, 11/03: fresh BIBLE installs from Manage write `DISC_STOP = 0`, and Manage's BIBLE menu gets the row ("Stop Disc
at Launch", Off / On). Done in patch 0140 with all 32 languages; not compiled or run yet. A config already on a card is
kept, so existing installs use the row. The row has no help text: `blSets` has nowhere to show one yet.
