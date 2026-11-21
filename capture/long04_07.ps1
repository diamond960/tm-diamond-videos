# long04 section 7: Settings > Personalization > Taskbar > Taskbar behaviors > Taskbar alignment: Left (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_07'
$adv = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
Set-ItemProperty -Path $adv -Name TaskbarAl -Value 1 -Type DWord -ErrorAction SilentlyContinue
Set-DarkMode
Shot 'centered_desktop'
Open-Settings
Go '^Personalization$' 'personalization' 'ListItem' 'ms-settings:personalization'
Go '^Taskbar$' 'taskbar_page' '' 'ms-settings:taskbar'
Go '^Taskbar behaviors' 'behaviors' '' ''
Move-To 1100 700; Scroll-Wheel 3; Start-Sleep -Seconds 1
$cb = El-Rect (Get-El '^Taskbar alignment' 'ComboBox')
if (-not $cb) { $cb = El-Rect (Get-El '.' 'ComboBox') }
Shot 'behaviors_open' @{ combo = $cb }
Dump-Names 'behaviors_open'
if ($cb) {
  $c = Center $cb; Move-To $c[0] $c[1]; Shot 'hover_align' @{ combo = $cb }
  Click $c[0] $c[1]; Start-Sleep -Seconds 1
  Shot 'align_open' @{ combo = $cb }
  Dump-All 'align_open'
  $lf = Find-Anywhere '^Left$'
  if ($lf) { $k = Center $lf; Move-To $k[0] $k[1]; Shot 'hover_left' @{ left = $lf }; Click $k[0] $k[1]; Start-Sleep -Seconds 3 }
  else { Write-Host 'Left not found' }
}
Shot 'left' @{ combo = $cb }
Dump-All 'left'
(New-Object -ComObject Shell.Application).MinimizeAll(); Start-Sleep -Seconds 1
Shot 'left_desktop'
Key-Combo @($VK.WIN); Start-Sleep -Seconds 2
Shot 'left_start'
[System.Windows.Forms.SendKeys]::SendWait('{ESC}')
Set-ItemProperty -Path $adv -Name TaskbarAl -Value 1 -Type DWord -ErrorAction SilentlyContinue
Save-Log
