# Build 136: BIBLE's MMCE build, no bind on an SD2PSX, slots 0 and 1, STATUS's audio row, and RIPGRID's source name fixed.

## Get it
- **RIPPS2.elf**, **RIPPS2-languages.zip** and the **theme pack** (edition 136) are attached below, or from the [release page](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.3.6-beta).
- Put it in place of your old RIPPS2.elf; your settings stay where they were.

## BIBLE
- **BIBLE's MMCE build is carried, signed by akilluminati47**: with RIPPS2 on an SD2PSX or MemCard PRO 2, Manage installs it on a genuine card in the other slot, and it starts RIPPS2 from the SD card at power on (genuine card in slot 0).
- **An SD2PSX or MMCE card is never bound**: Manage says so before anything restarts and offers BOOT LOCK for its own PS2BBL.
- **Slots are counted 0 and 1** everywhere, as mc0: and mc1:.

## STATUS
- **RIP THIS CONSOLE'S AUDIO** opens Audio Settings on BIOS Sounds and BIOS Music.
- The boot sound line names its file and says when it is on a memory card.

## RIPGRID and Adapt
- Categories across the top: the source name is Pop In only, nothing over STORAGE. Sidebar: the name over the grid too (Planet N on RIPGRID).

## Test list
- **SD2PSX or MMCE in a slot, Manage on that slot**: does it explain and offer BOOT LOCK, with no restart and no card dropping out?
- **BOOT LOCK from that offer**: does the SD2PSX boot card start RIPPS2 at power on?
- **BIBLE on a genuine card, RIPPS2 on the SD2PSX**: does Manage install it, and does power on (genuine card in slot 0) start RIPPS2 from the SD?
- **BIBLE on a genuine card, RIPPS2 on a memory card or USB**: does the console take the bind?
- **A refused bind**: does the message say to power cycle, and is the card back after one?
- **Manage, BOOT LOCK and STATUS**: do they all say slot 0 and slot 1?
- **A game's VMC settings**: VMC Slot 0 and VMC Slot 1?
- **STATUS > RIP THIS CONSOLE'S AUDIO**: does Audio Settings open on BIOS Sounds, and Circle come back?
- **STATUS boot sound line**: does it name your boot.adp, and say memory card when it is on one?
- **RIPGRID across the top**: nothing over STORAGE, the big name as the source changes?
- **RIPGRID with the sidebar**: the source name at the top in Planet N?
- **Adapt and Adapt Rx (pack 136)**: the same rule in their own font?
- **Your language**: are the new lines translated?

## Report
Please [open an issue on GitHub](https://github.com/akilluminati47/RIPPS2/issues) with your **console model**, **your cards** (genuine, SD2PSX, MemCard PRO 2) and your **DIAG.TXT** (STATUS > SAVE DIAGNOSTICS).
