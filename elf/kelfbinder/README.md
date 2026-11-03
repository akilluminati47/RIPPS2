# KELFBinder's IOPRP image, as RIPPS2 binds BIBLE with it

From build 138, **Settings > General > Boot Loader > Manage** binds BIBLE to a memory card with the IOP image
**KELFBinder** by El Isra (israpps) boots for its own installs, unchanged:

| File here | What it is | SHA-256 |
|---|---|---|
| `IOPRP.img` | KELFBinder's `iop/IOPRP.img` (15,741 bytes): an IOPRP image holding one module, `SECRMAN` = `secrman_special` version 0x0104, built 2018-06-14 | `7d814c36d9ef83cb1a28a5fa38f046474cfcc7b8429b20cf438c0a082ecbeb54` |
| `LICENSE.TXT` | GNU General Public License v3, KELFBinder's licence | |

- Source: https://github.com/israpps/KELFBinder (`iop/IOPRP.img`, first public release `f9dda8f`, 2023-01-29; checked
  against `a699f02`).
- RIPPS2 carries it as data inside RIPPS2.elf and hands it to the IOP's reboot as it is; RIPPS2 contains none of
  KELFBinder's code.

**Why:** on 2026-11-03 the user's SD2PSX (on a USA PS2) would not log in after RIPPS2's own reboot for the bind
(DIAG.TXT: "card login after the restart: not ready, not ready"), with only the memory card drivers loaded. That reboot
used ps2sdk's later rewrite of `secrman_special` in an image RIPPS2 built at run time. KELFBinder, booting this image,
bound BIBLE to the same card that night. So RIPPS2's bind now boots the same image, and the card, the console and the
module are the ones that already worked together.
