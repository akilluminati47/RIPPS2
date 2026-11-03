# BIBLE, as RIPPS2 installs it

From build 134 these files are **BIBLE**, akilluminati47's boot loader built on **PS2BBL (PlayStation 2 Basic
BootLoader) by El Isra (israpps)** and saildot4k's PS2BBL Extended: its splash, its keys pages and its HD modes, from
[github.com/akilluminati47/BIBLE](https://github.com/akilluminati47/BIBLE). Every build here was **signed by
akilluminati47**, with kelftool on their own PC (build 133 and earlier carried El Isra's own PS2BBL 1.2.0 builds,
unchanged). Build 139 carries BIBLE at commit `3282396`, signed 2026-11-03:

| File here | BIBLE build | SHA-256 |
|---|---|---|
| `SYSTEM.XLF` | `PS2` (memory card KELF) | `f56c950f753c78b862ce5c0a6d3578e9850e1eefc1285d4a3ef560f27c457a8a` |
| `MX4SIO/SYSTEM.XLF` | `PS2_MX4SIO` (memory card KELF; also reads `mx4sio:/` in slot 2) | `9f11f1d461e668d1a35179340b332aa446aa188932596618201dd750770f47f2` |
| `MMCE/SYSTEM.XLF` | `PS2_MMCE` (memory card KELF; also reads `mmce0:/` and `mmce1:/`, an SD2PSX or MemCard PRO 2) | `cbcff26cf6900df479e43eb66a601294ba75029486d967c292687562d7bacf05` |
| `HSYSTEM.XLF` | `PS2_HDD` (for the HDD's boot area) | `0f8f2a7ca76d4f3392636b0a1263b62d9a155285cce40b3226ab7926af5cf2b8` |
| `LICENSE.TXT` | GNU General Public License v3 | |

- **Build 139 (BIBLE `3282396`):** `BIBLE_BACKGROUND` (AUTO: RIPPS2's sky when RIPPS2's settings are found, else black;
  SKY; BLANK), RIPPS2's settings also read from `mc?:/RIPPS2` when AUTO starts RIPPS2 from an SD2PSX, USB or the HDD,
  RIPPS2 first in AUTO, and the boot sound: `boot.adp` beside BIBLE's settings file, read during the splash and handed to
  RIPPS2 in RAM (the MMCE, MX4SIO and HDD builds; see BIBLE's `docs/boot-sound-handoff.md`). RIPPS2's Manage now opens a
  BIBLE menu that sets these keys.
- **Build 138 (BIBLE `a1ffb0b`):** the MMCE and MX4SIO builds that builds 134 to 137 carried (`f31c8d5`) stopped on a black
  screen at power on: their own memory card driver did not link on the console (an IOP link error). `a1ffb0b` loads
  RIPPS2's memory card and pad drivers instead; its MMCE build, bound to an SD2PSX BOOT card by KELFBinder and by RIPPS2
  1.3.8's Manage, started RIPPS2 on a real PS2 (SCPH-39001) at power on.
- Source: https://github.com/akilluminati47/BIBLE, built on https://github.com/israpps/PlayStation2-Basic-BootLoader (GPL-3)
- The signed files are also on BIBLE's releases page.
- A signature is proven only when a console binds the file. If a bind is refused, RIPPS2 puts the card back as it was.

RIPPS2 carries them as data, inside RIPPS2.elf, and writes them to a memory card, or `HSYSTEM.XLF` to the internal
HDD's boot area, when you choose **Settings > General > Boot Loader > Manage**. BIBLE reads its config from
`mc?:/SYS-CONF/PS2BBL.INI` (PS2BBL Extended's place; PS2BBL 1.2.0 read `PS2BBL/CONFIG.INI`), so the install writes
it there, waiting 0 ms for a button and starting RIPPS2 first, with BOOT LOCK on.
The HDD install follows the FHDB / OSDMenu MBR steps: the old boot program is read out and kept in
`hdd0:__sysconf/RIPPS2/MBR-BACKUP.KELF` (Manage > Restore puts it back), HSYSTEM.XLF goes at sector
0x2000 of `__mbr`, the `__mbr` header is pointed at it, and the console's HDD boot setting is turned on.
RIPPS2's APA driver allows only those writes: the partition table stays fenced. RIPPS2 does not run them and contains
none of their code. On the card, the console's MechaCon binds the file to that card (the standard way a system update
is installed); RIPPS2 boots KELFBinder's IOPRP image for that step (build 138, `elf/kelfbinder`) and holds no keys.

Everything PS2BBL does is El Isra's work, and PS2BBL Extended's is saildot4k's. Thank you.
