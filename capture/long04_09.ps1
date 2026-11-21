# long04 section 9: Settings > Privacy & security > General - turn off the switches that are on (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_09'
Set-DarkMode
Open-Settings
Go '^Privacy & security$' 'privacy' 'ListItem' 'ms-settings:privacy'
Go '^General' 'general' '' 'ms-settings:privacy-general'
$tg = @(); $names = @()
foreach ($el in (Get-AllEl)) {
  $st = Toggle-State $el
  if ($st) { $tg += ('{0} = {1} enabled={2}' -f $el.Current.Name, $st, $el.Current.IsEnabled) }
  if ($st -eq 'On' -and $el.Current.IsEnabled -and $el.Current.Name -match '^(Let|Show)') { $names += $el.Current.Name }
}
Set-Content -Encoding utf8 -Path (Join-Path $script:Out 'toggles.txt') -Value $tg
Write-Host ($tg -join "`n")
$k = 0
foreach ($nm in $names) { $k++; Flip ('^' + [regex]::Escape($nm)) "p$k" | Out-Null }
Move-To 1450 900
Shot 'done'
Dump-Names 'done'
Save-Log
