# POPSTARTER (bundled)

**POPSTARTER** is the PlayStation 1 launcher for the PlayStation 2 by **krHACKen**. It is freeware.

RIPPS2 carries `POPSTARTER.ELF` as released (167,700 bytes, SHA-256
`734c813e8e8ec2c6729ec5e15dd46ab696e90deeade8d0b2ca3ad03782781aa1`, CRC-32 `59ebabb9`), the copy the
PSBBN Definitive Patch project ships (github.com/CosmicScale/PSBBN-Definitive-English-Patch,
`scripts/assets/POPStarter/POPSTARTER.ELF` at `a9af167`). It is not modified.

Your own POPSTARTER always comes first: the path in Settings, the drive's `POPS`, `APPS` and top
folders, a game's own `POPS/XX.<name>.ELF`, and the memory cards. Only when none of those has one does
RIPPS2 write this copy to the drive's `POPS/POPSTARTER.ELF` (or `__common/POPS` on the HDD), and it never
writes over a file that is already there. RIPPS2 contains no PS1 BIOS and no game data.
