# Neutrino launch arguments and `-logo` order for iLink: research and plan (FifthFox's request)

Read-only research on the build 80 tree. Line numbers refer to the patched RiptOPL tree (`src/...`).

## Short answer
- **Neutrino almost certainly does not care where `-logo` sits.** It reads every option into variables first, then acts on them. Position only matters for a repeated key (the last one wins) and for anything after `--b` (which goes to the game, not Neutrino). No Neutrino source was available offline, so this comes from its README and from what upstream is known to do. RiptOPL's own comments say "last-wins" as well.
- **What `-logo` really changes is the boot.** ee_core starts `rom0:PS2LOGO` with the game as its argument. That adds a **second IOP reboot**, which re-initialises the iLink driver, a few seconds of logo, and early small reads that wake the drive. Any of these could explain the better iLink handshakes. Its position in the argument list almost certainly cannot.
- **A delay inside RIPPS2 would not help.** On iLink RIPPS2 passes `-qb`, so the first IOP reset after handoff is ee_core's, which happens after RIPPS2 has let go.
- **Check FifthFox's wording.** The earlier community notes (10-02) recorded the theory as "logo *after* the compatibility modes", which is what RIPPS2 already does. This request says "*before* the mode arguments". Ask which one FifthFox means.

## Where the arguments are built today
`sysRunNeutrinoLaunch()`, `src/system.c:1586-1862` (called from bdm / hdd / mmce / udpfs supports). Order:

1. neutrino.elf
2. `-bsd= [-bsdfs=] -dvd=` (APA: `-bsd=ata -bsdfs=hdl -dvd=hdl:`)
3. auto `-qb` (usb, ilink, udp*)
4. `-gc=`
5. `-dbc`
6. **auto `-logo`** (`:1743`). It follows the global PS2 Logo setting, is forced off on mmce and udp* (issue #56), but **not on iLink**.
7. `-gsm=`
8. auto `-elf=`
9. `-mc0= -mc1=`
10. `-cwd=`
11. the user's global then per-game arguments (a typed `-logo` lands **here** and replaces the automatic one)
12. `--b` + arguments for the game

Arguments beyond the budget (14 entries / 256 bytes) are **refused** now; nothing is silently dropped.

**Already there:** Game Launching > Neutrino Defaults > **Show Launch Arguments** (build 75). It shows the exact argument list before each launch ("Neutrino will start with these arguments. Launch?"). FifthFox can use it today.

## Plan (recommended order)
1. **Per-game "Launch Arguments" preview** (no hardware risk; answers request 1).
   - Add a button after "Neutrino Launch Args" in the per-game Compatibility dialog (`diaCompatConfig`, `src/dialogs.c:1209`). It is greyed when the game does not start through Neutrino, exactly like that button (`guiGameSetCoreAwareState`, `src/guigame.c:1157`). Its popup shows the full argument string.
   - Split the composer out of `sysRunNeutrinoLaunch` (`sysComposeNeutrinoArgv`), so that the preview and the real launch run **the same code** and can never differ.
   - Add an optional per-device callback that gathers the launch inputs. The preview uses the dialog's unsaved values and has **no side effects**: no install offer, no toml sync; on MMCE it says "logo if the disc has one".
2. **Emit `-logo` first** (right after `neutrino.elf`), unconditionally.
   - Exactly one `-logo` still goes out; the mmce/udp suppression stays; anything after `--b` still goes to the game; the byte count is unchanged.
   - Present it as matching NHDDL's order, not as a fix.
3. **Hardware A/B test with FifthFox:** PS2 Logo on vs off on iLink, the same game, N cold boots each, with a photo of the preview.
4. **Only if logo-on clearly wins:** an "always send `-logo` on iLink" option (a per-device override of PS2 Logo). That is the one RIPPS2 lever that acts after the reset.
5. **If iLink timing is confirmed,** raise it with Neutrino upstream (rickgaiser), for example a wait-for-device in `IEEE1394_bd_mini` or ee_core.

**Not recommended:**
- a `DelayThread` before the handoff: it runs before Neutrino's reset, with RIPPS2's iLink stack still live;
- per-game custom ordering: Neutrino ignores order, so it would be UI for no effect.

## Files (as patch 0084; build 81 went to the Pop In toast, 82 to HD text and the RIPgrid flip, 83 to Star and YOUR ACCOUNT)
- `src/system.c`, `include/system.h`: the composer, `sysNeutrinoFormatArgs`, the `-logo` move.
- `include/iosupport.h`: the callback.
- the bdm / hdd / mmce / udpfs supports, with fav / mix passing it through.
- `src/supportbase.c`: a quiet Neutrino path resolver.
- `src/guigame.c`, `src/dialogs.c`, `include/dialogs.h`, `lng_tmpl/_base.yml`.
- `docs/NEUTRINO.md`.
- RiptOPL's `.github/scripts/test_neutrino_argv_budget.py`: it expects the per-game `-logo` last, which step 2 changes, so update it.

## Risks
| Device | Risk |
|---|---|
| MMCE, UDPFS, UDPBD | The suppression must survive the move. |
| APA | Position change only. |
| USB, MX4SIO | Unaffected beyond position. |
| SMB | Has no Neutrino path; the button stays greyed. |
| All | Budget unchanged. |
| Preview | Must never prompt or write. |

## Host test
Add `elf/tests/test_ripps2_neutrino_logo_order.py`: compile the composer with stubs, as RiptOPL's argv-budget test does, and check:
- `-logo` is the first argument on usb / ilink;
- exactly one `-logo` with a global and a per-game one;
- `--b -logo` stays after `--b`;
- mmce / udp get no automatic `-logo`, but a typed one goes through;
- the APA order;
- byte and entry counts are unchanged;
- the preview string equals what the stubbed launch recorded.
