# Publishing v1.4.3-beta and BIBLE signed-f5705eb (for when the user says so)

Nothing here has run. Every item is outward-facing and waits on the user's word. ELF: CI run 41998045891 (cc6cdbc), 2,816,052 B = 2,750 KB, artifacts RIPPS2-elf and RIPPS2-languages. Nothing on a real PS2 yet.

## Before: worth doing at the console
1. Follow `BIBLE-to-sign/README-f5705eb.txt`: Update BIBLE in Manage (it writes the icon too, KELFBinder does not), power on, then the hang test (E1 at a missing mmce path). If it stays on the splash for 30 s, stop: don't release. The SD is set up and backed up (`RIPPS2-holding-2026-11-05`).
2. If it binds, that card makes the new BootCard: `tools/dev/bible_bootcard.py --into <clean BOOT card> <bound card> <out>`, then cardwipe and grep first. No BootCard means publish143.py without `--bootcard`.
3. Put the notes right: fill in the "Not run yet" rows of release143.md and bible-release-f5705eb.md, and take out anything the console contradicts. Same for psxplace143*.txt.

## BIBLE first: RIPPS2's notes link to it
4. `gh release create signed-f5705eb -R akilluminati47/BIBLE --target f5705eb6ae422b95c08d4e5662f72b54e133e857 --title "BIBLE f5705eb, signed by akilluminati47: no more hang on a missing AUTO path" --notes-file tools/discord/notes/bible-release-f5705eb.md --latest` with `BIBLE-to-sign/release-f5705eb/`: BIBLE-signed-f5705eb.zip, BIBLE-ELF-f5705eb.zip, SHA256SUMS.txt (and the BootCard, in the sums too).
5. Merge BIBLE's `readme-f5705eb` into main: its README then matches what is published. README line 101 (the plain ELF) can follow a console result.

## RIPPS2
6. `make_test_embed.py --build 143 --notes tools/discord/notes/build143.md --out <dir>`, copy test-me-143.png over media/ripps2-test-me.png.
7. `python tools/discord/notes/publish143.py . [--bootcard]`, then `python tools/readme-i18n/readme_i18n.py check .` and `build .`. Commit with [skip ci], so the CI build stays the tested one.
8. `gh release create v1.4.3-beta -R akilluminati47/RIPPS2 --target <that commit> --title "RIPPS2 v1.4.3 beta (builds 142 and 143): Save Settings To stays, BIBLE's AUTO hang fixed" --notes-file tools/discord/notes/release143.md --latest` with RIPPS2.elf and RIPPS2-languages.zip from run 41998045891. Full release, never pre-release; never attach a video. Check the releases/latest download and every media link return 200.

## Words
9. Discord, only on the user's word: `make_test_embed.py --build 143 --notes tools/discord/notes/build143.md --release <url> --attach RIPPS2.elf --attach RIPPS2-languages.zip --attach <themes zip> --attach media/b143/save-settings.gif --post` with the webhook from ~/.ripps2/discord.env, never printed. BIBLE's channel gets its own post.
10. tools/discord/notes/reply143-nuno.md, once the build is out. Ask the user first: nuno may have answered in the meantime.
11. The user posts to psx-place, in this order: psxplace-bible-post.bbcode, psxplace-post.bbcode, notes/psxplace143.txt, notes/psxplace143-bible.txt. These replace psxplace141*.txt if those were not posted yet; they also cover 1.4.1's changes only by link, so if 141 was never bumped, post 141 first.
12. The SD (D:) has had build 143 since 11/05, the same bytes as CI run 41998045891, with RIPPS2-140.ELF.bak beside each. If the release is that build, nothing more to copy.
