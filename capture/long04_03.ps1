# long04 section 3: snap layouts - hover the maximize button / Windows + Z, pick a zone, Snap Assist (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_03'
Set-DarkMode
function Send([string]$s) { [System.Windows.Forms.SendKeys]::SendWait($s); Start-Sleep -Milliseconds 300 }
Start-Process explorer.exe (Join-Path $env:USERPROFILE 'Documents'); Start-Sleep -Seconds 4
Place-Foreground 700 240 900 600; Start-Sleep -Seconds 1
Start-Process notepad.exe; Start-Sleep -Seconds 3
Place-Foreground 300 160 1000 640; Start-Sleep -Seconds 1
Send 'My notes for today{ENTER}'
Shot 'two_windows'
$max = Find-RectLike '^Maximize' 'Button'
if (-not $max) { $max = Find-RectLike '^Maximize' }
Write-Host "max=$($max.x),$($max.y)"
if ($max) {
  $c = Center $max; Move-To ($c[0] - 40) ($c[1] + 30); Start-Sleep -Milliseconds 300
  Move-To $c[0] $c[1]; Start-Sleep -Milliseconds 200; Move-To ($c[0] + 1) $c[1]; Start-Sleep -Seconds 2
  Shot 'hover_max' @{ max = $max }
  Dump-All 'hover_max'
  Move-To 1500 900; Start-Sleep -Seconds 1
}
# keyboard: Windows + Z opens the same layouts
$np = Get-Process notepad -ErrorAction SilentlyContinue | Select-Object -First 1
if ($np) { [void][W]::SetForegroundWindow($np.MainWindowHandle); Start-Sleep -Milliseconds 800 }
Key-Combo @($VK.WIN, 0x5A); Start-Sleep -Seconds 2
Shot 'winz' @{ max = $max }
Dump-All 'winz'
# pick layout 1, zone 1 (left half) with the number keys shown on the layouts
Send '1'; Start-Sleep -Milliseconds 900
Shot 'winz_layout1'
Send '1'; Start-Sleep -Seconds 2
Shot 'snapped_left'
Dump-All 'snapped_left'
# Snap Assist offers the other open windows for the right half: click File Explorer's thumbnail
$fe = Find-Anywhere '^Documents'
Write-Host "assist target: $($fe.name) $($fe.x),$($fe.y)"
if ($fe -and $fe.x -gt 900) { $c = Center $fe; Move-To $c[0] $c[1]; Shot 'hover_assist' @{ item = $fe }; Click $c[0] $c[1] } else { Move-To 1440 540; Shot 'hover_assist'; Click 1440 540 }
Start-Sleep -Seconds 2
Shot 'side_by_side'
# keyboard snapping: Windows + Right / Windows + Left
Key-Combo @($VK.WIN, 0x25); Start-Sleep -Seconds 2
Shot 'win_left'
Dump-All 'win_left'
Send '{ESC}'
Save-Log
Get-Process notepad -ErrorAction SilentlyContinue | Stop-Process -Force
