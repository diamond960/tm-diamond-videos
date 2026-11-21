# long04 section 8: File Explorer > View > Show > Hidden items (your user folder shows AppData) (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_08'
$a = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
Set-ItemProperty -Path $a -Name Hidden -Value 2 -Type DWord
Set-DarkMode
Start-Process explorer.exe $env:USERPROFILE; Start-Sleep -Seconds 4
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 1
Shot 'before' @{ view = (Find-Rect 'View') }
Dump-Names 'before'
Explorer-ShowItem 'Hidden items' 'hid'
Move-To 1500 700
$ad = Find-Rect 'AppData'
if (-not $ad) { Key-Combo @([byte]0x74); Start-Sleep -Seconds 2; $ad = Find-Rect 'AppData' }
Shot 'shown' @{ appdata = $ad }
Dump-Names 'shown'
Set-ItemProperty -Path $a -Name Hidden -Value 2 -Type DWord
Save-Log
