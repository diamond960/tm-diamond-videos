# short04: "Windows hides a faster power mode" - Settings > System > Power > Power mode: Best performance (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'short04'
Set-DarkMode
Start-Process 'ms-settings:powersleep'
Start-Sleep -Seconds 5
Place-Foreground 160 110 1560 840
Start-Sleep -Seconds 2
$mode = Find-RectLike '^Power mode'
$combo = Find-RectLike '.' 'ComboBox'
Shot 'power_page' @{ mode = $mode; combo = $combo }
if ($combo) {
  $c = Center $combo; Move-To $c[0] $c[1]; Shot 'hover_combo' @{ combo = $combo }
  Click $c[0] $c[1]; Start-Sleep -Seconds 1
  $best = Find-Rect 'Best performance'
  Shot 'open_list' @{ combo = $combo; best = $best }
  if ($best) {
    $b = Center $best; Move-To $b[0] $b[1]; Shot 'hover_best' @{ best = $best }
    Click $b[0] $b[1]; Start-Sleep -Seconds 2
  }
}
$combo = Find-RectLike '.' 'ComboBox'
Shot 'best_set' @{ combo = $combo; mode = $mode }
Save-Log
