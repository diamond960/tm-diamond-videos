# long03 section 3: ping (Command Prompt, 1280x720 like captures/day20261112). Loopback test 127.0.0.1 always answers;
# this cloud PC blocks ping replies from the internet (day20261112 showed "Request timed out" for google.com).
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long03_03' 1280 720
Set-DarkMode
function Send([string]$s) { [System.Windows.Forms.SendKeys]::SendWait($s); Start-Sleep -Milliseconds 300 }
function Clear-Term { Send 'cls'; Send '{ENTER}'; Start-Sleep -Milliseconds 700 }
$gw = (Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Sort-Object RouteMetric | Select-Object -First 1).NextHop
Write-Host "gateway=$gw"
Key-Combo @($VK.WIN, $VK.R); Start-Sleep -Milliseconds 1500
Send 'cmd'; Send '{ENTER}'
Start-Sleep -Seconds 6
Dismiss-Popups
Key-Combo @($VK.WIN, 0x26); Start-Sleep -Seconds 1
Send '^{ADD}'; Send '^{ADD}'; Send '^{ADD}'
Start-Sleep -Seconds 1
$fg = Get-FgRect
if ($fg.title -match 'Run') { Write-Host "foreground is '$($fg.title)' - stopping"; Shot 'wrong_fg'; Save-Log; return }
Clear-Term
Shot 'p1_clean'
Type-Shots 'ping 127.0.0.1' 'p1_type'
Send '{ENTER}'
foreach ($s in 1, 2, 3, 4) { Start-Sleep -Seconds 1; Shot 'p1_run' }
Start-Sleep -Seconds 1
Shot 'p1_result'
Save-Log
if ($gw) {
  Clear-Term
  Shot 'p2_clean'
  Type-Shots "ping $gw" 'p2_type'
  Send '{ENTER}'
  foreach ($s in 1, 2, 3, 5, 8, 12, 16) { Start-Sleep -Seconds 1; Shot 'p2_run' }
  Start-Sleep -Seconds 2
  Shot 'p2_result'
  Save-Log
}
Clear-Term
Shot 'p3_clean'
Type-Shots 'ping -t 127.0.0.1' 'p3_type'
Send '{ENTER}'
foreach ($s in 1, 2, 3, 4, 5, 6) { Start-Sleep -Seconds 1; Shot 'p3_run' }
Key-Combo @($VK.CTRL, 0x43)
Start-Sleep -Seconds 1
Shot 'p3_stopped'
Save-Log
