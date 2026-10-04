# BIBLE: PS2BBL 1.2.0, as RIPPS2 installs it

These files are **PS2BBL (PlayStation 2 Basic BootLoader) v1.2.0 by El Isra (israpps)**, unchanged.
They are El Isra's signed builds, taken from the official v1.2.0 release:

| File here | In `PS2BBL_KELF-v1.2.0.7z` | SHA-256 |
|---|---|---|
| `SYSTEM.XLF` | `SYSTEM.XLF` (the memory card build) | `d53cf42e3c42220814b0bd8c934a6bf2bc9129e3f8ee20724b5532036a470435` |
| `MX4SIO/SYSTEM.XLF` | `MX4SIO/SYSTEM.XLF` (the build that also starts from MX4SIO) | `4f6bb1db8f8ea661e8acb5ee6aa9cb1e4a1fc7b783de232c4a82dfa8e678ee94` |
| `LICENSE.TXT` | `LICENSE.TXT` | |

- Release: https://github.com/israpps/PlayStation2-Basic-BootLoader/releases/tag/v1.2.0
- Source code (the commit these were built from, `a063bb3`): https://github.com/israpps/PlayStation2-Basic-BootLoader/tree/a063bb3
- Licence: GNU General Public License v3 (`LICENSE.TXT`)

RIPPS2 carries them as data, inside RIPPS2.elf, and writes them to a memory card when you choose
**Settings > General > Boot Loader > Manage**. RIPPS2 does not run them and contains none of their
code. On the card, the console's MechaCon binds the file to that card (the standard way a system
update is installed); RIPPS2 uses ps2sdk's open SECRMAN for that step and holds no keys.

"BIBLE" is only what RIPPS2 calls this setup: PS2BBL 1.2.0 with a config that waits 0 ms for a
button and starts RIPPS2 first. Everything PS2BBL does is El Isra's work. Thank you.
