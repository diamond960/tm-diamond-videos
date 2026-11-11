# long02 section 4: Settings > System > For developers > End task, then right-click an app on the taskbar (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long02_03'
Set-DarkMode
Start-Process 'ms-settings:developers'; Start-Sleep -Seconds 5
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
$tg = Find-RectLike '^End task' 'Button'
if (-not $tg) { $tg = Find-RectLike '^End task' }
Move-To 1300 700
Shot 'dev_page' @{ toggle = $tg }
Dump-Names 'dev_page'
if ($tg) { $c = Center $tg; Move-To $c[0] $c[1]; Shot 'hover_toggle' @{ toggle = $tg }; Click $c[0] $c[1]; Start-Sleep -Seconds 2 }
$tg2 = Find-RectLike '^End task' 'Button'
Shot 'toggle_on' @{ toggle = $tg2 }
Dump-Names 'toggle_on'
# a running app on the taskbar
Start-Process notepad.exe; Start-Sleep -Seconds 3
(New-Object -ComObject Shell.Application).MinimizeAll(); Start-Sleep -Seconds 1
$tb = Find-Anywhere '^Notepad.*running'
if (-not $tb) { $tb = Find-Anywhere '^Notepad' }
Shot 'taskbar' @{ tb = $tb }
if ($tb) {
  $c = Center $tb; Right-Click $c[0] $c[1]; Start-Sleep -Seconds 1
  $et = Find-Anywhere '^End task$'
  Shot 'jumplist' @{ tb = $tb; endtask = $et }
  if ($et) { $e = Center $et; Move-To $e[0] $e[1]; Shot 'hover_endtask' @{ endtask = $et }; Click $e[0] $e[1]; Start-Sleep -Seconds 2 }
}
Shot 'closed' @{ tb = $tb }
Save-Log
