# long04 section 6: Settings > System > Notifications - Do not disturb + turn off one app's notifications (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_06'
Set-DarkMode
Open-Settings
Go '^System$' 'system' 'ListItem' 'ms-settings:system'
Go '^Notifications' 'notifications' '' 'ms-settings:notifications'
# the per-app list ("Notifications from apps and other senders"): log every switch on the page
$tg = @()
foreach ($el in (Get-AllEl)) {
  $st = Toggle-State $el
  if ($st) { $tg += ('{0} = {1}' -f $el.Current.Name, $st) }
}
Set-Content -Encoding utf8 -Path (Join-Path $script:Out 'toggles.txt') -Value $tg
Write-Host ($tg -join "`n")
# turn on Do not disturb (a real switch on this page)
Flip '^Do not disturb' 'dnd' | Out-Null
Dump-Names 'dnd'
# scroll to the app list and switch off the first app that is on
Move-To 1100 700; Scroll-Wheel 6; Start-Sleep -Seconds 1
Shot 'app_list'
Dump-Names 'app_list'
$skip = '^(Notifications|Do not disturb|Turn on do not disturb|Set priority|Show notifications|Show the|Offer|Get tips|Suggest)'
$app = $null
foreach ($el in (Get-AllEl)) {
  $nm = $el.Current.Name
  if (-not $nm -or $nm -match $skip) { continue }
  if ((Toggle-State $el) -eq 'On' -and $el.Current.ControlType.ProgrammaticName -eq 'ControlType.Button') { $app = $nm; break }
}
Write-Host "app switch: $app"
if ($app) { Flip ('^' + [regex]::Escape($app)) 'app' | Out-Null }
Shot 'done'
Dump-Names 'done'
# undo Do not disturb so other captures are not affected
Set-ToggleQuiet '^Do not disturb' 'Off'
Save-Log
