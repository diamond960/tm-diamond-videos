# fb08: "Free up space without deleting your files" - Settings > System > Storage > Temporary files > Remove files (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'fb08'
Set-DarkMode
# a little real junk in the user's Temp folder so the list is not empty
$tmpdir = Join-Path $env:TEMP 'old-installer-cache'
New-Item -ItemType Directory -Force -Path $tmpdir | Out-Null
foreach ($i in 1..6) { $f = [System.IO.File]::Create((Join-Path $tmpdir "setup_$i.tmp")); $f.SetLength(150MB); $f.Close() }

function Dump-Names([string]$Tag) {
  # log every named control in the foreground window (for exact boxes in the spec)
  $items = @()
  try {
    $h = [W]::GetForegroundWindow(); $root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
    $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($el in $all) {
      $nm = $el.Current.Name; if (-not $nm) { continue }
      $b = $el.Current.BoundingRectangle; if ($b.Width -le 0) { continue }
      $items += ('{0} | {1} | {2},{3},{4},{5}' -f $el.Current.ControlType.ProgrammaticName, $nm, [int]$b.X, [int]$b.Y, [int]$b.Width, [int]$b.Height)
    }
  } catch { }
  Set-Content -Encoding utf8 -Path (Join-Path $script:Out "names_$Tag.txt") -Value $items
}

Start-Process 'ms-settings:storagesense'
Start-Sleep -Seconds 6
Place-Foreground 160 90 1560 900
Start-Sleep -Seconds 8   # let Storage finish measuring
Move-To 1400 760
$tmp = Find-RectLike '^Temporary files' ''
$sys = Find-RectLike '^System$' ''
$sto = Find-RectLike '^Storage$' ''
Dump-Names 'storage'
Shot 'storage' @{ temp = $tmp; system = $sys; storage = $sto }
if (-not $tmp) { Start-Sleep -Seconds 6; $tmp = Find-RectLike '^Temporary files' ''; Dump-Names 'storage2'; Shot 'storage2' @{ temp = $tmp } }
if ($tmp) {
  $c = Center $tmp
  Move-To $c[0] $c[1]; Shot 'hover_temp' @{ temp = $tmp }
  Click $c[0] $c[1]
  Start-Sleep -Seconds 10   # the page scans the temp folders
  Move-To 1400 760
  $rm = Find-RectLike '^Remove files' 'Button'
  Dump-Names 'temp'
  Shot 'temp_page' @{ remove = $rm }
  # tick a safe category (never Downloads)
  $boxes = @()
  try {
    $h = [W]::GetForegroundWindow(); $root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
    $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::CheckBox)
    $boxes = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond)
  } catch { }
  foreach ($cb in $boxes) {
    $nm = $cb.Current.Name
    if ($nm -match '^Temporary files' -or $nm -match 'Delivery Optimization' -or $nm -match 'Thumbnails') {
      try {
        $tp = $cb.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
        if ($tp.Current.ToggleState -eq [System.Windows.Automation.ToggleState]::Off) {
          $b = $cb.Current.BoundingRectangle
          $r = @{ x = [int]$b.X; y = [int]$b.Y; w = [int]$b.Width; h = [int]$b.Height; name = $nm }
          Click ([int]($b.X + 12)) ([int]($b.Y + $b.Height / 2)); Start-Sleep -Milliseconds 900
          Shot 'ticked' @{ box = $r }
        }
      } catch { Write-Host "toggle failed $nm" }
    }
  }
  $rm = Find-RectLike '^Remove files' 'Button'
  Dump-Names 'temp_ticked'
  Shot 'ready' @{ remove = $rm }
  if ($rm) {
    $c = Center $rm
    Move-To $c[0] $c[1]; Shot 'hover_remove' @{ remove = $rm }
    Click $c[0] $c[1]
    Start-Sleep -Seconds 2
    $cont = Find-Rect 'Continue'
    Dump-Names 'confirm'
    Shot 'confirm' @{ remove = $rm; cont = $cont }
    if ($cont) { $c = Center $cont; Move-To $c[0] $c[1]; Click $c[0] $c[1] }
    Start-Sleep -Seconds 12
    Move-To 1400 760
    Dump-Names 'done'
    Shot 'done' @{ remove = (Find-RectLike '^Remove files' 'Button') }
    Start-Sleep -Seconds 5
    Shot 'done2' @{}
  } else { Write-Host 'Remove files button not found' }
} else { Write-Host 'Temporary files not found' }
Save-Log
