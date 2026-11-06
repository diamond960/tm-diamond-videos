# NOTE: never use $n/$out/$log as variable names here (PowerShell names are case-insensitive: they clash with wincap.ps1)
# tiktok01: "5 File Explorer tricks" - real File Explorer on a real Windows PC
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'tiktok01'
# demo folder with a few real files
$d = 'C:\Work'
New-Item -ItemType Directory -Force -Path $d | Out-Null
Set-Content -Encoding utf8 "$d\notes.txt" "Monday`r`n- Send the invoice to Sam`r`n- Back up the laptop`r`n- Book the dentist`r`n`r`nTuesday`r`n- Team call at 10:00`r`n- Order new keyboard"
Set-Content -Encoding utf8 "$d\budget.csv" "Item,Cost`r`nRent,1200`r`nFood,350`r`nInternet,60"
Set-Content -Encoding utf8 "$d\trip plan.txt" "Flight Friday 7:40 AM`r`nHotel check-in 3 PM"
$bmp = New-Object System.Drawing.Bitmap 640, 400
$g = [System.Drawing.Graphics]::FromImage($bmp)
$br = New-Object System.Drawing.Drawing2D.LinearGradientBrush((New-Object System.Drawing.Rectangle 0,0,640,400), [System.Drawing.Color]::FromArgb(255,30,120,220), [System.Drawing.Color]::FromArgb(255,250,170,60), 45)
$g.FillRectangle($br, 0, 0, 640, 400); $g.Dispose(); $bmp.Save("$d\photo.png", [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
# start like a normal PC: extensions hidden, preview pane closed
$adv = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
Set-ItemProperty -Path $adv -Name HideFileExt -Value 1 -Type DWord
Set-ItemProperty -Path $adv -Name LaunchTo -Value 1 -Type DWord
Remove-Item -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Modules\GlobalSettings\DetailsContainer' -Recurse -ErrorAction SilentlyContinue
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
if (-not (Get-Process explorer -ErrorAction SilentlyContinue)) { Start-Process explorer.exe; Start-Sleep -Seconds 5 }
(New-Object -ComObject Shell.Application).MinimizeAll()
Start-Sleep -Seconds 1
Shot 'desktop'

function Center($r) { if ($r) { return @([int]($r.x + $r.w / 2), [int]($r.y + $r.h / 2)) } return $null }

# Win + E
Key-Combo @($VK.WIN, $VK.E)
Start-Sleep -Seconds 4
Place-Foreground 160 60 1560 900
Start-Sleep -Seconds 1
Shot 'explorer_home'
# Alt + D -> address bar
Key-Combo @($VK.ALT, [byte]0x44)
Start-Sleep -Milliseconds 800
Shot 'address_sel'
Type-Shots 'C:\Work' 'addr_type'
Key-Combo @($VK.ENTER)
Start-Sleep -Seconds 3
$view = Find-Rect 'View'
Shot 'work_folder' @{ view = $view }
# View > Show > File name extensions
$c = Center $view
if ($c) { Click $c[0] $c[1] } else { Write-Host 'View button not found' }
Start-Sleep -Milliseconds 1200
$show = Find-Rect 'Show'
Shot 'view_menu' @{ view = $view; show = $show }
$c = Center $show
if ($c) { Click $c[0] $c[1] } else { Write-Host 'Show not found' }
Start-Sleep -Milliseconds 1200
$fe = Find-Rect 'File name extensions'
Shot 'show_menu' @{ show = $show; ext = $fe }
$c = Center $fe
if ($c) { Click $c[0] $c[1] } else { Write-Host 'File name extensions not found' }
Start-Sleep -Milliseconds 1500
Shot 'ext_on'
Key-Combo @($VK.ESC)
Start-Sleep -Milliseconds 800
$notesR = Find-Rect 'notes.txt'; if (-not $notesR) { $notesR = Find-Rect 'notes' }
$p = Find-Rect 'photo.png'; $b = Find-Rect 'budget.csv'; $t = Find-Rect 'trip plan.txt'
Shot 'ext_on2' @{ notes = $notesR; photo = $p; budget = $b; trip = $t }
# click notes.txt, Alt + P
$c = Center $notesR
if ($c) { Click $c[0] $c[1] }
Start-Sleep -Milliseconds 800
Shot 'notes_selected' @{ notes = $notesR }
Key-Combo @($VK.ALT, [byte]0x50)
Start-Sleep -Seconds 2
Shot 'preview'
Start-Sleep -Seconds 1
Shot 'preview2'
# Ctrl + Shift + N
Key-Combo @($VK.CTRL, $VK.SHIFT, [byte]0x4E)
Start-Sleep -Milliseconds 1500
Shot 'new_folder'
Type-Shots 'Invoices' 'nf_type'
Key-Combo @($VK.ENTER)
Start-Sleep -Milliseconds 1200
$inv = Find-Rect 'Invoices'
Shot 'nf_done' @{ invoices = $inv }
# select photo.png, Alt + Enter
$p = Find-Rect 'photo.png'
$c = Center $p
if ($c) { Click $c[0] $c[1] }
Start-Sleep -Milliseconds 800
Shot 'photo_selected' @{ photo = $p }
Key-Combo @($VK.ALT, $VK.ENTER)
Start-Sleep -Seconds 3
Shot 'props'
Start-Sleep -Seconds 1
Shot 'props2'
Save-Log
