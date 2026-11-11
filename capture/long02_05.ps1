# long02 section 8: Settings > System > Storage > Storage Sense: Automatic User content cleanup on + schedule (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'long02_05'
Set-DarkMode
Start-Process 'ms-settings:storagepolicies'; Start-Sleep -Seconds 6
Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
function Get-El([string]$Pattern, [string]$Type) {
  $h = [W]::GetForegroundWindow(); $root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
  $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
  foreach ($el in $all) { if ($el.Current.Name -match $Pattern -and $el.Current.ControlType.ProgrammaticName -eq "ControlType.$Type") { return $el } }
  return $null
}
# this PC (a virtual machine) has it on already; switch it off first so the video shows the real "turn on" click
$el = Get-El '^Storage Sense runs' 'Button'
if ($el) { try { $tp = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern); if ($tp.Current.ToggleState -eq [System.Windows.Automation.ToggleState]::On) { $tp.Toggle(); Start-Sleep -Seconds 2 } } catch { Write-Host 'toggle failed' } }
Move-To 1300 760
$tg = Find-RectLike '^Storage Sense runs' 'Button'
Shot 'page_off' @{ toggle = $tg }
Dump-Names 'page_off'
if ($tg) { $c = Center $tg; Move-To $c[0] $c[1]; Shot 'hover_toggle' @{ toggle = $tg }; Click $c[0] $c[1]; Start-Sleep -Seconds 2 }
Shot 'on' @{ toggle = $tg }
Dump-Names 'on'
$combo = Find-RectLike '^Run Storage Sense' 'ComboBox'
if (-not $combo) { $combo = Find-RectLike '.' 'ComboBox' }
if ($combo) {
  $c = Center $combo; Move-To $c[0] $c[1]; Click $c[0] $c[1]; Start-Sleep -Seconds 1
  Shot 'schedule_open' @{ combo = $combo }
  Dump-Names 'schedule_open'
  $wk = Find-RectLike '^Every week$'
  if ($wk) { $k = Center $wk; Move-To $k[0] $k[1]; Shot 'hover_week' @{ week = $wk }; Click $k[0] $k[1]; Start-Sleep -Seconds 1 }
}
Shot 'final' @{ toggle = $tg; combo = $combo }
Dump-Names 'final'
Save-Log
