# BIBLE, as RIPPS2 installs it

From build 134 these files are **BIBLE**, akilluminati47's boot loader built on **PS2BBL (PlayStation 2 Basic
BootLoader) by El Isra (israpps)** and saildot4k's PS2BBL Extended: its splash, its keys pages and its HD modes, from
[github.com/akilluminati47/BIBLE](https://github.com/akilluminati47/BIBLE). Every build here was **signed by
akilluminati47**, with kelftool on their own PC (build 133 and earlier carried El Isra's own PS2BBL 1.2.0 builds,
unchanged). Build 143 carries BIBLE at commit `f5705eb`, signed 2026-11-04:

| File here | BIBLE build | SHA-256 |
|---|---|---|
| `SYSTEM.XLF` | `PS2` (memory card KELF) | `0b251edcf67cf1ff7c9dd4bc7c420e5a33aa7415ecc69d5a9e4da9b13a7e4f52` |
| `MX4SIO/SYSTEM.XLF` | `PS2_MX4SIO` (memory card KELF; also reads `mx4sio:/` in slot 2) | `bb927d630e27c4ab00080471bba9d0cce8691dbc3c768ca9209a2d5ef861fef8` |
| `MMCE/SYSTEM.XLF` | `PS2_MMCE` (memory card KELF; also reads `mmce0:/` and `mmce1:/`, an SD2PSX or MemCard PRO 2) | `6a0e8364cec382c8cdd6da580de1f82a21edebc0ba1738a13b800c83b9d6e216` |
| `HSYSTEM.XLF` | `PS2_HDD` (for the HDD's boot area) | `304f78ce6b772a70820d6f0c1c89116b469db5345e79c53136e3c0cc8d339e9c` |
| `bible.icn`, `icon.sys` | BIBLE's card icon and the colours and light it was checked under, from BIBLE's `assets/icon` (commit `c1e950c`) | |
| `LICENSE.TXT` | GNU General Public License v3 | |

- **Build 143 (BIBLE `f5705eb`):** a missing file on an AUTO path, on a drive BIBLE has to load a driver for, no longer stops
  the boot on the splash (`301de13`): BIBLE moves on to the next path. BIBLE no longer reads `boot.adp` into memory: it only
  tells RIPPS2 the folder, and RIPPS2 reads it (BIBLE's `docs/boot-sound-handoff.md` has the lab's numbers). The stage 2
  loader is out of the MMCE, MX4SIO and HDD builds, about 9.6 KB each. BIBLE's folders wear BIBLE's own icon.
- **Build 139 (BIBLE `3282396`):** `BIBLE_BACKGROUND` (AUTO: RIPPS2's sky when RIPPS2's settings are found, else black;
  SKY; BLANK), RIPPS2's settings also read from `mc?:/RIPPS2` when AUTO starts RIPPS2 from an SD2PSX, USB or the HDD,
  RIPPS2 first in AUTO, and the boot sound read during the splash and handed to RIPPS2 in RAM. RIPPS2's Manage opens a
  BIBLE menu that sets these keys. Manage now calls this build older and offers the update, and RIPPS2 still takes the RAM
  copy from a card bound with it.
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

Many consoles from ROM 2.30 on no longer run system updates, so a bound BIBLE may not start there at power on: Manage says so
on those ROMs and still lets you try. BIBLE also comes as a plain, unsigned ELF on its releases page, for OpenTuna or FunTuna
to start from `mc?:/BOOT/BOOT.ELF`. RIPPS2 does not carry or install that one; Manage recognises it by its size and CRC-32,
so its settings rows work.

Everything PS2BBL does is El Isra's work, and PS2BBL Extended's is saildot4k's. Thank you.
