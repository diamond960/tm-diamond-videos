# long04 section 2: clipboard history - Windows + V, Turn on, copy two things, paste the older one (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
. "$PSScriptRoot/../engine/long04_lib.ps1"
Init-Capture 'long04_02'
$cb = 'HKCU:\Software\Microsoft\Clipboard'
New-Item -Path $cb -Force | Out-Null
Set-ItemProperty -Path $cb -Name EnableClipboardHistory -Value 0 -Type DWord
Set-DarkMode
function Send([string]$s) { [System.Windows.Forms.SendKeys]::SendWait($s); Start-Sleep -Milliseconds 300 }
Start-Process notepad.exe; Start-Sleep -Seconds 3
Place-Foreground 260 130 1400 760; Start-Sleep -Seconds 1
Send 'Order number: 48213{ENTER}Meeting moved to 3 PM{ENTER}{ENTER}'
Start-Sleep -Milliseconds 500
Shot 'notes'
# Windows + V while history is off
Key-Combo @($VK.WIN, $VK.V); Start-Sleep -Seconds 2
$on = Find-Anywhere '^Turn on$'
Shot 'winv_off' @{ turnon = $on }
Dump-All 'winv_off'
if ($on) {
  $c = Center $on; Move-To $c[0] $c[1]; Shot 'hover_turnon' @{ turnon = $on }
  Click $c[0] $c[1]; Start-Sleep -Seconds 2
  Shot 'turned_on'
  Dump-All 'turned_on'
  Send '{ESC}'; Start-Sleep -Milliseconds 800
} else {
  Send '{ESC}'; Start-Sleep -Milliseconds 800
  Write-Host 'no Turn on button - using Settings > System > Clipboard'
  Start-Process 'ms-settings:clipboard'; Start-Sleep -Seconds 5
  Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
  Shot 'settings_clipboard'
  Dump-Names 'settings_clipboard'
  Flip '^Clipboard history' 'history'
  Get-Process SystemSettings -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep -Seconds 1
}
# back to Notepad: copy line 1, then line 2
$np = Get-Process notepad -ErrorAction SilentlyContinue | Select-Object -First 1
if ($np) { [void][W]::SetForegroundWindow($np.MainWindowHandle); Start-Sleep -Milliseconds 800 }
Send '^{HOME}'; Send '+{END}'; Shot 'sel1'; Send '^c'; Start-Sleep -Milliseconds 600
Send '{DOWN}'; Send '{HOME}'; Send '+{END}'; Shot 'sel2'; Send '^c'; Start-Sleep -Milliseconds 600
Send '^{END}'; Start-Sleep -Milliseconds 400
Shot 'ready'
Key-Combo @($VK.WIN, $VK.V); Start-Sleep -Seconds 2
Shot 'history'
Dump-All 'history'
# the older item (second in the list) - find it by its text
$old = Find-Anywhere '^Order number: 48213'
if (-not $old) { $old = Find-Anywhere 'Order number' }
if ($old) {
  $c = Center $old; Move-To $c[0] $c[1]; Shot 'hover_old' @{ item = $old }
  Click $c[0] $c[1]; Start-Sleep -Seconds 2
} else { Send '{DOWN}'; Send '{ENTER}'; Start-Sleep -Seconds 2 }
Shot 'pasted'
Save-Log
Get-Process notepad -ErrorAction SilentlyContinue | Stop-Process -Force
