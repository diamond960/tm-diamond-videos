# long02 section 8: Settings > System > Storage > Storage Sense on + schedule (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long02_05'
Set-DarkMode
Start-Process 'ms-settings:storagepolicies'; Start-Sleep -Seconds 6
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
Move-To 1300 760
$tg = Find-RectLike 'Storage Sense' 'Button'
Shot 'page' @{ toggle = $tg }
Dump-Names 'page'
if ($tg) { $c = Center $tg; Move-To $c[0] $c[1]; Shot 'hover_toggle' @{ toggle = $tg }; Click $c[0] $c[1]; Start-Sleep -Seconds 2 }
Shot 'on' @{ toggle = $tg }
Dump-Names 'on'
$combo = Find-RectLike '.' 'ComboBox'
if ($combo) {
  $c = Center $combo; Move-To $c[0] $c[1]; Click $c[0] $c[1]; Start-Sleep -Seconds 1
  Shot 'schedule_open' @{ combo = $combo }
  Dump-Names 'schedule_open'
  Key-Combo @($VK.ESC); Start-Sleep -Milliseconds 600
}
Shot 'final' @{ toggle = $tg; combo = $combo }
Save-Log
