# long04 section 4: Settings > Personalization > Colors > Choose your mode: Dark (starts in light mode)
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_04'
$p = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
New-Item -Path $p -Force | Out-Null
Set-ItemProperty -Path $p -Name AppsUseLightTheme -Value 1 -Type DWord
Set-ItemProperty -Path $p -Name SystemUsesLightTheme -Value 1 -Type DWord
Get-Process explorer -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 4; Dismiss-Popups
(New-Object -ComObject Shell.Application).MinimizeAll(); Start-Sleep -Seconds 1
Shot 'light_desktop'
Open-Settings
Shot 'settings_open'
Dump-Names 'settings_open'
Go '^Personalization$' 'personalization' 'ListItem' 'ms-settings:personalization'
Go '^Colors' 'colors' '' 'ms-settings:colors'
$cb = El-Rect (Get-El '^Choose your mode' 'ComboBox')
if (-not $cb) { $cb = El-Rect (Get-El '.' 'ComboBox') }
if ($cb) {
  $c = Center $cb; Move-To $c[0] $c[1]; Shot 'hover_mode' @{ combo = $cb }
  Click $c[0] $c[1]; Start-Sleep -Seconds 1
  Shot 'mode_open' @{ combo = $cb }
  Dump-All 'mode_open'
  $dk = Find-Anywhere '^Dark$'
  if ($dk) { $k = Center $dk; Move-To $k[0] $k[1]; Shot 'hover_dark' @{ dark = $dk }; Click $k[0] $k[1]; Start-Sleep -Seconds 4 }
  else { Write-Host 'Dark item not found' }
} else { Write-Host 'mode combo not found' }
Shot 'dark' @{ combo = $cb }
Dump-Names 'dark'
(New-Object -ComObject Shell.Application).MinimizeAll(); Start-Sleep -Seconds 1
Shot 'dark_desktop'
Save-Log
