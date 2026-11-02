# Build 130: long films and phone clips open and skip, VIDEO.TXT says where a video stopped, PS1 games named on their own drive, START rows and memory card copies that stay.

## Get it
- **RIPPS2.elf, RIPPS2-lite.elf** (without PS2BBL and Neutrino), **RIPPS2-languages.zip** and the **theme pack** (edition 128) are attached below, or from the [release page](https://github.com/akilluminati47/RIPPS2/releases/tag/v1.3.0-beta)
- Put it in place of your old RIPPS2.elf; your settings stay where they were.

## Video
- **Long videos open.** A two-hour film stuck at "Opening the video": its index outgrew memory. The index is now a fraction of the size (1.6 MB for a 2 h 41 film) and L1 / R1 skip through all of it.
- **Every video opens faster**, over MMCE most of all: the index is read from a buffer, not 4 bytes at a time from the drive.
- **VIDEO.TXT** beside RIPPS2 lists each step of opening a video, so one that never starts says where it stopped. A video RIPPS2 cannot play (a camera's MJPEG) says so and goes back to the list.

## PS1 names, START rows, Memory Files
- **PS1 games named by a code show their name**, read from conf_apps.cfg on the drive the POPS folder is on (its root or its OPL folder), on the list and on the info page.
- **START rows**: a drive on Manual with nothing saved gets a START row in All Games (START HDD, START USB, START MMCE...). Cross starts the drive and its games take the row's place.
- **A file copied onto a memory card stays** (it used to fail its read-back check and get removed).
- **A memory card folder lists in one read**: a full 64 MB card no longer crawls.

## Test list
- **Play a short video** (Betty Boop or any Media Studio clip) from **MMCE**: how long until the picture shows?
- **The same video from USB**: same?
- **Play a long film** (two hours or more) from MMCE or USB: does it open, and does sound stay in sync?
- **L1 / R1 in a long film**: does skipping work near the start, the middle and the end?
- **A phone clip** made with Media Studio: does it play to the end?
- **A camera's own MJPEG .avi**: does RIPPS2 say it cannot play it and go back to the list?
- **If a video stops or never starts**: send the VIDEO.TXT beside RIPPS2 (and DIAG.TXT).
- **PS1 games installed by POPStarterGameInstaller** on a USB drive: do they show their names, not codes?
- **The info page** of one of those games: is the Title the name too, and does it still launch?
- **START rows**: set USB, HDD or MMCE to Manual, open All Games: a START row for each? Cross starts the drive and its games appear?
- **Copy a file onto a memory card** in Memory Files: is it still there after you leave and come back?
- **Open a full 64 MB card** in Memory Files: how long does the list take?
- **Boot RIPPS2 from a memory card** with Boot Sound On (fast): does the sound start with the pillars?
- **RIPPS2-lite.elf**: everything the same as the full ELF?

## Coming next
- **Video player**: pause goes silent on a still frame, a clean end of video.
- **RIPFLOW and the info page**: Square / Triangle hints after a short idle, fades in step with the screenshot, art over the glass.
- **Themes**: RIPGRID L1 / R1 page like L2 / R2, the star on the right edge for Adapt and legacy, sky-matched vignettes.
- **Settings and Memory Files**: Set Metadata on every item, a smoother General and System tab, a pop-up that says how many files a copy wrote.

## Report
Please [open an issue on GitHub](https://github.com/akilluminati47/RIPPS2/issues) with your **console model**, your drives, your **boot loader**, where RIPPS2 starts from, your **DIAG.TXT** (STATUS > SAVE DIAGNOSTICS), **VIDEO.TXT** if it is about a video, and a **photo** of anything odd. Thanks to ripto, nuno6573, zackcage6, eliminator1403, FifthFox, Mr.sus.60, lukeatmynose and ahavasi for the reports that got us here (ahavasi's long film above all), to DarkNerdShawny for opening issues on GitHub, and to everyone testing RIPPS2 on Discord and opening issues on GitHub: be like them. Special thanks to all the YouTube love as well: glad to help however you reach me.
