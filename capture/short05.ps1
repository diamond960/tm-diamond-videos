# short05: "Turn off these animations for a faster PC" - Settings > Accessibility > Visual effects (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'short05'
Set-DarkMode
Start-Process 'ms-settings:easeofaccess-visualeffects'
Start-Sleep -Seconds 5
Place-Foreground 160 110 1560 840
Start-Sleep -Seconds 2
$tr = Find-RectLike '^Transparency effects' 'Button'
if (-not $tr) { $tr = Find-RectLike '^Transparency effects' }
$an = Find-RectLike '^Animation effects' 'Button'
if (-not $an) { $an = Find-RectLike '^Animation effects' }
Shot 'visual_page' @{ transparency = $tr; animation = $an }
foreach ($pair in @(@('animation', $an), @('transparency', $tr))) {
  $r = $pair[1]; if (-not $r) { continue }
  $c = Center $r; Move-To $c[0] $c[1]; Shot ("hover_" + $pair[0]) @{ t = $r }
  Click $c[0] $c[1]; Start-Sleep -Seconds 2
  Shot ($pair[0] + "_off") @{ t = $r; transparency = $tr; animation = $an }
}
Save-Log
