# Helpers for the long04 capture scripts (Windows 11 settings). Dot-sourced after engine/wincap.ps1.
# NOTE: never name a variable $n, $out or $log here (they clash with wincap.ps1's script variables).

function Get-AllEl {
  $h = [W]::GetForegroundWindow(); $root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
  return $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
}

function Get-El([string]$Pattern, [string]$Type = '') {
  foreach ($el in (Get-AllEl)) {
    $nm = $el.Current.Name
    if (-not $nm -or $nm -notmatch $Pattern) { continue }
    if ($Type -and $el.Current.ControlType.ProgrammaticName -ne "ControlType.$Type") { continue }
    return $el
  }
  return $null
}

function El-Rect($el) {
  if (-not $el) { return $null }
  $b = $el.Current.BoundingRectangle
  if ($b.Width -le 0) { return $null }
  return @{ x = [int]$b.X; y = [int]$b.Y; w = [int]$b.Width; h = [int]$b.Height; name = $el.Current.Name }
}

function Into-View($el) {
  if (-not $el) { return }
  try { $el.GetCurrentPattern([System.Windows.Automation.ScrollItemPattern]::Pattern).ScrollIntoView(); Start-Sleep -Milliseconds 800 } catch { }
}

function Toggle-State($el) {
  try { return [string]$el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState } catch { return '' }
}

function Set-ToggleQuiet([string]$Pattern, [string]$Want) {
  # setup only (before filming): put a toggle in a known state without filming it
  $el = Get-El $Pattern 'Button'
  if (-not $el) { $el = Get-El $Pattern }
  if (-not $el) { Write-Host "setup toggle not found: $Pattern"; return }
  try {
    $tp = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
    if ([string]$tp.Current.ToggleState -ne $Want) { $tp.Toggle(); Start-Sleep -Seconds 1 }
  } catch { Write-Host "setup toggle failed: $Pattern" }
}

function Open-Settings {
  Key-Combo @($VK.WIN, $VK.I); Start-Sleep -Seconds 5
  $fg = Get-FgRect
  if ($fg.title -notmatch 'Settings') { Start-Process 'ms-settings:'; Start-Sleep -Seconds 5 }
  Place-Foreground 160 110 1560 840; Start-Sleep -Seconds 2
}

function Go([string]$Pattern, [string]$Label, [string]$Type = '', [string]$Fallback = '') {
  # hover + click a real element (nav item, link, button), film both, then the page it opens
  $el = $null
  if ($Type) { $el = Get-El $Pattern $Type }
  if (-not $el) { $el = Get-El $Pattern }
  Into-View $el
  $r = El-Rect $el
  if ($r) {
    $c = Center $r; Move-To $c[0] $c[1]; Shot "hover_$Label" @{ target = $r }
    Click $c[0] $c[1]; Start-Sleep -Seconds 2
  } elseif ($Fallback) {
    Write-Host "not found: $Pattern - opening $Fallback"
    Start-Process $Fallback; Start-Sleep -Seconds 5
  } else { Write-Host "not found: $Pattern" }
  Shot $Label @{ target = $r }
  Dump-Names $Label
  return $r
}

function Flip([string]$Pattern, [string]$Label) {
  # click a real toggle switch and film before/after (state logged in the shot note)
  $el = Get-El $Pattern 'Button'
  if (-not $el) { $el = Get-El $Pattern }
  if (-not $el) { Write-Host "toggle not found: $Pattern"; return $null }
  Into-View $el
  $r = El-Rect $el
  $before = Toggle-State $el
  $c = Center $r; Move-To $c[0] $c[1]
  Shot "before_$Label" @{ toggle = $r } "state:$before"
  Click $c[0] $c[1]; Start-Sleep -Milliseconds 1500
  $el2 = Get-El $Pattern 'Button'; if (-not $el2) { $el2 = $el }
  $r2 = El-Rect $el2
  Shot "after_$Label" @{ toggle = $r2 } ("state:" + (Toggle-State $el2))
  return $r2
}

function Scroll-Wheel([int]$Notches) {
  # positive = down
  $d = [BitConverter]::ToUInt32([BitConverter]::GetBytes([int32](-120 * $Notches)), 0)
  [W]::mouse_event(0x0800, 0, 0, $d, [IntPtr]::Zero); Start-Sleep -Milliseconds 700
}

function Dump-All([string]$Tag) {
  # every named element on the whole desktop (flyouts, Start, taskbar) for exact boxes in the spec
  $items = @()
  try {
    $root = [System.Windows.Automation.AutomationElement]::RootElement
    $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    foreach ($el in $all) {
      $nm = $el.Current.Name; if (-not $nm) { continue }
      $b = $el.Current.BoundingRectangle; if ($b.Width -le 0) { continue }
      $items += ('{0} | {1} | {2},{3},{4},{5}' -f $el.Current.ControlType.ProgrammaticName, $nm, [int]$b.X, [int]$b.Y, [int]$b.Width, [int]$b.Height)
    }
  } catch { }
  Set-Content -Encoding utf8 -Path (Join-Path $script:Out "all_$Tag.txt") -Value $items
}

function Explorer-ShowItem([string]$Item, [string]$Label) {
  # File Explorer: View > Show > <Item> (submenus open on a click; Right arrow as a fallback)
  $view = Find-Rect 'View'
  if (-not $view) { Write-Host 'View button not found'; return }
  $c = Center $view; Move-To $c[0] $c[1]; Shot "${Label}_hover_view" @{ view = $view }
  Click $c[0] $c[1]; Start-Sleep -Milliseconds 900
  $show = Find-Rect 'Show'
  Shot "${Label}_view_menu" @{ view = $view; show = $show }
  if (-not $show) { return }
  Click ([int]($show.x + $show.w / 2)) ([int]($show.y + $show.h / 2)); Start-Sleep -Milliseconds 1200
  $it = Find-Rect $Item
  if (-not $it) { Key-Combo @([byte]0x27); Start-Sleep -Milliseconds 1200; $it = Find-Rect $Item }
  Shot "${Label}_show_menu" @{ show = $show; item = $it }
  Dump-All "${Label}_show_menu"
  if ($it) {
    Move-To ([int]($it.x + 60)) ([int]($it.y + $it.h / 2)); Start-Sleep -Milliseconds 300
    Shot "${Label}_hover_item" @{ item = $it }
    Click ([int]($it.x + 60)) ([int]($it.y + $it.h / 2)); Start-Sleep -Seconds 2
  } else { Write-Host "$Item not found" }
}
