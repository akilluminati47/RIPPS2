# Build 135: Neutrino found, never carried (plan, 2026-11-02; built 11/02 as build 135)

What is left of the 11/02 lite-only plan after build 134. The user (11/02): "we move lite to the main release flow and
drop bundling in bbl 1.20 and neutrino files from now on just do smart detection for the boot lock write ... remove the
neutrino injection so its more like launcHer style handshake/detection only ... keep their credit etc."

## What build 134 already settled (v1.3.4-beta, 11/02)

- The boot loader half went the other way, on the user's word ("the real use case is the manage loader feature
  actually writing the kelf into memory card and it boots through it to ripps2"): Boot Loader > Manage stays and now
  installs the signed BIBLE (elf/bible, BIBLE release signed-f31c8d5), and writes its config to mc?:/SYS-CONF/PS2BBL.INI
  (the HDD install's card config too), where BIBLE reads it. PS2BBL 1.2.0 is no longer carried; "BBL 1.20" became BIBLE
  in all 32 languages.
- So the old points 2, 3 (Manage removed, no install), the Restore question and "BIBLE is now just BOOT LOCK" are void.
- Still open from 134: the first console binds of the signed BIBLE (KELFBinder kit in BIBLE-to-sign/kelfbinder-test,
  then Manage on a spare card). Nothing says "working" until one passes.

## The change (one build, from then-current main)

1. **Neutrino found, never installed.** RIPPS2 looks for it where it does now (custom path, the game's drive, mc0/mc1,
   the drive search); when none is found it says where to put the `neutrino` folder (and the link) instead of
   `ripps2NeutrinoOffer` installing the carried copy. The STATUS install row (`stInstallNeutrino`) goes; STATUS keeps
   showing where Neutrino was found.
2. **The ELF stops carrying Neutrino.** `neutrino_tgz.o` leaves the full build; `elf/neutrino` keeps a short README
   (what RIPPS2 works with, where to get it), the binaries leave the tree (history keeps them).
3. **Words.** About, README (and its 32 languages), CHANGELOG and release notes say Neutrino is found, not carried.
   Credits stay: rickgaiser's Neutrino, ORBIT's fork, El Isra's PS2BBL, saildot4k's PS2BBL Extended. Changed on-screen
   lines get all 32 translations.

## Open questions for the user

- **The lite ELF.** With BIBLE inside the full ELF and Neutrino gone, lite differs only by BIBLE. Keep shipping
  RIPPS2-lite.elf (no BIBLE) next to RIPPS2.elf, or one ELF only?
- **Whether to do this at all now**, or wait for the first BIBLE console binds.

## Lab

A Neutrino game with Neutrino on mc0, on the game's drive, and with none (the message); STATUS; About pages; the ELF
size. Then CI (build + host tests: test_ripps2_build91's dialog id check, anything naming `RIPPS2_LITE`), push to main.
Release and Discord only on the user's word.

## Decided (11/02)

The user: "go", then "the lite only keeps bible injections not neutrino so users provide their own, no more lite tag just
the one ripps2 with bible". Built as patch 0135: one RIPPS2.elf (BIBLE carried, Neutrino found), no lite ELF.
