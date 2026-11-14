# long03 section 7: winget upgrade (Command Prompt, 1280x720). Lists apps with updates, then starts
# "winget upgrade --all" for real and stops it with Ctrl+C after ~40 s (the capture PC is not ours to update fully).
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long03_07' 1280 720
Set-DarkMode
function Send([string]$s) { [System.Windows.Forms.SendKeys]::SendWait($s); Start-Sleep -Milliseconds 300 }
function Clear-Term { Send 'cls'; Send '{ENTER}'; Start-Sleep -Milliseconds 700 }
$wg = Get-Command winget -ErrorAction SilentlyContinue
Write-Host "winget=$($wg.Source)"
Key-Combo @($VK.WIN, $VK.R); Start-Sleep -Milliseconds 1500
Send 'cmd'; Send '{ENTER}'
Start-Sleep -Seconds 6
Dismiss-Popups
Key-Combo @($VK.WIN, 0x26); Start-Sleep -Seconds 1
Send '^{ADD}'; Send '^{ADD}'
Start-Sleep -Seconds 1
$fg = Get-FgRect
if ($fg.title -match 'Run') { Write-Host "foreground is '$($fg.title)' - stopping"; Shot 'wrong_fg'; Save-Log; return }
Clear-Term
Shot 'w1_clean'
Type-Shots 'winget upgrade' 'w1_type'
Send '{ENTER}'
$t0 = Get-Date; $agreed = $false
foreach ($s in 2, 4, 6, 9, 12, 16, 20, 25, 30) {
  while (((Get-Date) - $t0).TotalSeconds -lt $s) { Start-Sleep -Milliseconds 300 }
  Shot 'w1_run'
  if (-not $agreed -and $s -ge 6) { $agreed = $true; Send 'Y'; Send '{ENTER}'; Start-Sleep -Seconds 1; Shot 'w1_agreed' }
}
Start-Sleep -Seconds 3
Shot 'w1_result'
Save-Log
# scroll position: bottom of the list
Clear-Term
Shot 'w2_clean'
Type-Shots 'winget upgrade --all' 'w2_type'
Send '{ENTER}'
$t0 = Get-Date
foreach ($s in 2, 5, 10, 15, 20, 30, 40) {
  while (((Get-Date) - $t0).TotalSeconds -lt $s) { Start-Sleep -Milliseconds 300 }
  Dismiss-Popups
  Shot 'w2_run'
}
Key-Combo @($VK.CTRL, 0x43); Start-Sleep -Seconds 2
Shot 'w2_stopped'
Save-Log
