# long02 section 6: Performance Options > Adjust for best performance (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long02_04'
Set-DarkMode
Start-Process SystemPropertiesPerformance.exe; Start-Sleep -Seconds 4
Dismiss-Popups; Start-Sleep -Seconds 2
$po = Find-Anywhere '^Performance Options$'
Place-Foreground 610 180 640 720; Start-Sleep -Seconds 1
Move-To 1500 800
$best = Find-RectLike '^Adjust for best performance' 'RadioButton'
if (-not $best) { $best = Find-RectLike '^Adjust for best performance' }
$ok = Find-RectLike '^OK$' 'Button'
Shot 'dialog' @{ best = $best; ok = $ok; po = $po }
Dump-Names 'dialog'
if ($best) { $c = Center $best; Move-To ($best.x + 8) $c[1]; Shot 'hover_best' @{ best = $best }; Click ($best.x + 8) $c[1]; Start-Sleep -Seconds 1 }
Shot 'best_selected' @{ best = $best; ok = $ok }
Dump-Names 'best_selected'
if ($ok) { $c = Center $ok; Move-To $c[0] $c[1]; Shot 'hover_ok' @{ ok = $ok }; Click $c[0] $c[1]; Start-Sleep -Seconds 4 }
Dismiss-Popups
Shot 'applied' @{}
Save-Log
