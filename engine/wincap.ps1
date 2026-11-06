# Real Windows screen capture for TM Diamond videos (runs on a GitHub Actions Windows runner).
# A capture script (capture/<name>.ps1) dot-sources this file and calls the helpers below.
# Every Shot saves a real screenshot (PNG, no cursor) to captures/<name>/NNN_<label>.png and logs it,
# with the cursor position and any UI rectangles, to captures/<name>/shots.json. The editor
# (engine/realcut.py) animates a cursor, zooms and callouts on top of these real screens.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms, System.Drawing, UIAutomationClient, UIAutomationTypes
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class W {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint f, IntPtr e);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hh, bool r);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Ansi)]
  public struct DEVMODE {
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmDeviceName;
    public short dmSpecVersion; public short dmDriverVersion; public short dmSize; public short dmDriverExtra; public int dmFields;
    public int dmPositionX; public int dmPositionY; public int dmDisplayOrientation; public int dmDisplayFixedOutput;
    public short dmColor; public short dmDuplex; public short dmYResolution; public short dmTTOption; public short dmCollate;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmFormName;
    public short dmLogPixels; public int dmBitsPerPel; public int dmPelsWidth; public int dmPelsHeight;
    public int dmDisplayFlags; public int dmDisplayFrequency; public int dmICMMethod; public int dmICMIntent;
    public int dmMediaType; public int dmDitherType; public int dmReserved1; public int dmReserved2; public int dmPanningWidth; public int dmPanningHeight;
  }
  [DllImport("user32.dll")] public static extern int EnumDisplaySettings(string d, int m, ref DEVMODE dm);
  [DllImport("user32.dll")] public static extern int ChangeDisplaySettings(ref DEVMODE dm, int f);
  public static int SetRes(int w, int h) {
    DEVMODE dm = new DEVMODE(); dm.dmSize = (short)Marshal.SizeOf(typeof(DEVMODE));
    EnumDisplaySettings(null, -1, ref dm);
    dm.dmPelsWidth = w; dm.dmPelsHeight = h; dm.dmFields = 0x80000 | 0x100000;
    return ChangeDisplaySettings(ref dm, 0);
  }
}
"@
[void][W]::SetProcessDPIAware()

$script:Out = $null
$script:Log = New-Object System.Collections.ArrayList
$script:N = 0  # NOTE: PowerShell names are case-insensitive - never use $n in capture scripts

function Init-Capture([string]$Name, [int]$Width = 1920, [int]$Height = 1080) {
  $r = [W]::SetRes($Width, $Height)
  Start-Sleep -Milliseconds 800
  $script:Out = Join-Path (Get-Location) "captures/$Name"
  New-Item -ItemType Directory -Force -Path $script:Out | Out-Null
  $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  Write-Host "SetRes=$r screen=$($b.Width)x$($b.Height)"
  # keep the desktop clean: minimise everything that is open
  (New-Object -ComObject Shell.Application).MinimizeAll()
  Start-Sleep -Milliseconds 800
}

function Get-FgRect {
  $h = [W]::GetForegroundWindow(); $r = New-Object W+RECT
  [void][W]::GetWindowRect($h, [ref]$r)
  $sb = New-Object System.Text.StringBuilder 256; [void][W]::GetWindowText($h, $sb, 256)
  return @{ x = $r.Left; y = $r.Top; w = $r.Right - $r.Left; h = $r.Bottom - $r.Top; title = $sb.ToString() }
}

function Find-Rect([string]$Name) {
  # bounding box of the first UI element with this accessible name (or $null)
  try {
    $root = [System.Windows.Automation.AutomationElement]::RootElement
    $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Name)
    $el = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
    if ($null -eq $el) { return $null }
    $b = $el.Current.BoundingRectangle
    return @{ x = [int]$b.X; y = [int]$b.Y; w = [int]$b.Width; h = [int]$b.Height; name = $Name }
  } catch { return $null }
}

function Shot([string]$Label, [hashtable]$Rects = @{}, [string]$Note = '') {
  $script:N++
  $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
  $file = ('{0:D3}_{1}.png' -f $script:N, $Label)
  $bmp.Save((Join-Path $script:Out $file), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
  $p = [System.Windows.Forms.Cursor]::Position
  $fg = Get-FgRect
  [void]$script:Log.Add(@{ i = $script:N; label = $Label; file = $file; cursor = @($p.X, $p.Y); fg = $fg; rects = $Rects; note = $Note })
  Write-Host "shot $file  fg='$($fg.title)' $($fg.x),$($fg.y) $($fg.w)x$($fg.h)"
}

function Save-Log {
  $script:Log | ConvertTo-Json -Depth 6 | Set-Content -Encoding utf8 (Join-Path $script:Out 'shots.json')
}

function Move-To([int]$X, [int]$Y) { [void][W]::SetCursorPos($X, $Y); Start-Sleep -Milliseconds 120 }
function Click([int]$X, [int]$Y) {
  Move-To $X $Y
  [W]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero); Start-Sleep -Milliseconds 60
  [W]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero); Start-Sleep -Milliseconds 400
}
function Key-Combo([byte[]]$Vks) {
  foreach ($v in $Vks) { [W]::keybd_event($v, 0, 0, [IntPtr]::Zero); Start-Sleep -Milliseconds 40 }
  [array]::Reverse($Vks)
  foreach ($v in $Vks) { [W]::keybd_event($v, 0, 2, [IntPtr]::Zero); Start-Sleep -Milliseconds 40 }
  Start-Sleep -Milliseconds 300
}
# virtual key codes
$VK = @{ WIN = 0x5B; CTRL = 0x11; SHIFT = 0x10; ALT = 0x12; ENTER = 0x0D; ESC = 0x1B; TAB = 0x09; R = 0x52; V = 0x56; E = 0x45; I = 0x49; X = 0x58 }

function Type-Shots([string]$Text, [string]$Label, [hashtable]$Rects = @{}) {
  # types one character at a time and takes a real screenshot after each one
  foreach ($ch in $Text.ToCharArray()) {
    $k = [string]$ch
    if ('+^%~(){}[]'.Contains($k)) { $k = '{' + $k + '}' }
    [System.Windows.Forms.SendKeys]::SendWait($k)
    Start-Sleep -Milliseconds 90
    Shot "$Label" $Rects "typed:$ch"
  }
}

function Place-Foreground([int]$X, [int]$Y, [int]$Wd, [int]$Ht) {
  $h = [W]::GetForegroundWindow(); [void][W]::MoveWindow($h, $X, $Y, $Wd, $Ht, $true); Start-Sleep -Milliseconds 500
}

function Find-RectLike([string]$Pattern, [string]$Type = '') {
  # bounding box of the first UI element in the foreground window whose accessible name matches the regex
  # (optionally only of one control type, e.g. 'HeaderItem', 'Button', 'TreeItem', 'ListItem', 'DataItem')
  try {
    $h = [W]::GetForegroundWindow()
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
    $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($el in $all) {
      $n = $el.Current.Name
      if (-not $n) { continue }
      if ($Type -and $el.Current.ControlType.ProgrammaticName -ne "ControlType.$Type") { continue }
      if ($n -match $Pattern) {
        $b = $el.Current.BoundingRectangle
        if ($b.Width -le 0) { continue }
        return @{ x = [int]$b.X; y = [int]$b.Y; w = [int]$b.Width; h = [int]$b.Height; name = $n }
      }
    }
  } catch { }
  return $null
}

function Set-DarkMode {
  # dark mode like the owner's own PC, then restart Explorer so the taskbar follows
  $p = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
  New-Item -Path $p -Force | Out-Null
  Set-ItemProperty -Path $p -Name AppsUseLightTheme -Value 0 -Type DWord
  Set-ItemProperty -Path $p -Name SystemUsesLightTheme -Value 0 -Type DWord
  Get-Process explorer -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep -Seconds 4
  (New-Object -ComObject Shell.Application).MinimizeAll()
  Start-Sleep -Seconds 1
}
function Center($r) { return @([int]($r.x + $r.w / 2), [int]($r.y + $r.h / 2)) }
