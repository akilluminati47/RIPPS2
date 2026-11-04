# BIBLE race takes (11/03 night): BIBLE 3282396's memory card build (unsigned lab ELF) starting RIPPS2 139 from the lab
# card, BIBLE_BACKGROUND BLANK, no glyphs, VIDEO_MODE AUTO (RIPPS2's NTSC). -Which w6000 (info on) or w0.
param([string]$Which = 'w6000', [string]$Steps = 'wait:0.3,burst:28,wait:0.5')
$R = 'C:\Users\MINIPC~1\AppData\Local\Temp\claude\382675e3eda1ee02\b7d6b691-8b5a-49a2-aed2-50b5989d4fe8\scratchpad\race'
$F = "B:\Emulation\PlayStation\PCSX2\ripps2-test\race_frames\$Which"
$env:REEL_CARD_DIRS = "APPS=$R\$Which\APPS;SYS-CONF=$R\$Which\SYS-CONF"
$env:PS2BG_BURST = $F
Remove-Item -Recurse -Force $F -ErrorAction SilentlyContinue
& 'B:\Videos - Projects\.montages\hyperframes\ripps2-recap\tools\take108.ps1' -Name "bible_race_$Which" -Upscale 2 -Hdd 'B:\Emulation\PlayStation\PCSX2\ripps2-test\t114-sdmirror.raw' -Elf 'B:\Webpages - Projects\BIBLE-to-sign\in-next\PS2\COMPRESSED_PS2BBL.ELF' -Set @("theme=<RIPPS2>","vmode=2","enable_bgm=0","enable_boot_snd=0") -Steps $Steps 2>&1 | Select-Object -Last 3
Remove-Item Env:REEL_CARD_DIRS
Remove-Item Env:PS2BG_BURST
