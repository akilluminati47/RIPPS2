## BIBLE f5705eb, signed by akilluminati47: no more hang on a missing AUTO path, and it no longer reads the boot sound

BIBLE is akilluminati47's boot loader, built on [PS2BBL](https://github.com/israpps/PlayStation2-Basic-BootLoader) by El Isra and [PS2BBL Extended](https://github.com/saildot4k/PlayStation2-Basic-BootLoader-Extended) by saildot4k (GPL-3). **All four builds here were signed by akilluminati47** on 11/04, with kelftool on their own PC.

**Using RIPPS2? You do not need the signed files from this page.** [RIPPS2 v1.4.3-beta](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.4.3-beta) carries them inside RIPPS2.elf. With BIBLE on a card, **Settings > General > Boot Loader > Manage** offers the update.

**This has only run in the PCSX2 lab, not on a real PS2 yet.**

### What is new since `signed-3282396`
- **The AUTO hang is fixed.** A missing file on an AUTO path, on a drive BIBLE has to load a driver for (USB, MMCE, MX4SIO, HDD), stopped the boot on the splash for good: no words, the clock stopped, the buttons dead. BIBLE moves on to the next path now. **Every card on 3282396 keeps the hang until it is updated.** If nothing on the list starts, BIBLE shows NO VALID PATH FOUND FOR AUTO and waits for you, as it always has.
- **BIBLE no longer reads `boot.adp` into memory.** It only tells RIPPS2 the folder (`-bible-home=`), and RIPPS2 reads the sound itself. The read never reached RIPPS2 on an SD2PSX, and on a memory card launch it only moved the wait into BIBLE. RIPPS2 still takes the copy from a card on an older BIBLE. [The numbers and the reasons](https://github.com/akilluminati47/BIBLE/blob/main/docs/boot-sound-handoff.md).
- **The stage 2 loader is out** of the MMCE, MX4SIO and HDD builds, about 9.6 KB each.
- **Its own icon:** its logo and an open book on a dark plate, one shape, `assets/icon`.
- **A plain ELF**, for consoles with no system update.

### Which file
| You have | Use |
|---|---|
| RIPPS2 | Nothing from here: Manage does it |
| A console that can bind, and another installer | `BIBLE-signed-f5705eb.zip` |
| A late slim with no system update (many from ROM 2.30 on), and OpenTuna or FunTuna | `BIBLE-ELF-f5705eb.zip`, unsigned, with its own README: it goes in `mc?:/BOOT/BOOT.ELF` |

### Tested
| What | Where | Result |
|---|---|---|
| Signing | akilluminati47's PC, kelftool (memory card builds: dnasload, HDD build: fhdb) | All four signed on 11/04. Each is its plain ELF plus 148 bytes |
| AUTO with `mmce?:/APPS/RIPPS2.ELF` and no device | PCSX2, MMCE build | Moves on to the next path in about 2 s. 3282396 stayed on the splash |
| Start to RIPPS2's towers, 0 ms, no splash (`LOGO_DISPLAY = 0`) | PCSX2, MMCE build, a 367,904-byte `boot.adp` | Three runs each: 4.73 to 5.16 s before, 3.95 to 4.31 s after, the sound 0.14 s after the towers (0.13 s before) |
| The memory card, MX4SIO and HDD builds | PCSX2, RIPPS2 on a memory card | Start RIPPS2, the home passed, the sound played |
| The plain ELF through the real OpenTuna exploit | PCSX2, ROM 2.20A, all four builds | Started by the exploit. MMCE and MX4SIO went on to RIPPS2, MMCE and memory card to BOOT2.ELF, the HDD build got past its splash |
| The icon | PCSX2 browser on ROM 1.60A and 2.20A, RIPPS2's Memory Files viewer | Right in all three |
| **A bind of this build, a real MMCE, USB, MX4SIO or HDD with a missing file, ROM 2.30, FunTuna** | | **Not run yet** |

The only console report on this line is one SCPH-90004 on ROM 2.30E, on an earlier test build of the plain ELF.

### The files
| File | Build | SHA-256 |
|---|---|---|
| `SYSTEM.XLF` | memory card (memory cards, USB) | `0b251edcf67cf1ff7c9dd4bc7c420e5a33aa7415ecc69d5a9e4da9b13a7e4f52` |
| `MX4SIO/SYSTEM.XLF` | memory card, also reads MX4SIO | `bb927d630e27c4ab00080471bba9d0cce8691dbc3c768ca9209a2d5ef861fef8` |
| `MMCE/SYSTEM.XLF` | memory card, also reads MMCE (SD2PSX, MemCard PRO 2) | `6a0e8364cec382c8cdd6da580de1f82a21edebc0ba1738a13b800c83b9d6e216` |
| `HSYSTEM.XLF` | the internal HDD's boot area | `304f78ce6b772a70820d6f0c1c89116b469db5345e79c53136e3c0cc8d339e9c` |

A memory card KELF only starts once a console has bound it to that card (RIPPS2's Manage or KELFBinder do this as they install it); copying the file onto a card by hand does not make it boot.

The tag is at the commit these were built from, `f5705eb`. `main` adds only the icon, its tools and documents. Source and licence: this repository (GPL-3).
