# long02 section 3: Task Manager > Processes > Windows Explorer > Restart task (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long02_02'
Set-DarkMode
Start-Process explorer.exe; Start-Sleep -Seconds 3
(New-Object -ComObject Shell.Application).MinimizeAll(); Start-Sleep -Seconds 1
Key-Combo @($VK.CTRL, $VK.SHIFT, $VK.ESC); Start-Sleep -Seconds 4
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
$row = Find-RectLike '^Windows Explorer'
Shot 'processes' @{ row = $row }
Dump-Names 'processes'
if ($row) {
  $c = Center $row; Move-To ($row.x + 120) $c[1]; Shot 'hover_row' @{ row = $row }
  Click ($row.x + 120) $c[1]; Start-Sleep -Seconds 1
  $rs = Find-Rect 'Restart task'
  if (-not $rs) { $rs = Find-RectLike '^Restart' 'Button' }
  Shot 'selected' @{ row = $row; restart = $rs }
  Dump-Names 'selected'
  if ($rs) { $c = Center $rs; Move-To $c[0] $c[1]; Shot 'hover_restart' @{ restart = $rs }; Click $c[0] $c[1]; Start-Sleep -Seconds 1; Shot 'restarting' @{}; Start-Sleep -Seconds 4 }
}
Shot 'after' @{}
Save-Log
