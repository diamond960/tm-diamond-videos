# long04 section 1: File Explorer > View > Show > File name extensions (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_01'
$a = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
Set-ItemProperty -Path $a -Name HideFileExt -Value 1 -Type DWord
Set-DarkMode
$d = Join-Path $env:USERPROFILE 'Downloads'
New-Item -ItemType Directory -Force -Path $d | Out-Null
Get-ChildItem $d -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
Copy-Item "$env:WINDIR\System32\notepad.exe" (Join-Path $d 'invoice.pdf.exe')
Set-Content -Path (Join-Path $d 'meeting notes.txt') -Value 'Agenda'
$bmp = New-Object System.Drawing.Bitmap 64, 64; $bmp.Save((Join-Path $d 'holiday photo.png'), [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
Set-Content -Path (Join-Path $d 'budget.csv') -Value 'item,cost'
Start-Sleep -Seconds 1
Start-Process explorer.exe $d; Start-Sleep -Seconds 4
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 1
Shot 'hidden' @{ invoice = (Find-Rect 'invoice.pdf'); view = (Find-Rect 'View') }
Dump-Names 'hidden'
Explorer-ShowItem 'File name extensions' 'ext'
Move-To 1500 700
$inv = Find-Rect 'invoice.pdf.exe'
if (-not $inv) { Key-Combo @([byte]0x74); Start-Sleep -Seconds 2; $inv = Find-Rect 'invoice.pdf.exe' }
Shot 'shown' @{ invoice = $inv }
Dump-Names 'shown'
Save-Log
