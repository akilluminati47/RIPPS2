# Neutrino (found, not carried)

**Neutrino** is a small, fast and modular PS2 device emulator by **rickgaiser**, licensed **AFL-3.0**
(`LICENSE.txt`, beside this file). Releases: <https://github.com/rickgaiser/neutrino/releases>

RIPPS2 starts games through the Neutrino you keep. Since build 135 (v1.3.5-beta) it no longer carries a copy: put
Neutrino's release folder as `neutrino/` on the game's drive or on a memory card (`mc0:/neutrino/`, `mc1:/neutrino/`),
or point **Game Launching > Neutrino** at its `neutrino.elf`. RIPPS2 looks there, then wherever **STATUS > LOOK FOR
THEM** or an earlier launch found one, and a launch that finds none says where to put it. RIPPS2 reads the install's
`version.txt` (or, for an older kit, its `config/` files) and sends it only the options it knows.

Builds 77 to 134 carried Neutrino inside RIPPS2.elf and installed it where the user picked (1.8.0, then from build 115
the development build v1.8.0-61-g7be8de2). That tar is in this folder's history:
`git log -- elf/neutrino/neutrino-1.8.0-61-g7be8de2.tar.gz`. `tools/dev/pack_neutrino.py` still repacks a release
the same way, for anyone who wants that copy.
