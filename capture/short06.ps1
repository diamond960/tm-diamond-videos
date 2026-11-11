# short06: Settings > System > For developers > End task, then right-click Notepad on the taskbar > End task, and Notepad closes.
# (real Windows, dark mode). Re-capture of long02 fix 4 with the after-click frame, which the long02 run missed.
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'short06'
Set-DarkMode
Start-Process 'ms-settings:developers'; Start-Sleep -Seconds 5
Dismiss-Popups
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
$tg = Find-RectLike '^End task' 'Button'
if (-not $tg) { $tg = Find-RectLike '^End task' }
Move-To 1300 700
Shot 'dev_page' @{ toggle = $tg }
Dump-Names 'dev_page'
if ($tg) { $c = Center $tg; Move-To $c[0] $c[1]; Shot 'hover_toggle' @{ toggle = $tg }; Click $c[0] $c[1]; Start-Sleep -Seconds 2 }
$tg2 = Find-RectLike '^End task' 'Button'
Shot 'toggle_on' @{ toggle = $tg2 }
# a running app on the taskbar
Start-Process notepad.exe; Start-Sleep -Seconds 4
(New-Object -ComObject Shell.Application).MinimizeAll(); Start-Sleep -Seconds 1
Dismiss-Popups; Start-Sleep -Milliseconds 600
$tb = Find-Anywhere '^Notepad.*running'
if (-not $tb) { $tb = Find-Anywhere '^Notepad' }
Move-To 1500 700
Shot 'taskbar' @{ tb = $tb }
if ($tb) {
  $c = Center $tb
  Move-To $c[0] $c[1]; Shot 'hover_tb' @{ tb = $tb }
  Right-Click $c[0] $c[1]; Start-Sleep -Seconds 1
  $et = Find-Anywhere '^End task$'
  Shot 'jumplist' @{ tb = $tb; endtask = $et }
  Dump-Names 'jumplist'
  # the jump list's End task row sits about 77 px left of and 87 px above the taskbar button centre (long02 capture)
  if ($et) { $e = Center $et } else { $e = @(($c[0] - 77), ($c[1] - 87)) }
  Move-To $e[0] $e[1]; Start-Sleep -Milliseconds 400
  Shot 'hover_endtask' @{ endtask = $et } "endtask at $($e[0]),$($e[1])"
  Click $e[0] $e[1]; Start-Sleep -Seconds 3
  Dismiss-Popups
  Move-To 1500 700; Start-Sleep -Milliseconds 400
  $left = @(Get-Process notepad -ErrorAction SilentlyContinue).Count
  Shot 'closed' @{ tb = $tb } "notepad processes left: $left"
}
Save-Log
