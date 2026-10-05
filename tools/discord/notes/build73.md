# Covers that fetch themselves, POPSTARTER on board, PS1 games from Memory Files, and BIBLE on the internal HDD. Real PS2s wanted: here is what to try.

## Cover Art (Settings > Network)
- **Download**, right after NBD Server: the PS2 fetches a cover for every PS2 game that has none (xlenore's ps2-covers, over HTTPS) into that drive's ART folder. Covers you have are never touched.
- Saved like OPL's art packs: 140x200, 256 colours, about 20 KB each.

## PS1 games
- **POPSTARTER is built in.** Your own copy always wins; only when there is none anywhere does RIPPS2 put its copy in the drive's POPS folder and start the game. Nothing is written over.
- **PS1 games start from Memory Files**: a .VCD in a drive's POPS folder shows as a disc. Cross plays it (USB and MMCE).

## BIBLE on the internal HDD
- **Boot Loader > Manage > Internal HDD**: PS2BBL 1.2.0's HDD build in the HDD's boot area, RIPPS2 copied to __sysconf, and the console set to boot its HDD. Fat PS2 + network adapter = straight into RIPPS2, no card needed.
- The HDD's old boot program is kept first; **Restore** in the same list puts it back.

## HDD Manager
- **Removing a partition works now** (it always said COULD NOT REMOVE). System partitions, RIPPS2's home and the one it started from still stay.

## Test list
- **Cover Art > Download** with games missing covers: how many came in? Photo of any error (it names the step).
- **A PS1 .VCD with no POPSTARTER anywhere**: does RIPPS2 put one in POPS and start the game?
- **Your own POPSTARTER set-up**: still starts exactly as before?
- **Memory Files > a drive > POPS > a .VCD**: Cross. Does it play?
- **PS1 games on the internal HDD** with no POPSTARTER in __common/POPS: does it install and start?
- **BIBLE on the internal HDD** (fat PS2 with network adapter, HDD you have backed up): install, power off, power on. Straight into RIPPS2?
- **Then Restore**: is your old HDD boot back?
- **HDD Manager** (Memory Files > HDD > Square): remove a partition you do not need. Gone, and the rest fine?
- **Ember games, .elf on the HDD, Show Recents, music during big loads**: anything worse than build 72?
- **Save Settings** after changes: saved after a power cycle?

## Report
Post here with your **console model**, where your games live (USB, HDD, MX4SIO, MMCE, iLink, network) and a **photo** of anything odd. For the HDD install, say what your HDD booted before (HDD-OSD, FHDB, OSDMenu, PSBBN, nothing).
