# short05: "Turn off these animations for a faster PC" - Settings > Accessibility > Visual effects (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'short05'
Set-DarkMode
Start-Process 'ms-settings:easeofaccess-visualeffects'
Start-Sleep -Seconds 5
Place-Foreground 160 110 1560 840
Start-Sleep -Seconds 2
function Get-Toggle([string]$Pattern) {
  $h = [W]::GetForegroundWindow(); $root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
  $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
  foreach ($el in $all) {
    if ($el.Current.Name -match $Pattern -and $el.Current.ControlType.ProgrammaticName -eq 'ControlType.Button') { return $el }
  }
  return $null
}
# This PC (a virtual machine) starts with both effects off; switch them on first, the way a normal PC ships,
# so the video shows the real "turn off" click.
foreach ($n in @('^Animation effects', '^Transparency effects')) {
  $el = Get-Toggle $n
  if ($el) {
    try { $tp = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
      if ($tp.Current.ToggleState -eq [System.Windows.Automation.ToggleState]::Off) { $tp.Toggle(); Start-Sleep -Seconds 2 } } catch { Write-Host "toggle failed $n" }
  }
}
Start-Sleep -Seconds 1
$tr = Find-RectLike '^Transparency effects' 'Button'
$an = Find-RectLike '^Animation effects' 'Button'
Move-To 1300 700
Shot 'visual_page_on' @{ transparency = $tr; animation = $an }
foreach ($pair in @(@('animation', $an), @('transparency', $tr))) {
  $r = $pair[1]; if (-not $r) { continue }
  $c = Center $r; Move-To $c[0] $c[1]; Shot ("hover_" + $pair[0]) @{ t = $r }
  Click $c[0] $c[1]; Start-Sleep -Seconds 2
  Shot ($pair[0] + "_off") @{ t = $r; transparency = $tr; animation = $an }
}
Save-Log
