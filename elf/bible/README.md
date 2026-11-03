# BIBLE, as RIPPS2 installs it

From build 134 these files are **BIBLE**, akilluminati47's boot loader built on **PS2BBL (PlayStation 2 Basic
BootLoader) by El Isra (israpps)** and saildot4k's PS2BBL Extended: its splash, its keys pages and its HD modes, from
[github.com/akilluminati47/BIBLE](https://github.com/akilluminati47/BIBLE) at commit `f31c8d5`, signed for RIPPS2
on 2026-11-02 by akilluminati47 (build 138: the MMCE and MX4SIO builds from commit `a1ffb0b`, signed 2026-11-03, see
below; build 133 and earlier carried El Isra's own PS2BBL 1.2.0
builds, unchanged):

| File here | BIBLE build | SHA-256 |
|---|---|---|
| `SYSTEM.XLF` | `PS2` (memory card KELF) | `1a27175c3bcdba8209a0a8bf8ddb32e6bfb9773754ac642c9d82f67fd8f3ec36` |
| `MX4SIO/SYSTEM.XLF` | `PS2_MX4SIO` at `a1ffb0b` (memory card KELF; also reads `mx4sio:/` in slot 2) | `c961a8ff2b666b36aae246f9f6cfac5ebd26161dbdfd90eb04cb83a18ffba018` |
| `MMCE/SYSTEM.XLF` | `PS2_MMCE` at `a1ffb0b` (memory card KELF; also reads `mmce0:/` and `mmce1:/`, an SD2PSX or MemCard PRO 2) | `cacf865b196d4ee91e322152ae0d76107b56112c3e226c1c1918703641e269bb` |
| `HSYSTEM.XLF` | `PS2_HDD` (for the HDD's boot area) | `95d0756f8dc66e557c6a727314178c29a248749a7b143580ba8d887c9b138407` |
| `LICENSE.TXT` | GNU General Public License v3 | |

- **Build 138:** the MMCE and MX4SIO builds that builds 134 to 137 carried (`f31c8d5`) stopped on a black screen at power
  on: their own memory card driver did not link on the console (an IOP link error), so they waited for the memory card
  service forever. BIBLE `a1ffb0b` loads RIPPS2's memory card and pad drivers instead; signed again on 2026-11-03, the
  MMCE build was bound to an SD2PSX BOOT card (by KELFBinder) and started RIPPS2 on a real PS2 at power on.
- Source: https://github.com/akilluminati47/BIBLE/tree/f31c8d5, built on
  https://github.com/israpps/PlayStation2-Basic-BootLoader (GPL-3)
- The signed files are also on BIBLE's releases page.
- A signature is proven only when a console binds the file; the first console binds of these were still to come when
  they went in (build 134). If a bind is refused, RIPPS2 puts the card back as it was.

RIPPS2 carries them as data, inside RIPPS2.elf, and writes them to a memory card, or `HSYSTEM.XLF` to the internal
HDD's boot area, when you choose **Settings > General > Boot Loader > Manage**. BIBLE reads its config from
`mc?:/SYS-CONF/PS2BBL.INI` (PS2BBL Extended's place; PS2BBL 1.2.0 read `PS2BBL/CONFIG.INI`), so the install writes
it there, waiting 0 ms for a button and starting RIPPS2 first, with BOOT LOCK on.
The HDD install follows the FHDB / OSDMenu MBR steps: the old boot program is read out and kept in
`hdd0:__sysconf/RIPPS2/MBR-BACKUP.KELF` (Manage > Restore puts it back), HSYSTEM.XLF goes at sector
0x2000 of `__mbr`, the `__mbr` header is pointed at it, and the console's HDD boot setting is turned on.
RIPPS2's APA driver allows only those writes: the partition table stays fenced. RIPPS2 does not run them and contains
none of their code. On the card, the console's MechaCon binds the file to that card (the standard way a system update
is installed); RIPPS2 uses ps2sdk's open SECRMAN for that step and holds no keys.

Everything PS2BBL does is El Isra's work, and PS2BBL Extended's is saildot4k's. Thank you.
