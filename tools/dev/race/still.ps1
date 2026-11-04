# BIBLE stills in 1080i (11/03 night): a Color Theme's sky without the info line, or the credits page. F8 shots.
param([string]$Which = 'blood', [string]$Steps = 'wait:5.5,shot,wait:1,grab,wait:1')
$R = 'C:\Users\MINIPC~1\AppData\Local\Temp\claude\382675e3eda1ee02\b7d6b691-8b5a-49a2-aed2-50b5989d4fe8\scratchpad\race'
$env:REEL_CARD_DIRS = "SYS-CONF=$R\still_$Which\SYS-CONF"
& 'B:\Videos - Projects\.montages\hyperframes\ripps2-recap\tools\take108.ps1' -Name "bible_still_$Which" -Upscale 1 -Hdd 'B:\Emulation\PlayStation\PCSX2\ripps2-test\t114-sdmirror.raw' -Elf 'B:\Webpages - Projects\BIBLE-to-sign\in-next\PS2\COMPRESSED_PS2BBL.ELF' -Set @("theme=<RIPPS2>","vmode=2","enable_bgm=0") -Steps $Steps 2>&1 | Select-Object -Last 4
Remove-Item Env:REEL_CARD_DIRS
