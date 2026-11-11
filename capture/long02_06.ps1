# long02 section 9: Settings > Apps > Installed apps, sort by size, ... > Uninstall (menu only) (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long02_06'
Set-DarkMode
Start-Process 'ms-settings:appsfeatures'; Start-Sleep -Seconds 7
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 3
Move-To 1300 760
$sort = Find-RectLike '^Sort options' 'ComboBox'
Shot 'apps' @{ sort = $sort }
Dump-Names 'apps'
if ($sort) {
  $c = Center $sort; Move-To $c[0] $c[1]; Click $c[0] $c[1]; Start-Sleep -Seconds 1
  $big = Find-RectLike '^Size \(large to small\)'
  if (-not $big) { $big = Find-Anywhere '^Size \(large to small\)' }
  Shot 'sort_open' @{ sort = $sort; big = $big }
  Dump-Names 'sort_open'
  if ($big) { $b = Center $big; Move-To $b[0] $b[1]; Click $b[0] $b[1]; Start-Sleep -Seconds 3 }
}
Shot 'sorted' @{ sort = $sort }
Dump-Names 'sorted'
$more = Find-RectLike '^More options' 'Button'
if (-not $more) { $more = Find-RectLike 'options' 'Button' }
if ($more) {
  $c = Center $more; Move-To $c[0] $c[1]; Click $c[0] $c[1]; Start-Sleep -Seconds 1
  $un = Find-RectLike '^Uninstall$'
  Shot 'menu' @{ more = $more; uninstall = $un }
  Dump-Names 'menu'
  if ($un) { $u = Center $un; Move-To $u[0] $u[1]; Shot 'hover_uninstall' @{ uninstall = $un } }
  Key-Combo @($VK.ESC)
}
Save-Log
