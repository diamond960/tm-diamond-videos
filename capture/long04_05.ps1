# long04 section 5: Settings > Personalization > Start - turn off the recommendation/tips switches (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_05'
Set-DarkMode
Key-Combo @($VK.WIN); Start-Sleep -Seconds 2
Shot 'start_before'
Dump-All 'start_before'
[System.Windows.Forms.SendKeys]::SendWait('{ESC}'); Start-Sleep -Seconds 1
Open-Settings
Go '^Personalization$' 'personalization' 'ListItem' 'ms-settings:personalization'
Go '^Start$' 'start_page' '' 'ms-settings:personalization-start'
# film each "Show ..." switch that is on being turned off
$names = @()
foreach ($el in (Get-AllEl)) {
  $nm = $el.Current.Name
  if ($nm -and $nm -match '^Show (recommendations|recently added|recommended|account|websites)' -and (Toggle-State $el) -eq 'On') { $names += $nm }
}
Write-Host ("on: " + ($names -join ' | '))
$k = 0
foreach ($nm in $names) { $k++; Flip ('^' + [regex]::Escape($nm)) "s$k" | Out-Null }
Shot 'start_page_done'
Dump-Names 'start_page_done'
Get-Process SystemSettings -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1
Key-Combo @($VK.WIN); Start-Sleep -Seconds 2
Shot 'start_after'
Dump-All 'start_after'
[System.Windows.Forms.SendKeys]::SendWait('{ESC}')
Save-Log
