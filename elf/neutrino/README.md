# Neutrino (bundled)

**Neutrino** is a small, fast and modular PS2 device emulator by **rickgaiser**, licensed **AFL-3.0**
(`LICENSE.txt`, beside this file). Releases: <https://github.com/rickgaiser/neutrino/releases>

`neutrino-1.8.0.tar.gz` is the official `neutrino_v1.8.0.7z` (SHA-256 `17f760f9293d3cba6e9e3fbf601801d0784fe7048d16b4e68c3358aff589910a`) repacked, unmodified, as a
gzip'd ustar (594 KB of tar, 72 files, SHA-256 `201b7c8a6c95647eed2c8aa155b70e065eaecb634d6fdaa278dd89142c9e9bce`) with Neutrino's licence added. Its PC-side
`udpfs_server/` folder is left out: it is not for the PS2.

RIPPS2 carries it inside RIPPS2.elf. When a game starts through Neutrino and no Neutrino is found where
RIPPS2 looks (the path in Settings, the game's drive, the memory cards), RIPPS2 asks where to install
this one: the game's drive (`<drive>/neutrino/`) or a memory card (`mc0:/neutrino/`, `mc1:/neutrino/`).
Your own Neutrino always comes first. `config/system.toml` is written last, so an interrupted copy is
never taken for a complete install.
