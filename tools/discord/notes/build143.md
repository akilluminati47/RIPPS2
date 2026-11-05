# Builds 142 and 143: Save Settings To stays, BIBLE's AUTO hang fixed, BIBLE no longer reads the boot sound. Lab only so far, so your reports count.

## Get it
- **RIPPS2.elf** and **RIPPS2-languages.zip** are attached below, or from the [release page](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.4.3-beta). The [theme pack](https://github.com/akilluminati47/RIPPS2-themes/releases/latest) stays at edition 136.

## New
- **Save Settings To stays** (thanks nuno6573): a settings file beside RIPPS2.ELF no longer beats your choice, and the row starts the drive you choose instead of saying it is not connected.
- **If you hit that before:** your old choice is still on the card and RIPPS2 follows it now. To stay on the card, choose Memory Card and Save Changes.
- **BIBLE f5705eb inside.** Manage offers the update to a card on an older BIBLE. A missing file on an AUTO path no longer stops the boot on the splash, but a card keeps that hang until it takes the update.
- **BIBLE no longer reads the boot sound into memory.** It only tells RIPPS2 the folder.
- **ROM 2.30 and newer:** Manage warns that a bound BIBLE may not start at power on, and still lets you try.
- **A plain BIBLE** at mc?:/BOOT/BOOT.ELF, started by OpenTuna or FunTuna, is recognised, so its settings rows work.

## Test list
- Save Settings To > USB Drive, with USB's source on Manual and never opened: does it save, and is the row still USB after a power cycle?
- The same with MMCE.
- RIPPS2 in mc?:/RIPPS2, the same test. Does it stay on the drive?
- Pull that drive and boot. Does RIPPS2 come up with the card's settings, after a short wait? Put it back and boot: are the drive's settings back?
- Choose Memory Card again and Save Changes. Does it stay on the card?
- Fast Boot on, a drive as the home: is the drive read on the next boot?
- A card on an older BIBLE: does Manage offer Update BIBLE, does the bind work, and does it start at power on?
- After that update: is the folder's icon right in the console's browser and in Memory Files' viewer?
- BIBLE's MMCE build with an AUTO path to a file that is not there: does it move on within a few seconds?
- Boot Sound On (fast) with the new BIBLE: is the sound there with the towers?
- ROM 2.30 or newer: does Manage warn you, and did a bind start at power on? Please tell us either way.
- OpenTuna or FunTuna with BIBLE's plain ELF: does Manage show BIBLE's rows, and does the list say plain ELF?

## Report
Say your console model and ROM and what you did, and attach your `DIAG.TXT`: STATUS > SAVE DIAGNOSTICS, or it saves itself when a game or a video starts from a drive.
