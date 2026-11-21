# long04 section 10: restore point check (System Protection), then Accessibility > Keyboard > Sticky keys shortcut off
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_10'
Set-DarkMode
# 1) Create a restore point: System Properties > System Protection (Windows client feature; check what this PC shows)
try { Start-Process 'SystemPropertiesProtection.exe' -ErrorAction Stop; Start-Sleep -Seconds 4; Shot 'protection'; Dump-Names 'protection' } catch { Write-Host "SystemPropertiesProtection failed: $_" }
Get-Process SystemPropertiesProtection -ErrorAction SilentlyContinue | Stop-Process -Force
(New-Object -ComObject Shell.Application).MinimizeAll(); Start-Sleep -Seconds 1
# 2) Sticky keys shortcut (pressing Shift five times)
Open-Settings
Go '^Accessibility$' 'accessibility' 'ListItem' 'ms-settings:easeofaccess'
Go '^Keyboard' 'keyboard' '' 'ms-settings:easeofaccess-keyboard'
Go '^Sticky keys' 'sticky' '' ''
$tg = @()
foreach ($el in (Get-AllEl)) { $st = Toggle-State $el; if ($st) { $tg += ('{0} = {1}' -f $el.Current.Name, $st) } }
Set-Content -Encoding utf8 -Path (Join-Path $script:Out 'toggles.txt') -Value $tg
Write-Host ($tg -join "`n")
Set-ToggleQuiet '^Keyboard shortcut for Sticky keys' 'On'
Shot 'sticky_page'
Flip '^Keyboard shortcut for Sticky keys' 'shortcut' | Out-Null
Dump-Names 'done'
Save-Log
