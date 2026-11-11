# long02 section 6: Performance Options > Adjust for best performance (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long02_04'
Set-DarkMode
Start-Process SystemPropertiesPerformance.exe; Start-Sleep -Seconds 4
Place-Foreground 610 200 700 720; Start-Sleep -Seconds 1
$best = Find-RectLike '^Adjust for best performance'
$apply = Find-Rect 'Apply'
$ok = Find-Rect 'OK'
Shot 'dialog' @{ best = $best; apply = $apply; ok = $ok }
Dump-Names 'dialog'
if ($best) { $c = Center $best; Move-To ($best.x + 10) $c[1]; Shot 'hover_best' @{ best = $best }; Click ($best.x + 10) $c[1]; Start-Sleep -Seconds 1 }
Shot 'best_selected' @{ best = $best; apply = $apply; ok = $ok }
if ($ok) { $c = Center $ok; Move-To $c[0] $c[1]; Shot 'hover_ok' @{ ok = $ok }; Click $c[0] $c[1]; Start-Sleep -Seconds 3 }
Shot 'applied' @{}
Save-Log
