# RIPPS2 Audio Studio

A small PC app that makes an `AUDIO` folder for RIPPS2: your own sounds and music, in the formats the PS2 plays.

- **Browse** to any sound or song (WAV, FLAC, Ogg, MP3 and more). Play it as it is, or as the PS2 will play it (mono SPU2 ADPCM at 44.1 kHz), before you convert it.
- **Convert** it into one of RIPPS2's sounds (RiptOPL's `boot`, `cursor`, `confirm`, `cancel`, `message`, `transition`, `bd_connect`, `bd_disconnect`, then RIPPS2's `page_in`, `page_out`, `error`, `save`, `launch`, `disc`, `random`) or into a music track. Start converts a whole folder: files named for an event become that sound, long ones become music.
- **Your BIOS:** pick the BIOS dump of your own PS2 (the file PCSX2 uses) and the app renders the console's own menu sounds and system music from it, the way its sound chip plays them: the boot, the tower tunnel, the PS2 logo, the clock and the ambient music. Start rips the lot into a full AUDIO folder. Nothing from any BIOS ships with RIPPS2 or this app; it reads only the dump you give it, on your PC.

Everything lands in `output/AUDIO` beside the app. Copy that folder to a USB stick, then in RIPPS2's **Memory Files** copy it beside `RIPPS2.ELF`. Settings > Audio Settings > Music picks the track.

The AUDIO FOLDER tab shows how much of the PS2's sound RAM your sounds use: RIPPS2 loads every sound into the SPU2's 2 MB at once (the music streams, so it does not count).

## Run it

- **Windows app:** `RIPPS2 Audio Studio.exe`, no install. Put `ffmpeg.exe` beside it to read more formats and to write Ogg music (without it, music is written as WAV, which RIPPS2 also plays).
- **From source:** Python 3.10 or newer, then `pip install -r requirements.txt` and `python studio.py` (or double-click `run_studio.bat`).

Controls: arrows move, Enter opens or converts, Backspace goes back, Space plays, P plays the PS2 version, Tab (or Q / E) switches tabs, S converts a folder or rips a BIOS, O opens the output folder. The mouse works (double-click), and so does a gamepad: Cross, Circle, Square, Triangle, L1 / R1, Start.

## Files

- `studio.py`: the app (pygame).
- `adpcm.py`: the `.adp` encoder and decoder (the same as `elf/theme/tools/make_adp.py`).
- `audio_io.py`: reading audio, writing `.adp` and music.
- `ps2bios.py`: reads a PS2 BIOS dump's sound image (its ROM directory, the BIOS's LZ compression, the SSHD sound banks and SSSQ sequences) and renders them with an SPU2 voice model (ADPCM, the ADSR envelope, pitch, pan, noise). `python ps2bios.py <bios.bin> <folder>` writes every menu sound as a WAV.
- `test_studio.py`: drives the app off screen and checks its output.
- `build_exe.bat`: builds the Windows app with PyInstaller.
