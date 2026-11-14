# long03 section 10: shutdown /s /t 3600 then shutdown /a (Command Prompt, 1280x720).
# Safety: the abort is sent no matter what, so the capture PC never shuts down.
# Run 2 (2026-11-14): run 1 shared the PC with winget installers that stole focus; this script now runs alone.
# The second 'shutdown /a' proves the first abort worked (Windows: no shutdown in progress).
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long03_10' 1280 720
Set-DarkMode
function Send([string]$s) { [System.Windows.Forms.SendKeys]::SendWait($s); Start-Sleep -Milliseconds 300 }
function Clear-Term { Send 'cls'; Send '{ENTER}'; Start-Sleep -Milliseconds 700 }
try {
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
  Shot 's1_clean'
  Type-Shots 'shutdown /s /t 3600' 's1_type'
  Send '{ENTER}'
  foreach ($s in 1, 2, 3, 5, 8) { Start-Sleep -Seconds 1; Shot 's1_run' }
  Save-Log
  Type-Shots 'shutdown /a' 's2_type'
  Send '{ENTER}'
  foreach ($s in 1, 2, 3, 5) { Start-Sleep -Seconds 1; Shot 's2_run' }
  Save-Log
  Type-Shots 'shutdown /a' 's3_type'
  Send '{ENTER}'
  Start-Sleep -Seconds 2
  Shot 's3_result'
  Save-Log
} finally {
  & shutdown.exe /a 2>$null
  Save-Log
}
