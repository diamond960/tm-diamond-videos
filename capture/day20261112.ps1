# day20261112: Windows block 2 "Command Prompt basics" (+ a check for block 1 ep10, optional driver updates).
# 1280x720 so the whole screen stays readable in the full-screen framing; Windows Terminal maximised, text enlarged.
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'day20261112' 1280 720
Set-DarkMode
function Send([string]$s) { [System.Windows.Forms.SendKeys]::SendWait($s); Start-Sleep -Milliseconds 300 }
function Clear-Term { Send 'cls'; Send '{ENTER}'; Start-Sleep -Milliseconds 700 }
function Shots-Until([string]$Proc, [string]$Label, [int]$MaxSec, [int[]]$At) {
  # takes a shot at each second mark in $At until the process ends (or $MaxSec)
  $t0 = Get-Date; $k = 0
  while ($true) {
    Start-Sleep -Milliseconds 500
    $el = ((Get-Date) - $t0).TotalSeconds
    if ($k -lt $At.Count -and $el -ge $At[$k]) { Shot $Label @{} ("t=" + [int]$el); $k++ }
    if ($el -gt 4 -and -not (Get-Process $Proc -ErrorAction SilentlyContinue)) { break }
    if ($el -gt $MaxSec) { Write-Host "$Proc still running after $MaxSec s"; break }
  }
  Start-Sleep -Seconds 1
}

# ---- block 1 ep10: is Optional updates (driver updates) available on this PC?
Start-Process 'ms-settings:windowsupdate'
Start-Sleep -Seconds 6
Key-Combo @($VK.WIN, 0x26)
Start-Sleep -Seconds 1
Shot 'b1e10_wu'
Dump-Names 'b1e10_wu'
Start-Process 'ms-settings:windowsupdate-optionalupdates'
Start-Sleep -Seconds 5
Shot 'b1e10_optional'
Dump-Names 'b1e10_optional'
Get-Process SystemSettings -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
(New-Object -ComObject Shell.Application).MinimizeAll()
Start-Sleep -Seconds 1
Save-Log

# ---- open Command Prompt as administrator from Start search
Shot 'cmd_desktop'
Key-Combo @($VK.WIN)
Start-Sleep -Seconds 2
Shot 'cmd_start'
Type-Shots 'cmd' 'cmd_search_type'
Start-Sleep -Seconds 3
$runas = Find-Anywhere '^Run as administrator$'
$best = Find-Anywhere '^Command Prompt'
Shot 'cmd_search' @{ runas = $runas; best = $best }
Dump-Names 'cmd_search'
if ($runas) {
  $c = Center $runas; Move-To ($c[0] - 60) ($c[1] - 40); Start-Sleep -Milliseconds 300
  Move-To $c[0] $c[1]; Shot 'cmd_search_hover' @{ runas = $runas }
  Click $c[0] $c[1]
} else {
  Write-Host 'no Run as administrator in search - using Win+R'
  Send '{ESC}'; Start-Sleep -Seconds 1
  Key-Combo @($VK.WIN, $VK.R); Start-Sleep -Milliseconds 1500
  Shot 'cmd_run'; Type-Shots 'cmd' 'cmd_run_type'; Send '{ENTER}'
}
Start-Sleep -Seconds 6
Dismiss-Popups
Key-Combo @($VK.WIN, 0x26)
Start-Sleep -Seconds 1
Shot 'cmd_open_small'
# bigger text (Windows Terminal: Ctrl + numpad plus)
Send '^{ADD}'; Send '^{ADD}'; Send '^{ADD}'
Start-Sleep -Seconds 1
Shot 'cmd_open'
Save-Log

# ---- b2e2 ipconfig
Clear-Term
Shot 'b2e2_clean'
Type-Shots 'ipconfig' 'b2e2_type'
Send '{ENTER}'
Start-Sleep -Seconds 3
Shot 'b2e2_result'
Save-Log

# ---- b2e1 ipconfig /flushdns (TikTok)
Clear-Term
Shot 'b2e1_clean'
Type-Shots 'ipconfig /flushdns' 'b2e1_type'
Send '{ENTER}'
Start-Sleep -Seconds 2
Shot 'b2e1_result'
Save-Log

# ---- b2e3 ping (cloud PCs often block ping replies - check)
Clear-Term
Shot 'b2e3_clean'
Type-Shots 'ping google.com' 'b2e3_type'
Send '{ENTER}'
Shots-Until 'PING' 'b2e3_ping' 25 @(1, 2, 3, 5, 8, 12, 18)
Shot 'b2e3_result'
Save-Log

# ---- b2e5 systeminfo
Clear-Term
Shot 'b2e5_clean'
Type-Shots 'systeminfo' 'b2e5_type'
Send '{ENTER}'
Start-Sleep -Seconds 1
Shot 'b2e5_loading'
Shots-Until 'systeminfo' 'b2e5_loading' 40 @(3)
Shot 'b2e5_result'
Move-To 640 380
for ($k = 1; $k -le 10; $k++) { [W]::mouse_event(0x0800, 0, 0, [uint32]360, [IntPtr]::Zero); Start-Sleep -Milliseconds 300; Shot 'b2e5_scroll' }
Key-Combo @($VK.CTRL, $VK.SHIFT, 0x24)
Start-Sleep -Seconds 1
Shot 'b2e5_top'
Key-Combo @($VK.CTRL, $VK.SHIFT, 0x23)
Start-Sleep -Milliseconds 500
Save-Log

# ---- b2e6 tasklist + taskkill on a real Notepad window
Clear-Term
Start-Process notepad.exe
Start-Sleep -Seconds 3
Place-Foreground 330 110 620 420
Start-Sleep -Milliseconds 500
$tb = Find-Anywhere '^Notepad'
Shot 'b2e6_notepad' @{ notepad = $tb }
Key-Combo @($VK.ALT, $VK.TAB)
Start-Sleep -Seconds 1
Shot 'b2e6_back'
Type-Shots 'tasklist' 'b2e6_type1'
Send '{ENTER}'
Start-Sleep -Seconds 3
Shot 'b2e6_list'
Type-Shots 'taskkill /im notepad.exe /f' 'b2e6_type2'
Send '{ENTER}'
Start-Sleep -Seconds 2
Shot 'b2e6_result'
Start-Sleep -Seconds 1
Shot 'b2e6_result2'
Save-Log

# ---- b2e9 driverquery
Clear-Term
Shot 'b2e9_clean'
Type-Shots 'driverquery' 'b2e9_type'
Send '{ENTER}'
Start-Sleep -Milliseconds 600
Shot 'b2e9_loading'
Start-Sleep -Seconds 5
Shot 'b2e9_result'
Save-Log

# ---- b2e8 chkdsk C: (read-only scan, no /f)
Clear-Term
Shot 'b2e8_clean'
Type-Shots 'chkdsk C:' 'b2e8_type'
Send '{ENTER}'
Shots-Until 'chkdsk' 'b2e8_run' 300 @(2, 5, 10, 20, 40, 80, 160, 240)
Shot 'b2e8_result'
Save-Log

# ---- b2e4 sfc /scannow (last: it can take many minutes)
Clear-Term
Shot 'b2e4_clean'
Type-Shots 'sfc /scannow' 'b2e4_type'
Send '{ENTER}'
Shots-Until 'sfc' 'b2e4_run' 690 @(3, 8, 20, 45, 90, 150, 240, 360, 480, 600)
Shot 'b2e4_result'
Save-Log
