# long02 section 10: Optimize Drives (dfrgui) > C: > Optimize (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long02_07'
Set-DarkMode
Start-Process dfrgui.exe; Start-Sleep -Seconds 5
Place-Foreground 360 170 1200 760; Start-Sleep -Seconds 2
Move-To 1300 860
$c = Find-RectLike '^\(C:\)|^Windows \(C:\)|C:'
$opt = Find-Rect 'Optimize'
Shot 'window' @{ drive = $c; optimize = $opt }
Dump-Names 'window'
if ($c) { $cc = Center $c; Click $cc[0] $cc[1]; Start-Sleep -Seconds 1 }
$opt = Find-Rect 'Optimize'
Shot 'drive_selected' @{ drive = $c; optimize = $opt }
if ($opt) { $o = Center $opt; Move-To $o[0] $o[1]; Shot 'hover_optimize' @{ optimize = $opt }; Click $o[0] $o[1]; Start-Sleep -Seconds 4; Shot 'optimizing' @{ drive = $c }; Start-Sleep -Seconds 20 }
Shot 'done' @{ drive = $c }
Dump-Names 'done'
Save-Log
