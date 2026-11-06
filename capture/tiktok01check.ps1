# tiktok01check: fact-check the carousel and text post shortcuts on a real Windows PC (results in shots.json notes)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'tiktok01check'
$res = @()
function Note([string]$s) { Write-Host "CHECK $s"; $script:res += $s }
# Ctrl + Shift + Esc
Key-Combo @($VK.CTRL, $VK.SHIFT, $VK.ESC)
Start-Sleep -Seconds 4
$fg = Get-FgRect
Note ("ctrl_shift_esc fg='" + $fg.title + "' taskmgr_running=" + [bool](Get-Process Taskmgr -ErrorAction SilentlyContinue))
Shot 'ctrl_shift_esc'
Stop-Process -Name Taskmgr -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
# Win + PrtScn -> Pictures\Screenshots
$sd = Join-Path ([Environment]::GetFolderPath('MyPictures')) 'Screenshots'
$before = @(Get-ChildItem $sd -ErrorAction SilentlyContinue).Count
Key-Combo @($VK.WIN, [byte]0x2C)
Start-Sleep -Seconds 3
$after = @(Get-ChildItem $sd -ErrorAction SilentlyContinue).Count
Note ("win_prtscn folder=$sd before=$before after=$after files=" + ((Get-ChildItem $sd -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name) -join ';'))
Shot 'win_prtscn'
# Alt + PrtScn with Notepad in front
Start-Process notepad.exe
Start-Sleep -Seconds 3
Place-Foreground 300 200 900 600
Start-Sleep -Seconds 1
[System.Windows.Forms.Clipboard]::Clear()
$fg = Get-FgRect
Key-Combo @($VK.ALT, [byte]0x2C)
Start-Sleep -Seconds 2
$img = [System.Windows.Forms.Clipboard]::GetImage()
if ($img) { Note ("alt_prtscn clipboard=" + $img.Width + "x" + $img.Height + " window=" + $fg.w + "x" + $fg.h + " title='" + $fg.title + "'") } else { Note 'alt_prtscn clipboard=EMPTY' }
Shot 'alt_prtscn'
# PrtScn alone
[System.Windows.Forms.Clipboard]::Clear()
Key-Combo @([byte]0x2C)
Start-Sleep -Seconds 2
Shot 'prtscn_alone'
$img = [System.Windows.Forms.Clipboard]::GetImage()
$fg = Get-FgRect
if ($img) { Note ("prtscn clipboard=" + $img.Width + "x" + $img.Height + " fg='" + $fg.title + "'") } else { Note ("prtscn clipboard=EMPTY fg='" + $fg.title + "'") }
Key-Combo @($VK.ESC)
Start-Sleep -Seconds 1
# Win + Shift + S
[System.Windows.Forms.Clipboard]::Clear()
Key-Combo @($VK.WIN, $VK.SHIFT, [byte]0x53)
Start-Sleep -Seconds 3
$fg = Get-FgRect
Note ("win_shift_s fg='" + $fg.title + "' procs=" + ((Get-Process | Where-Object { $_.Name -match 'Snip|ScreenClip' } | Select-Object -ExpandProperty Name) -join ';'))
Shot 'win_shift_s'
# drag a region to see if it lands on the clipboard
Move-To 400 300
[W]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero); Start-Sleep -Milliseconds 200
Move-To 600 420; Start-Sleep -Milliseconds 200
Move-To 800 520; Start-Sleep -Milliseconds 200
[W]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero); Start-Sleep -Seconds 3
$img = [System.Windows.Forms.Clipboard]::GetImage()
if ($img) { Note ("win_shift_s clipboard=" + $img.Width + "x" + $img.Height) } else { Note 'win_shift_s clipboard=EMPTY' }
Shot 'win_shift_s_after'
Key-Combo @($VK.ESC)
Start-Sleep -Seconds 1
# Win + . emoji panel
Key-Combo @($VK.WIN, [byte]0xBE)
Start-Sleep -Seconds 2
Shot 'win_period'
Key-Combo @($VK.ESC)
Stop-Process -Name notepad -Force -ErrorAction SilentlyContinue
$res | Set-Content -Encoding utf8 (Join-Path $script:Out 'results.txt')
Save-Log
