# day20261112b: the two admin commands that need more time (chkdsk took ~6.5 min, sfc runs after it).
# Opens Command Prompt as administrator from Start search ("command prompt", so it is the best match - "cmd" matched
# Git CMD on this PC). 1280x720, Windows Terminal maximised, text enlarged.
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'day20261112b' 1280 720
Set-DarkMode
function Send([string]$s) { [System.Windows.Forms.SendKeys]::SendWait($s); Start-Sleep -Milliseconds 300 }
function Clear-Term { Send 'cls'; Send '{ENTER}'; Start-Sleep -Milliseconds 700 }
function Shots-Until([string]$Proc, [string]$Label, [int]$MaxSec, [int[]]$At) {
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

Shot 'adm_desktop'
Key-Combo @($VK.WIN)
Start-Sleep -Seconds 2
Shot 'adm_start'
Type-Shots 'command prompt' 'adm_search_type'
Start-Sleep -Seconds 3
Shot 'adm_search'
Dump-Names 'adm_search'
$runas = Find-Anywhere '^Run as administrator$'
if (-not $runas) { $runas = @{ x = 640; y = 409; w = 180; h = 26; name = 'fallback position' } }
$c = Center $runas
Move-To ($c[0] - 80) ($c[1] - 60); Start-Sleep -Milliseconds 300
Move-To $c[0] $c[1]
Shot 'adm_hover' @{ runas = $runas }
Click $c[0] $c[1]
Start-Sleep -Seconds 6
Dismiss-Popups
Key-Combo @($VK.WIN, 0x26)
Start-Sleep -Seconds 1
Shot 'adm_open_small'
Send '^{ADD}'; Send '^{ADD}'; Send '^{ADD}'
Start-Sleep -Seconds 1
Shot 'adm_open'
Save-Log
# make sure the typing goes to the terminal
$fg = Get-FgRect
if ($fg.title -notmatch 'Administrator') { Write-Host "foreground is '$($fg.title)' - stopping"; Save-Log; return }

# ---- b2e8 chkdsk C: (read-only, no /f)
Clear-Term
Shot 'b2e8_clean'
Type-Shots 'chkdsk C:' 'b2e8_type'
Send '{ENTER}'
Shots-Until 'chkdsk' 'b2e8_run' 560 @(2, 5, 10, 20, 40, 80, 160, 240, 320, 400, 480)
Shot 'b2e8_result'
Save-Log
if (Get-Process chkdsk -ErrorAction SilentlyContinue) { Write-Host 'chkdsk not finished - skipping sfc'; return }

# ---- b2e4 sfc /scannow
Clear-Term
Shot 'b2e4_clean'
Type-Shots 'sfc /scannow' 'b2e4_type'
Send '{ENTER}'
Shots-Until 'sfc' 'b2e4_run' 840 @(3, 8, 20, 45, 90, 150, 240, 360, 480, 600, 720)
Shot 'b2e4_result'
Save-Log
