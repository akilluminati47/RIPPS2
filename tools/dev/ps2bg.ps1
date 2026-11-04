# Drives the RIPPS2 lab PCSX2 in the BACKGROUND: it never takes focus, never touches the keyboard, and stays off the
# screen, so the user can keep using the PC (or play a game) while tests run. Same step language as ps2drive.ps1.
#
#   ps2bg.ps1 -Elf <path> -Steps "wait:24,start,wait:2,grab,cross,wait:3,grab" [-Keep] [-Attach]
#
# How: PCSX2 is started minimized without activation (SW_SHOWMINNOACTIVE), then restored, still without activation,
# to a spot far off the screen, so it renders but nobody sees it. Pad buttons are POSTED to PCSX2's own windows as
# key messages (the [Pad1] keyboard bindings), so no other program ever receives them. "grab" asks the window to
# draw itself into a bitmap (PrintWindow, PW_RENDERFULLCONTENT), which works off screen. "rec" posts F11 (PCSX2's
# video capture), "shot" F8 (its screenshot). At the end the lab PCSX2 is closed (killed: its cards are lab copies).
#
# Not out of sight entirely (user, 10/13/2026): a small "RIPPS2 lab: AI run" window sits on the user's taskbar for
# the whole run, shown without taking the focus. It says which step the run is on, previews the hidden screen once a
# second, and has two buttons. Take over saves a state (F1), closes the hidden PCSX2 and opens PCSX2 on the user's own
# desktop at that point, to play on by hand. Stop (or closing the window) ends the run. The hidden PCSX2 is tied to this
# script's process (a job that ends with it), so ending the run in Task Manager closes PCSX2 too. -NoPanel leaves the
# window out; -Title names the run in it.
#
# Step tokens: wait:<sec>, grab, burst:<sec> (frames to PS2BG_BURST as fast as they come), shot, rec, sstate (F1: a save state, for reading a stuck EE), up, down, left, right, cross, circle, square, triangle, start, select,
#              l1, r1, l2, r2, l3, r3, rup/rdown/rleft/rright (right stick), hold:<button>:<ms>,
#              kdown:<button> / kup:<button>
param(
  [string]$Elf,
  [string]$Steps = "wait:15,grab",
  [switch]$Keep,
  [string]$Iso = "",
  [switch]$Attach,
  [string]$Title = "",
  [switch]$NoPanel,
  [switch]$Bios
)

$lab = "B:\Emulation\PlayStation\PCSX2\ripps2-lab"
$exe = "$lab\pcsx2-qt.exe"
$grabDir = Join-Path $PSScriptRoot "grabs"
New-Item -ItemType Directory -Force $grabDir | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -ReferencedAssemblies System.Drawing, System.Windows.Forms @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class BG {
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct STARTUPINFO { public int cb; public string lpReserved, lpDesktop, lpTitle; public int dwX, dwY, dwXSize, dwYSize,
    dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags; public short wShowWindow, cbReserved2; public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError; }
  [StructLayout(LayoutKind.Sequential)] public struct PROCESS_INFORMATION { public IntPtr hProcess, hThread; public int dwProcessId, dwThreadId; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [StructLayout(LayoutKind.Sequential)] public struct WINDOWPLACEMENT { public int length, flags, showCmd; public POINT ptMin, ptMax; public RECT rcNormal; }
  [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  static extern bool CreateProcess(string app, StringBuilder cmd, IntPtr pa, IntPtr ta, bool inherit, uint flags, IntPtr env, string dir,
    ref STARTUPINFO si, out PROCESS_INFORMATION pi);
  [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc f, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr p, EnumProc f, IntPtr l);
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern uint MapVirtualKey(uint code, uint type);
  [DllImport("user32.dll")] public static extern bool GetWindowPlacement(IntPtr h, ref WINDOWPLACEMENT p);
  [DllImport("user32.dll")] public static extern bool SetWindowPlacement(IntPtr h, ref WINDOWPLACEMENT p);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)] static extern IntPtr CreateDesktop(string name, IntPtr dev, IntPtr mode, int flags, uint access, IntPtr sa);
  [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)] static extern IntPtr OpenDesktop(string name, int flags, bool inherit, uint access);
  [DllImport("user32.dll", SetLastError = true)] static extern bool SetThreadDesktop(IntPtr h);
  [DllImport("user32.dll")] static extern bool EnumDesktopWindows(IntPtr desk, EnumProc f, IntPtr l);

  // A desktop of its own (not the one on the screen): nothing on it can take the focus, show up or get the keyboard
  public static string DeskName = "RIPPS2LAB";
  public static IntPtr Desk = IntPtr.Zero;
  public static bool UseDesk = false;
  public static bool OpenDesk() {
    Desk = OpenDesktop(DeskName, 0, false, 0x10000000); // GENERIC_ALL
    if (Desk == IntPtr.Zero) Desk = CreateDesktop(DeskName, IntPtr.Zero, IntPtr.Zero, 0, 0x10000000, IntPtr.Zero);
    UseDesk = Desk != IntPtr.Zero;
    return UseDesk;
  }
  // Runs f on a thread that sits on the lab's desktop (window messages only cross within one desktop)
  public static void OnDesk(Action f) {
    if (!UseDesk) { f(); return; }
    Exception err = null;
    var t = new System.Threading.Thread(() => { try { SetThreadDesktop(Desk); f(); } catch (Exception e) { err = e; } });
    t.Start(); t.Join();
    if (err != null) throw err;
  }
  public static IntPtr MainWindowOnDesk(int pid) {
    if (!UseDesk) return MainWindow(pid);
    IntPtr best = IntPtr.Zero; long area = 0;
    EnumDesktopWindows(Desk, (h, l) => { uint p; GetWindowThreadProcessId(h, out p);
      if (p == pid && IsWindowVisible(h)) { RECT r; GetWindowRect(h, out r); long a = (long)(r.R - r.L) * (r.B - r.T);
        var c = new StringBuilder(64); GetClassName(h, c, 64);
        if (a > area && c.ToString().StartsWith("Qt")) { area = a; best = h; } }
      return true; }, IntPtr.Zero);
    return best;
  }
  public static void Post(IntPtr h, uint msg, long w, long l) { OnDesk(() => PostMessage(h, msg, (IntPtr)w, (IntPtr)l)); }
  public static bool GrabOnDesk(IntPtr h, string file) { bool ok = false; OnDesk(() => { ok = Grab(h, file); }); return ok; }
  // 11/03: burst:<sec>, frames as fast as PrintWindow gives them, uncompressed, named by the ms since the burst began. PCSX2's
  // video capture dies when one ELF starts another (BIBLE into RIPPS2); this carries straight through it
  public static int BurstOnDesk(IntPtr h, string dir, double seconds) {
    int n = 0;
    OnDesk(() => {
      RECT r; GetWindowRect(h, out r); int w = r.R - r.L, hh = r.B - r.T;
      var sw = System.Diagnostics.Stopwatch.StartNew();
      using (var bmp = new System.Drawing.Bitmap(w, hh, System.Drawing.Imaging.PixelFormat.Format24bppRgb)) {
        while (sw.Elapsed.TotalSeconds < seconds) {
          long ms = sw.ElapsedMilliseconds;
          using (var g = System.Drawing.Graphics.FromImage(bmp)) { IntPtr dc = g.GetHdc(); PrintWindow(h, dc, 2); g.ReleaseHdc(dc); }
          bmp.Save(System.IO.Path.Combine(dir, "f" + ms.ToString("D6") + ".bmp"), System.Drawing.Imaging.ImageFormat.Bmp);
          n++;
        }
      }
    });
    return n;
  }
  public static void ParkOnDesk(IntPtr h, int w, int hgt) { OnDesk(() => Park(h, w, hgt)); }

  public static int Launch(string exe, string args, string dir) {
    var si = new STARTUPINFO(); si.cb = Marshal.SizeOf(si); si.dwFlags = 1; si.wShowWindow = 7; // STARTF_USESHOWWINDOW, SW_SHOWMINNOACTIVE
    if (UseDesk) si.lpDesktop = "WinSta0\\" + DeskName;
    PROCESS_INFORMATION pi;
    if (!CreateProcess(exe, new StringBuilder("\"" + exe + "\" " + args), IntPtr.Zero, IntPtr.Zero, false, 0, IntPtr.Zero, dir, ref si, out pi)) return -1;
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    return pi.dwProcessId;
  }
  public static string Info(IntPtr h) {
    var c = new StringBuilder(128); GetClassName(h, c, 128); var t = new StringBuilder(128); GetWindowText(h, t, 128);
    return c.ToString() + " '" + t.ToString() + "'";
  }
  // The process's main window: its biggest visible top-level window (the game display lives inside it)
  public static IntPtr MainWindow(int pid) {
    IntPtr best = IntPtr.Zero; long area = 0;
    EnumWindows((h, l) => { uint p; GetWindowThreadProcessId(h, out p);
      if (p == pid && IsWindowVisible(h)) { RECT r; GetWindowRect(h, out r); long a = (long)(r.R - r.L) * (r.B - r.T);
        var c = new StringBuilder(64); GetClassName(h, c, 64);
        if (a > area && c.ToString().StartsWith("Qt")) { area = a; best = h; } }
      return true; }, IntPtr.Zero);
    return best;
  }
  public static List<IntPtr> Children(IntPtr parent) {
    var list = new List<IntPtr>();
    EnumChildWindows(parent, (h, l) => { list.Add(h); return true; }, IntPtr.Zero);
    return list;
  }
  // Somewhere nobody looks: restored (so it renders) far off every screen, and never activated
  public static void Park(IntPtr h, int w, int hgt) {
    var p = new WINDOWPLACEMENT(); p.length = Marshal.SizeOf(p); GetWindowPlacement(h, ref p);
    p.showCmd = 4; // SW_SHOWNOACTIVATE
    p.rcNormal.L = -12000; p.rcNormal.T = -9000; p.rcNormal.R = -12000 + w; p.rcNormal.B = -9000 + hgt;
    SetWindowPlacement(h, ref p);
  }
  public static bool Grab(IntPtr h, string file) {
    RECT r; GetWindowRect(h, out r); int w = r.R - r.L, hh = r.B - r.T;
    if (w <= 0 || hh <= 0) return false;
    using (var bmp = new System.Drawing.Bitmap(w, hh)) {
      using (var g = System.Drawing.Graphics.FromImage(bmp)) { IntPtr dc = g.GetHdc(); PrintWindow(h, dc, 2); g.ReleaseHdc(dc); }
      bmp.Save(file, System.Drawing.Imaging.ImageFormat.Png);
    }
    return true;
  }
  // 10/25: PCSX2's own message boxes (an "Error" over the main window). One sat unseen on the lab's desktop from 01:30 on
  // and, being modal, disabled the main window, so no key reached the game for hours. Visible Qt windows the main one owns.
  [DllImport("user32.dll")] static extern IntPtr GetWindow(IntPtr h, uint cmd);
  public static List<IntPtr> Dialogs(int pid, IntPtr main) {
    var list = new List<IntPtr>();
    EnumProc f = (h, l) => { uint p; GetWindowThreadProcessId(h, out p);
      if (p == pid && h != main && IsWindowVisible(h) && GetWindow(h, 4) == main) { var c = new StringBuilder(64); GetClassName(h, c, 64);
        if (c.ToString().StartsWith("Qt")) list.Add(h); }
      return true; };
    OnDesk(() => { if (UseDesk) EnumDesktopWindows(Desk, f, IntPtr.Zero); else EnumWindows(f, IntPtr.Zero); });
    return list;
  }
  // The window drawn into a bitmap in memory, for the panel's preview
  public static System.Drawing.Bitmap GrabBitmap(IntPtr h) {
    System.Drawing.Bitmap bmp = null;
    OnDesk(() => {
      RECT r; GetWindowRect(h, out r); int w = r.R - r.L, hh = r.B - r.T;
      if (w <= 0 || hh <= 0) return;
      bmp = new System.Drawing.Bitmap(w, hh);
      using (var g = System.Drawing.Graphics.FromImage(bmp)) { IntPtr dc = g.GetHdc(); PrintWindow(h, dc, 2); g.ReleaseHdc(dc); }
    });
    return bmp;
  }

  // A job that closes with this process: however the run ends (Task Manager included), the hidden PCSX2 ends with it
  [StructLayout(LayoutKind.Sequential)] struct JOBOBJECT_BASIC_LIMIT_INFORMATION { public long PerProcessUserTimeLimit, PerJobUserTimeLimit;
    public uint LimitFlags; public UIntPtr MinimumWorkingSetSize, MaximumWorkingSetSize; public uint ActiveProcessLimit; public UIntPtr Affinity;
    public uint PriorityClass, SchedulingClass; }
  [StructLayout(LayoutKind.Sequential)] struct IO_COUNTERS { public ulong R, W, O, RB, WB, OB; }
  [StructLayout(LayoutKind.Sequential)] struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION { public JOBOBJECT_BASIC_LIMIT_INFORMATION Basic; public IO_COUNTERS Io;
    public UIntPtr ProcessMemoryLimit, JobMemoryLimit, PeakProcessMemoryUsed, PeakJobMemoryUsed; }
  [DllImport("kernel32.dll", CharSet = CharSet.Unicode)] static extern IntPtr CreateJobObject(IntPtr sa, string name);
  [DllImport("kernel32.dll")] static extern bool SetInformationJobObject(IntPtr job, int cls, ref JOBOBJECT_EXTENDED_LIMIT_INFORMATION info, int len);
  [DllImport("kernel32.dll")] static extern bool AssignProcessToJobObject(IntPtr job, IntPtr proc);
  [DllImport("kernel32.dll")] static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
  static IntPtr job = IntPtr.Zero;
  public static bool TieToThisProcess(int pid) {
    if (job == IntPtr.Zero) {
      job = CreateJobObject(IntPtr.Zero, null);
      var info = new JOBOBJECT_EXTENDED_LIMIT_INFORMATION(); info.Basic.LimitFlags = 0x2000; // JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
      if (job == IntPtr.Zero || !SetInformationJobObject(job, 9, ref info, Marshal.SizeOf(info))) return false;
    }
    IntPtr p = OpenProcess(0x0101, false, pid); // PROCESS_TERMINATE | PROCESS_SET_QUOTA
    if (p == IntPtr.Zero) return false;
    bool ok = AssignProcessToJobObject(job, p); CloseHandle(p); return ok;
  }
}

// The run on the user's own desktop: a taskbar window that never takes the focus, says what the hidden PCSX2 is doing,
// previews it, and lets the user stop the run or take it over. Statics carry the run's state between the script's
// thread and the window's.
public class LabPanel : System.Windows.Forms.Form {
  public static volatile int Request = 0;    // 1 stop, 2 take over
  public static volatile string Status = "starting";
  public static volatile int Run = 0;        // a new run closes an old run's window
  public static IntPtr Target = IntPtr.Zero; // the hidden PCSX2 window, for the preview
  int run;
  System.Windows.Forms.Label status;
  System.Windows.Forms.PictureBox peek;
  System.Windows.Forms.Timer timer;
  DateTime started = DateTime.Now;
  protected override bool ShowWithoutActivation { get { return true; } }

  LabPanel(string title, string iconFrom, int run) {
    this.run = run;
    Text = "RIPPS2 lab: AI run" + (title.Length > 0 ? " (" + title + ")" : "");
    FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle; MaximizeBox = false; ShowInTaskbar = true;
    StartPosition = System.Windows.Forms.FormStartPosition.Manual;
    ClientSize = new System.Drawing.Size(360, 386);
    var wa = System.Windows.Forms.Screen.PrimaryScreen.WorkingArea;
    Location = new System.Drawing.Point(wa.Right - Width - 12, wa.Bottom - Height - 12);
    try { Icon = System.Drawing.Icon.ExtractAssociatedIcon(iconFrom); } catch { }
    var head = new System.Windows.Forms.Label { Location = new System.Drawing.Point(12, 8), Size = new System.Drawing.Size(336, 48),
      Text = "An AI test run is using the lab PCSX2 on a hidden desktop. Your keyboard, mouse and controller are untouched; this window never takes the focus." };
    status = new System.Windows.Forms.Label { Location = new System.Drawing.Point(12, 58), Size = new System.Drawing.Size(336, 18), Text = Status };
    peek = new System.Windows.Forms.PictureBox { Location = new System.Drawing.Point(12, 80), Size = new System.Drawing.Size(336, 252),
      SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom, BackColor = System.Drawing.Color.Black };
    var take = new System.Windows.Forms.Button { Text = "Take over", Location = new System.Drawing.Point(12, 342), Size = new System.Drawing.Size(162, 32) };
    var stop = new System.Windows.Forms.Button { Text = "Stop run", Location = new System.Drawing.Point(186, 342), Size = new System.Drawing.Size(162, 32) };
    var tips = new System.Windows.Forms.ToolTip();
    tips.SetToolTip(take, "Saves a state, closes the hidden run and opens PCSX2 on your desktop at that point, to play on by hand");
    tips.SetToolTip(stop, "Ends the run and closes the hidden PCSX2 (closing this window does the same)");
    take.Click += (o, e) => { if (Request == 0) { Request = 2; status.Text = "taking over: saving where it is"; } };
    stop.Click += (o, e) => { if (Request == 0) { Request = 1; status.Text = "stopping"; } };
    FormClosing += (o, e) => { if (Run == this.run && Request == 0) Request = 1; };
    Controls.AddRange(new System.Windows.Forms.Control[] { head, status, peek, take, stop });
    timer = new System.Windows.Forms.Timer { Interval = 1000 };
    timer.Tick += Tick; timer.Start();
  }

  void Tick(object o, EventArgs e) {
    if (Run != run) { timer.Stop(); Close(); return; }
    var t = DateTime.Now - started;
    if (Request == 0) status.Text = string.Format("{0}   ({1}:{2:00})", Status, (int)t.TotalMinutes, t.Seconds);
    if (Target != IntPtr.Zero && Request == 0 && WindowState != System.Windows.Forms.FormWindowState.Minimized) {
      try { var b = BG.GrabBitmap(Target); if (b != null) { var old = peek.Image; peek.Image = b; if (old != null) old.Dispose(); } } catch { }
    }
  }

  public static void Start(string title, string iconFrom) {
    int r = ++Run; Request = 0; Status = "starting PCSX2"; Target = IntPtr.Zero;
    var t = new System.Threading.Thread(() => { System.Windows.Forms.Application.Run(new LabPanel(title, iconFrom, r)); });
    t.SetApartmentState(System.Threading.ApartmentState.STA); t.IsBackground = true; t.Start();
  }
  public static void Finish() { Run++; } // the window closes at its next tick
}
"@

$vk = @{ up=0x26; down=0x28; left=0x25; right=0x27; cross=0x58; circle=0x43; square=0x5A; triangle=0x53;
         start=0x0D; select=0x08; l1=0x51; r1=0x45; l2=0x31; r2=0x33; f8=0x77; f1=0x70; rec=0x7A; l3=0x56; r3=0x42;
         rup=0x49; rdown=0x4B; rleft=0x4A; rright=0x4C;
         # one key held for two buttons (posted keys reach PCSX2 one at a time; the lab ini binds T to TRIANGLE and
         # CROSS, Y to L2 and R2)
         tricross=0x54; l2r2=0x59 }
$extended = @(0x25, 0x26, 0x27, 0x28)

function KeyMsg([IntPtr]$h, [int]$code, [bool]$up) {
  $scan = [BG]::MapVirtualKey($code, 0)
  $l = 1 -bor ($scan -shl 16)
  if ($extended -contains $code) { $l = $l -bor (1 -shl 24) }
  if ($up) { $l = $l -bor (1 -shl 30) -bor (1 -shl 31) }
  $msg = if ($up) { 0x0101 } else { 0x0100 } # WM_KEYUP / WM_KEYDOWN
  [BG]::Post($h, $msg, [int64]$code, [int64]([uint32]$l))
}
# The key goes to every window of PCSX2's main window (the frame and the display inside it); Qt delivers it to the
# widget that holds the window's focus, which is the game display.
function Targets {
  switch ($env:PS2BG_TARGET) {
    'children' { return @([BG]::Children($script:main)) }
    'all' { $t = @($script:main); $t += [BG]::Children($script:main); return $t }
    default { return @($script:main) } # the frame: Qt hands the key to the game display, which holds its focus
  }
}
function Down([int]$code) { foreach ($h in (Targets)) { KeyMsg $h $code $false } }
function Up([int]$code) { foreach ($h in (Targets)) { KeyMsg $h $code $true } }
function Press([int]$code, [int]$ms = 100) { Down $code; Start-Sleep -Milliseconds $ms; Up $code; Start-Sleep -Milliseconds 120 }

if ($Attach) {
  $p = Get-Process pcsx2-qt -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $exe } | Select-Object -First 1
  if (-not $p) { "no running lab PCSX2 to attach to"; return }
  $pid2 = $p.Id; "attached to pid $pid2"
} else {
  $fgBefore = [BG]::GetForegroundWindow()
  if (-not $env:PS2BG_NODESK) { if ([BG]::OpenDesk()) { "on the lab's own desktop ($([BG]::DeskName)): it cannot take the focus or show" } else { "could not make the lab desktop; running parked off screen" } }
  $launchArgs = $(if ($Bios) { "-bios" } else { "-fastboot -elf `"$Elf`"" }) # -Bios: the console's own menu (the browser), no ELF
  # PS2BG_SLOWBOOT=1: the BIOS intro before the ELF, so buttons held from the start are down when it first reads the pad
  if ($env:PS2BG_SLOWBOOT -and -not $Bios) { $launchArgs = "-slowboot -elf `"$Elf`"" }
  if ($Iso) { $launchArgs += " `"$Iso`"" }
  if (-not $NoPanel) { [LabPanel]::Start($(if ($Title) { $Title } else { $(if ($Bios) { "BIOS" } else { Split-Path -Leaf (Split-Path -Parent $Elf) }) }), $exe) }
  $pid2 = [BG]::Launch($exe, $launchArgs, $lab)
  if ($pid2 -le 0) { "could not start PCSX2"; [LabPanel]::Finish(); return }
  "launched pid $pid2 (minimized, not activated)"
  # -Keep leaves PCSX2 running for a later -Attach, so only a run that closes it is tied to this process
  if (-not $Keep) { if ([BG]::TieToThisProcess($pid2)) { "tied to this run: ending it (Task Manager too) ends PCSX2" } }
}
if ($Attach -and -not $NoPanel) { [LabPanel]::Start($(if ($Title) { $Title } else { "attached" }), $exe) }
$script:main = [IntPtr]::Zero
for ($i = 0; $i -lt 60 -and $script:main -eq [IntPtr]::Zero; $i++) { Start-Sleep -Milliseconds 250; $script:main = [BG]::MainWindowOnDesk($pid2) }
if ($script:main -eq [IntPtr]::Zero) { "no PCSX2 window appeared"; [LabPanel]::Finish(); return }
[LabPanel]::Target = $script:main
if (-not $Attach) {
  Start-Sleep -Milliseconds 400
  [BG]::ParkOnDesk($script:main, 1300, 1060)
  "parked off screen: $([BG]::Info($script:main))"
  if ([BG]::GetForegroundWindow() -ne $fgBefore) { "note: the foreground window changed during launch" }
}
# A PCSX2 message box over the main window takes every key the run sends (10/25: one did, unseen, for hours). Each is
# grabbed to grabs\dialog_*.png, named in the output, and closed with Return, before the next step.
$script:dialogsSeen = 0
function Dialogs {
  foreach ($d in [BG]::Dialogs($pid2, $script:main)) {
    $script:dialogsSeen++
    $file = Join-Path $grabDir ("dialog_{0}.png" -f (Get-Date -Format 'HHmmss_fff'))
    $shot = if ([BG]::GrabOnDesk($d, $file)) { $file } else { "(no grab)" }
    "PCSX2 DIALOG over the game: $([BG]::Info($d)), grabbed to $shot; closing it"
    [BG]::Post($d, 0x0010, 0, 0) # WM_CLOSE: a key would not reach it (the box is no more active than PCSX2 is)
    Start-Sleep -Milliseconds 400
  }
  if ($script:dialogsSeen -and @([BG]::Dialogs($pid2, $script:main)).Count) { "a PCSX2 dialog is still open: keys will not reach the game" }
}
Dialogs
Press 0x10 # an unbound key (Shift) first, so the first real press is not lost

# a wait the panel's buttons can cut short
function Waiting([double]$sec) {
  $end = (Get-Date).AddSeconds($sec)
  while ((Get-Date) -lt $end) { if ([LabPanel]::Request -ne 0) { return }; Start-Sleep -Milliseconds 100 }
}
$list = @(($Steps -split ',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$recOn = $false
for ($n = 0; $n -lt $list.Count; $n++) {
  if ([LabPanel]::Request -ne 0) { break }
  $s = $list[$n]
  if ($s -notlike 'wait:*') { Dialogs } # a box that came up since the last step would take this one's keys
  [LabPanel]::Status = "step $($n + 1) of $($list.Count): $s"
  if ($s -like 'wait:*') { Waiting ([double]($s.Split(':')[1])); continue }
  if ($s -eq 'rec') { $recOn = -not $recOn }
  if ($s -like 'burst:*') {
    $burstDir = if ($env:PS2BG_BURST) { $env:PS2BG_BURST } else { Join-Path $grabDir ("burst_{0}" -f (Get-Date -Format 'HHmmss')) }
    New-Item -ItemType Directory -Force $burstDir | Out-Null
    "burst $burstDir : $([BG]::BurstOnDesk($script:main, $burstDir, [double]($s.Split(':')[1]))) frames"
    continue
  }
  if ($s -eq 'grab') {
    $file = Join-Path $grabDir ("grab_{0}.png" -f (Get-Date -Format 'HHmmss_fff'))
    if ([BG]::GrabOnDesk($script:main, $file)) { "grab $file" } else { "grab failed" }
    continue
  }
  if ($s -eq 'shot') {
    # until PCSX2's new PNG is there and holds still (it is written in the background: a run that closed PCSX2
    # 1.3 s after its last F8 left that screenshot cut short), at most 6 s
    $snapDir = Join-Path $lab "snaps"; $t0 = (Get-Date).AddSeconds(-0.5)
    Press $vk.f8
    $shotFile = $null; $last = -1
    for ($w = 0; $w -lt 30; $w++) {
      Start-Sleep -Milliseconds 200
      if (-not $shotFile) { $shotFile = Get-ChildItem -LiteralPath $snapDir -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $t0 } | Sort-Object LastWriteTime | Select-Object -Last 1 }
      if ($shotFile) { $now = (Get-Item -LiteralPath $shotFile.FullName).Length; if ($now -gt 0 -and $now -eq $last) { break }; $last = $now }
    }
    if ($w -lt 5) { Start-Sleep -Milliseconds (1000 - 200 * $w) } # the old pace, for step lists timed around it
    "shot" + $(if ($shotFile) { " $($shotFile.Name) ($last bytes)" } else { " (no file seen)" }); continue
  }
  if ($s -eq 'sstate') { Press $vk.f1; Start-Sleep -Milliseconds 2500; "save state (F1, lab sstates)"; continue }
  if ($s -like 'kdown:*') { Down $vk[$s.Split(':')[1]]; "kdown $($s.Split(':')[1])"; continue }
  if ($s -like 'kup:*') { Up $vk[$s.Split(':')[1]]; "kup $($s.Split(':')[1])"; continue }
  if ($s -like 'hold:*') { $a = $s.Split(':'); Press $vk[$a[1]] ([int]$a[2]); "hold $($a[1])"; continue }
  if ($vk.ContainsKey($s)) { Press $vk[$s]; "press $s" } else { "unknown step '$s'" }
}

if ([LabPanel]::Request -eq 2 -and -not $Attach) {
  # take over: finish a recording so its file is whole, save a state, and reopen PCSX2 on the user's desktop there
  [LabPanel]::Status = "taking over"
  if ($recOn) { Press $vk.rec; Start-Sleep -Milliseconds 1500 }
  $sst = Join-Path $lab "sstates"; $t0 = (Get-Date).AddSeconds(-1)
  Press $vk.f1
  $state = $null
  for ($i = 0; $i -lt 50 -and -not $state; $i++) {
    Start-Sleep -Milliseconds 200
    $state = Get-ChildItem -LiteralPath $sst -Filter *.p2s -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $t0 } | Sort-Object LastWriteTime | Select-Object -Last 1
  }
  if ($state) { # until its size holds still: the state is written in the background
    $last = -1; for ($i = 0; $i -lt 30; $i++) { $now = (Get-Item -LiteralPath $state.FullName).Length; if ($now -eq $last) { break }; $last = $now; Start-Sleep -Milliseconds 300 }
  }
  Stop-Process -Id $pid2 -Force -ErrorAction SilentlyContinue
  $openArgs = @("-fastboot", "-elf", "`"$Elf`"")
  if ($state) { $openArgs += @("-statefile", "`"$($state.FullName)`"") }
  if ($Iso) { $openArgs += "`"$Iso`"" }
  $mine = Start-Process -FilePath $exe -ArgumentList $openArgs -WorkingDirectory $lab -PassThru
  "taken over: PCSX2 is open on your desktop (pid $($mine.Id))" + $(if ($state) { ", at the state $($state.Name)" } else { ", from boot (no state was saved)" })
} elseif ([LabPanel]::Request -eq 1) {
  if ($recOn) { Press $vk.rec; Start-Sleep -Milliseconds 1500 }
  if (-not $Attach) { Stop-Process -Id $pid2 -Force -ErrorAction SilentlyContinue }
  "stopped from the panel" + $(if (-not $Attach) { "; PCSX2 closed" } else { "" })
} elseif (-not $Keep) {
  Stop-Process -Id $pid2 -Force -ErrorAction SilentlyContinue
  "PCSX2 closed"
}
[LabPanel]::Finish()
