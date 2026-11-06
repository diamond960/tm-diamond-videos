# fb07: "That PDF is really a program" - show file name extensions in File Explorer (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'fb07'
# dark mode, like the owner's own PC
$p = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
New-Item -Path $p -Force | Out-Null
Set-ItemProperty -Path $p -Name AppsUseLightTheme -Value 0 -Type DWord
Set-ItemProperty -Path $p -Name SystemUsesLightTheme -Value 0 -Type DWord
# file name extensions hidden (the Windows default)
$a = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
Set-ItemProperty -Path $a -Name HideFileExt -Value 1 -Type DWord
Get-Process explorer -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 4
(New-Object -ComObject Shell.Application).MinimizeAll()
Start-Sleep -Seconds 1
# demo files in Downloads (a harmless copy of Notepad renamed to look like a PDF)
$d = Join-Path $env:USERPROFILE 'Downloads'
New-Item -ItemType Directory -Force -Path $d | Out-Null
Get-ChildItem $d -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
Copy-Item "$env:WINDIR\System32\notepad.exe" (Join-Path $d 'invoice.pdf.exe')
Set-Content -Path (Join-Path $d 'meeting notes.txt') -Value 'Agenda'
$bmp = New-Object System.Drawing.Bitmap 64, 64; $bmp.Save((Join-Path $d 'holiday photo.png'), [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
Set-Content -Path (Join-Path $d 'budget.csv') -Value 'item,cost'
Start-Sleep -Seconds 1
Start-Process explorer.exe $d
Start-Sleep -Seconds 4
Place-Foreground 160 110 1560 840
Start-Sleep -Seconds 1
$view = Find-Rect 'View'
$inv = Find-Rect 'invoice.pdf'
Shot 'hidden' @{ view = $view; invoice = $inv }
if ($view) {
  Move-To ([int]($view.x + $view.w / 2)) ([int]($view.y + $view.h / 2)); Shot 'hover_view' @{ view = $view }
  Click ([int]($view.x + $view.w / 2)) ([int]($view.y + $view.h / 2))
  Start-Sleep -Milliseconds 900
  $show = Find-Rect 'Show'
  Shot 'view_menu' @{ view = $view; show = $show }
  if ($show) {
    # hovering alone does not open the submenu on the runner: click "Show", then fall back to the Right arrow key
    Click ([int]($show.x + $show.w / 2)) ([int]($show.y + $show.h / 2))
    Start-Sleep -Milliseconds 1200
    $ext = Find-Rect 'File name extensions'
    if (-not $ext) { Key-Combo @([byte]0x27); Start-Sleep -Milliseconds 1200; $ext = Find-Rect 'File name extensions' }
    Shot 'show_menu' @{ show = $show; ext = $ext }
    if ($ext) {
      Move-To ([int]($ext.x + 60)) ([int]($ext.y + $ext.h / 2)); Start-Sleep -Milliseconds 300
      Shot 'hover_ext' @{ ext = $ext }
      Click ([int]($ext.x + 60)) ([int]($ext.y + $ext.h / 2))
      Start-Sleep -Seconds 2
    } else { Write-Host 'File name extensions item not found' }
  }
}
Move-To 1500 700
$inv2 = Find-Rect 'invoice.pdf.exe'
if (-not $inv2) { Key-Combo @([byte]0x74); Start-Sleep -Seconds 2; $inv2 = Find-Rect 'invoice.pdf.exe' }
Shot 'shown' @{ invoice = $inv2 }
Start-Sleep -Seconds 1
Shot 'shown2' @{ invoice = (Find-Rect 'invoice.pdf.exe') }
Save-Log
