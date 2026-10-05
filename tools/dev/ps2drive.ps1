# Drives PCSX2 for RIPPS2 testing: launch an ELF, press pad buttons (via the keyboard
# bindings added to [Pad1]), and take F8 screenshots into Documents\PCSX2\snaps.
#
#   ps2drive.ps1 -Elf <path> -Steps "wait:12,shot,down,down,shot,cross,wait:3,shot" [-Keep]
#
# Step tokens: wait:<sec>, shot, up, down, left, right, cross, circle, square, triangle,
#              start, select, l1, r1, l2, r2, rup/rdown/rleft/rright (right stick), hold:<button>:<ms>,
#              kdown:<button> / kup:<button> (hold across other steps)
param(
  [string]$Elf,
  [string]$Steps = "wait:15,shot",
  [switch]$Keep,
  [string]$Iso = "",   # a disc image in the drive as well (the ELF still boots)
  [switch]$Attach   # drive the PCSX2 that is already running instead of launching
)

$exe = "B:\Emulation\PlayStation\PCSX2\pcsx2-v2.9.92-windows-x64-Qt\pcsx2-qt.exe"
$snaps = "$env:USERPROFILE\Documents\PCSX2\snaps"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class W {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
  [DllImport("user32.dll")] public static extern uint MapVirtualKey(uint code, uint type);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, IntPtr pid);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
}
"@
Add-Type -AssemblyName System.Drawing
$grabDir = Join-Path $PSScriptRoot "grabs"
New-Item -ItemType Directory -Force $grabDir | Out-Null

# Copy the PCSX2 window straight off the screen (no hotkey involved). It must be visible and on top.
function Grab($p) {
  $r = New-Object W+RECT
  [void][W]::GetWindowRect($p.MainWindowHandle, [ref]$r)
  $w = $r.R - $r.L; $h = $r.B - $r.T
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size)
  $file = Join-Path $grabDir ("grab_{0}.png" -f (Get-Date -Format 'HHmmss_fff'))
  $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
  return $file
}

# Virtual-key codes for the keyboard bindings in [Pad1] plus the F8 screenshot hotkey
$vk = @{ up=0x26; down=0x28; left=0x25; right=0x27; cross=0x58; circle=0x43; square=0x5A; triangle=0x53;
         start=0x0D; select=0x08; l1=0x51; r1=0x45; l2=0x31; r2=0x33; f8=0x77;
         rup=0x49; rdown=0x4B; rleft=0x4A; rright=0x4C; rec=0x7A; l3=0x56; r3=0x42 }  # l3: V, r3: B  # rec: F11, PCSX2 video capture on/off  # right stick on I/K/J/L (Pad1 keyboard binds)
$extended = @(0x25, 0x26, 0x27, 0x28)

# Bring PCSX2 to the front. Windows can refuse a plain SetForegroundWindow, so if it does,
# briefly attach to the foreground thread's input and retry. Returns $true only when PCSX2
# really is the foreground window.
function Focus($p) {
  $p.Refresh(); $h = $p.MainWindowHandle
  [void][W]::ShowWindow($h, 9)
  [void][W]::SetForegroundWindow($h)
  if ([W]::GetForegroundWindow() -ne $h) {
    $fg = [W]::GetWindowThreadProcessId([W]::GetForegroundWindow(), [IntPtr]::Zero)
    $me = [W]::GetCurrentThreadId()
    [void][W]::AttachThreadInput($me, $fg, $true)
    [void][W]::BringWindowToTop($h); [void][W]::SetForegroundWindow($h)
    [void][W]::AttachThreadInput($me, $fg, $false)
  }
  Start-Sleep -Milliseconds 450
  return ((FgPid) -eq $p.Id)
}
# Process that owns the foreground window. Comparing processes (not window handles) also accepts
# PCSX2's own dialogs, such as the "shut down?" prompt.
function FgPid { $fp = [uint32]0; [void][W]::GetWindowThreadProcessId([W]::GetForegroundWindow(), [ref]$fp); return $fp }
# Short taps: a longer hold trips the menus' auto-repeat and moves twice.
# Every press first re-checks that PCSX2 is in front; if it cannot be, the run stops instead of
# sending the key to whatever window is in front.
$script:proc = $null
function Press([int]$code, [int]$ms = 100) {
  if (-not $script:proc) { throw "no PCSX2 process registered; key not sent" }
  if ((FgPid) -ne $script:proc.Id -and -not (Focus $script:proc)) { throw "PCSX2 is not the foreground window; key not sent" }
  $scan = [byte][W]::MapVirtualKey($code, 0)
  $flag = if ($extended -contains $code) { 1 } else { 0 }
  [W]::keybd_event([byte]$code, $scan, $flag, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds $ms
  [W]::keybd_event([byte]$code, $scan, ($flag -bor 2), [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 120
}

$before = @(Get-ChildItem $snaps -Filter *.png -ErrorAction SilentlyContinue | ForEach-Object FullName)
if ($Attach) {
  $p = Get-Process pcsx2-qt -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $p) { "no running PCSX2 to attach to"; return }
  "attached to pid $($p.Id)"
} else {
  $launchArgs = @("-fastboot", "-elf", "`"$Elf`"")
  if ($Iso) { $launchArgs += "`"$Iso`"" }
  $p = Start-Process -FilePath $exe -ArgumentList $launchArgs -PassThru
  for ($i = 0; $i -lt 40 -and $p.MainWindowHandle -eq 0; $i++) { Start-Sleep -Milliseconds 250; $p.Refresh() }
  "launched pid $($p.Id)"
}
$script:proc = $p
# The window can exist before it is shown, and Windows will not foreground a hidden window:
# keep trying for a while. If it never comes forward, skip the steps but still close and restore.
$focused = $false
for ($i = 0; $i -lt 24 -and -not $focused; $i++) { $focused = Focus $p; if (-not $focused) { Start-Sleep -Milliseconds 500 } }
if ($focused) {
  Press 0x10 # wake the window with an unbound key (Shift) so the first real button press is not dropped
} else {
  "PCSX2 could not be brought to the front; no keys sent"
  $Steps = ""
}

foreach ($s in ($Steps -split ',')) {
  $s = $s.Trim(); if (-not $s) { continue }
  if ($s -like 'wait:*') { Start-Sleep -Seconds ([double]($s.Split(':')[1])); continue }
  if (-not (Focus $p)) { "stopped at '$s': PCSX2 is not in front, so no key was sent"; break }
  if ($s -eq 'shot') { Press $vk.f8; Start-Sleep -Milliseconds 1300; "shot"; continue }
  if ($s -eq 'grab') { "grab $(Grab $p)"; continue }
  if ($s -like 'kdown:*' -or $s -like 'kup:*') { # press and hold / release, so a shot can land mid-hold
    $a = $s.Split(':'); $code = $vk[$a[1]]; $scan = [byte][W]::MapVirtualKey($code, 0)
    $flag = if ($extended -contains $code) { 1 } else { 0 }
    if ($a[0] -eq 'kup') { $flag = $flag -bor 2 }
    [W]::keybd_event([byte]$code, $scan, $flag, [UIntPtr]::Zero); "$($a[0]) $($a[1])"; continue
  }
  if ($s -like 'hold:*') { $a = $s.Split(':'); Press $vk[$a[1]] ([int]$a[2]); "hold $($a[1])"; continue }
  if ($vk.ContainsKey($s)) { Press $vk[$s]; "press $s" } else { "unknown step '$s'" }
}

$after = @(Get-ChildItem $snaps -Filter *.png -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | ForEach-Object FullName)
$new = $after | Where-Object { $before -notcontains $_ }
"screenshots:"; $new
$p.Refresh(); "window title: $($p.MainWindowTitle)"
if (-not $Keep -and -not $p.HasExited) {
  [void]$p.CloseMainWindow(); Start-Sleep -Milliseconds 800; $p.Refresh()
  # ConfirmShutdown is on: accept the modal "shut down?" prompt with Enter
  if (-not $p.HasExited -and (Focus $p)) { Press 0x0D }
  for ($i = 0; $i -lt 16 -and -not $p.HasExited; $i++) { Start-Sleep -Milliseconds 500; $p.Refresh() }
  if ($p.HasExited) { "PCSX2 closed" } else { "PCSX2 still open" }
}

# PCSX2 saves its window position on exit: put the user's own geometry back from the backup
$p.Refresh()
if ($p.HasExited) {
  $ini = "$env:USERPROFILE\Documents\PCSX2\inis\PCSX2.ini"
  $bak = "$ini.ripps2-backup"
  if (Test-Path $bak) {
    $orig = @{}
    foreach ($k in 'MainWindowGeometry', 'MainWindowState') { $orig[$k] = (Select-String -Path $bak -Pattern "^$k = " | Select-Object -First 1).Line }
    $c = Get-Content $ini | ForEach-Object { $l = $_; foreach ($k in $orig.Keys) { if ($orig[$k] -and $l -match "^$k = ") { $l = $orig[$k] } }; $l }
    [IO.File]::WriteAllText($ini, (($c -join "`r`n") + "`r`n"), (New-Object Text.UTF8Encoding $false)) # no BOM: the file never had one
    "restored your PCSX2 window geometry"
  }
}
