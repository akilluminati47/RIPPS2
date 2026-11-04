# Publishing v1.4.0-beta (for when the user says so)

The draft release holds RIPPS2.elf and RIPPS2-languages.zip from CI run 41863546378 (7a15c7b). Nothing public says 1.4.0 yet except the CHANGELOG.

1. Fill the "TO FILL IN FROM THE CONSOLE TEST" row of notes/release140.md, and take out anything the console test contradicts. Same for notes/psxplace140.txt.
2. `gh release edit v1.4.0-beta -R akilluminati47/RIPPS2 --notes-file tools/discord/notes/release140.md --draft=false --latest`. Never attach a video.
3. README: build 140, v1.4.0 beta, 2,768 KB, in English and 32 languages: the 11/03 scratchpad's i18n139.py with 138/139 and 1.3.8/1.3.9 moved on a build and 730/764 becoming 764/768, then `readme_i18n.py check` and `build`. README banner: `make_test_embed.py --build 140 --notes notes/build140.md --readme`.
4. The user posts: psxplace-post.bbcode (first post), psxplace-bible-post.bbcode (BIBLE's first post), notes/psxplace140.txt (RIPPS2's thread), notes/psxplace140-bible.txt (BIBLE's thread).
5. Discord only when the user says: `make_test_embed.py --build 140 --notes notes/build140.md --release <url> --attach ...`.
6. The APPS and RIPPS2 folders on the user's SD already have this build, with RIPPS2-139.ELF.bak beside each.
