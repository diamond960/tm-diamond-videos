# long02 section 1: Task Manager > Startup apps > Disable (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long02_01'
Set-DarkMode
$exe = New-HeavyApp
# an app that starts with Windows (registered the normal way, in the user's Run key)
$run = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
if (-not (Test-Path $run)) { New-Item -Path $run | Out-Null }
New-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'HeavyApp' -Value "`"$exe`"" -PropertyType String -Force | Out-Null
Key-Combo @($VK.CTRL, $VK.SHIFT, $VK.ESC); Start-Sleep -Seconds 4
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
$nav = Find-RectLike '^Startup apps' 'ListItem'
if (-not $nav) { $nav = Find-RectLike '^Startup apps' }
Shot 'tm_open' @{ nav = $nav }
Dump-Names 'tm_open'
if ($nav) {
  $c = Center $nav; Move-To $c[0] $c[1]; Shot 'hover_nav' @{ nav = $nav }
  Click $c[0] $c[1]; Start-Sleep -Seconds 3
}
$row = Find-RectLike '^HeavyApp'
Shot 'startup_list' @{ nav = $nav; row = $row }
Dump-Names 'startup_list'
if ($row) {
  Click ($row.x + 120) ([int]($row.y + $row.h / 2)); Start-Sleep -Seconds 1
  $dis = Find-Rect 'Disable'
  Shot 'selected' @{ row = $row; disable = $dis }
  if ($dis) { $c = Center $dis; Move-To $c[0] $c[1]; Shot 'hover_disable' @{ disable = $dis }; Click $c[0] $c[1]; Start-Sleep -Seconds 2 }
}
$row = Find-RectLike '^HeavyApp'
Shot 'disabled' @{ row = $row }
Dump-Names 'disabled'
Save-Log
