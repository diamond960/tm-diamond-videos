# tiktok02: 6 ways to make a slow Windows 11 PC faster (plan block 1) - all steps on a real Windows PC, dark mode.
# 1 Task Manager > Startup apps > Disable   2 Processes > Windows Explorer > Restart task
# 3 CPU column sort > End task               4 Settings > Accessibility > Visual effects (animation + transparency off)
# 5 Settings > System > Storage > Storage Sense on + schedule   6 Settings > Apps > Installed apps > sort by size > ... > Uninstall (menu only)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'tiktok02'
Set-DarkMode
$exe = New-HeavyApp
# an app that starts with Windows (registered the normal way, in the user's Run key) and is running now
$run = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
if (-not (Test-Path $run)) { New-Item -Path $run | Out-Null }
New-ItemProperty -Path $run -Name 'HeavyApp' -Value "`"$exe`"" -PropertyType String -Force | Out-Null
Start-Process explorer.exe $exe; Start-Sleep -Seconds 3
# a File Explorer window, so Windows Explorer is listed under Apps
Start-Process explorer.exe; Start-Sleep -Seconds 3
(New-Object -ComObject Shell.Application).MinimizeAll(); Start-Sleep -Seconds 1

# ---------- 1 Startup apps
Move-To 1300 760
Key-Combo @($VK.CTRL, $VK.SHIFT, $VK.ESC); Start-Sleep -Seconds 4
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
$nav = Find-RectLike '^Startup apps' 'ListItem'
if (-not $nav) { $nav = Find-RectLike '^Startup apps' }
$navp = Find-RectLike '^Processes' 'ListItem'
if (-not $navp) { $navp = Find-RectLike '^Processes' }
Shot 'tm_open' @{ nav = $nav; navp = $navp }
Dump-Names 'tm_open'
if ($nav) { $c = Center $nav; Click $c[0] $c[1]; Start-Sleep -Seconds 3 }
$row = Find-RectLike '^HeavyApp'
Shot 'startup_list' @{ nav = $nav; row = $row }
Dump-Names 'startup_list'
if ($row) {
  Click ($row.x + 120) ([int]($row.y + $row.h / 2)); Start-Sleep -Seconds 1
  $dis = Find-Rect 'Disable'
  Shot 'startup_selected' @{ row = $row; disable = $dis }
  if ($dis) { $c = Center $dis; Click $c[0] $c[1]; Start-Sleep -Seconds 2 }
}
$row = Find-RectLike '^HeavyApp'
Shot 'startup_disabled' @{ row = $row }

# ---------- 2 Restart Windows Explorer
if ($navp) { $c = Center $navp; Click $c[0] $c[1]; Start-Sleep -Seconds 3 }
Move-To 1300 760
$wex = Find-RectLike '^Windows Explorer'
$cpu = Find-RectLike 'CPU' 'HeaderItem'
Shot 'processes' @{ navp = $navp; wex = $wex; cpu = $cpu }
Dump-Names 'processes'
if ($wex) {
  $c = Center $wex; Click ($wex.x + 120) $c[1]; Start-Sleep -Seconds 1
  $rs = Find-Rect 'Restart task'
  if (-not $rs) { $rs = Find-RectLike '^Restart' 'Button' }
  Shot 'wex_selected' @{ wex = $wex; restart = $rs }
  Dump-Names 'wex_selected'
  if ($rs) { $c = Center $rs; Click $c[0] $c[1]; Start-Sleep -Seconds 1; Shot 'restarting' @{ restart = $rs }; Start-Sleep -Seconds 4 }
}
Shot 'after_restart' @{}

# ---------- 3 Sort by CPU, End task
$cpu = Find-RectLike 'CPU' 'HeaderItem'
if ($cpu) { $c = Center $cpu; Click $c[0] $c[1]; Start-Sleep -Seconds 3 }
Move-To 1300 760
$hog = Find-RectLike '^HeavyApp'
Shot 'sorted_cpu' @{ cpu = $cpu; hog = $hog }
Dump-Names 'sorted_cpu'
if ($hog) {
  $c = Center $hog; Click ($hog.x + 120) $c[1]; Start-Sleep -Seconds 1
  $end = Find-Rect 'End task'
  Shot 'hog_selected' @{ hog = $hog; end = $end }
  if ($end) { $e = Center $end; Click $e[0] $e[1]; Start-Sleep -Seconds 3 }
}
Get-Process HeavyApp -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Shot 'hog_ended' @{ cpu = $cpu }
Get-Process Taskmgr -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# ---------- 4 Visual effects
function Get-El([string]$Pattern, [string]$Type) {
  $h = [W]::GetForegroundWindow(); $root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
  $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
  foreach ($el in $all) { if ($el.Current.Name -match $Pattern -and $el.Current.ControlType.ProgrammaticName -eq "ControlType.$Type") { return $el } }
  return $null
}
function Set-Toggle([string]$Pattern, [string]$Want) {
  $el = Get-El $Pattern 'Button'
  if ($el) { try { $tp = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
    if ($tp.Current.ToggleState.ToString() -ne $Want) { $tp.Toggle(); Start-Sleep -Seconds 2 } } catch { Write-Host "toggle failed $Pattern" } }
}
Start-Process 'ms-settings:easeofaccess-visualeffects'; Start-Sleep -Seconds 6
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
# this virtual machine starts with both effects off; switch them on first (the way a normal PC ships) so the video shows the real "turn off" click
Set-Toggle '^Animation effects' 'On'; Set-Toggle '^Transparency effects' 'On'
Start-Sleep -Seconds 1
Move-To 1300 760
$an = Find-RectLike '^Animation effects' 'Button'
$tr = Find-RectLike '^Transparency effects' 'Button'
Shot 'visual_on' @{ animation = $an; transparency = $tr }
Dump-Names 'visual_on'
if ($an) { $c = Center $an; Click $c[0] $c[1]; Start-Sleep -Seconds 2; Shot 'animation_off' @{ animation = $an; transparency = $tr } }
if ($tr) { $c = Center $tr; Click $c[0] $c[1]; Start-Sleep -Seconds 2; Shot 'transparency_off' @{ animation = $an; transparency = $tr } }

# ---------- 5 Storage Sense
Start-Process 'ms-settings:storagepolicies'; Start-Sleep -Seconds 6
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
# this virtual machine has it on already; switch it off first so the video shows the real "turn on" click
Set-Toggle '^Storage Sense runs' 'Off'
Move-To 1300 760
$tg = Find-RectLike '^Storage Sense runs' 'Button'
Shot 'sense_off' @{ toggle = $tg }
Dump-Names 'sense_off'
if ($tg) { $c = Center $tg; Click $c[0] $c[1]; Start-Sleep -Seconds 2 }
Shot 'sense_on' @{ toggle = $tg }
$combo = Find-RectLike '^Run Storage Sense' 'ComboBox'
if (-not $combo) { $combo = Find-RectLike '.' 'ComboBox' }
if ($combo) {
  $c = Center $combo; Click $c[0] $c[1]; Start-Sleep -Seconds 1
  $wk = Find-RectLike '^Every week$'
  if (-not $wk) { $wk = Find-Anywhere '^Every week$' }
  Shot 'schedule_open' @{ combo = $combo; week = $wk }
  Dump-Names 'schedule_open'
  if ($wk) { $k = Center $wk; Click $k[0] $k[1]; Start-Sleep -Seconds 1 }
}
Move-To 1300 760
Shot 'sense_final' @{ toggle = $tg; combo = $combo }

# ---------- 6 Installed apps
Start-Process 'ms-settings:appsfeatures'; Start-Sleep -Seconds 7
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 3
Move-To 1300 760
$sort = Find-RectLike '^Sort options' 'ComboBox'
if (-not $sort) { $sort = Find-RectLike '^Sort' 'ComboBox' }
Shot 'apps' @{ sort = $sort }
Dump-Names 'apps'
if ($sort) {
  $c = Center $sort; Click $c[0] $c[1]; Start-Sleep -Seconds 1
  $big = Find-RectLike '^Size \(large to small\)'
  if (-not $big) { $big = Find-Anywhere '^Size \(large to small\)' }
  Shot 'sort_open' @{ sort = $sort; big = $big }
  if ($big) { $b = Center $big; Click $b[0] $b[1]; Start-Sleep -Seconds 3 }
}
Move-To 1300 760
$more = Find-RectLike '^More options' 'Button'
if (-not $more) { $more = Find-RectLike 'options' 'Button' }
Shot 'sorted' @{ sort = $sort; more = $more }
Dump-Names 'sorted'
if ($more) {
  $c = Center $more; Click $c[0] $c[1]; Start-Sleep -Seconds 1
  $un = Find-RectLike '^Uninstall$'
  if (-not $un) { $un = Find-Anywhere '^Uninstall$' }
  Shot 'menu' @{ more = $more; uninstall = $un }
  Dump-Names 'menu'
  if ($un) { $u = Center $un; Move-To $u[0] $u[1]; Shot 'hover_uninstall' @{ uninstall = $un } }
  Key-Combo @($VK.ESC)
}
Save-Log
