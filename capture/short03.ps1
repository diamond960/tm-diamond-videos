# short03: "What's slowing your PC? Check this" - Task Manager, sort by CPU / Memory, End task (real Windows, dark mode)
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'short03'
Set-DarkMode
# a real app hogging the CPU (a small busy program named HeavyApp), so there is something to find.
# Never touch powershell processes: the runner's own shell is one of them.
$src = 'using System; using System.Threading; public static class P { public static void Main() { for (int i = 0; i < 2; i++) { var t = new Thread(() => { while (true) { } }); t.Start(); } } }'
Add-Type -TypeDefinition $src -OutputAssembly "$env:TEMP\HeavyApp.exe" -OutputType ConsoleApplication
$hogp = Start-Process "$env:TEMP\HeavyApp.exe" -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 3
Key-Combo @($VK.CTRL, $VK.SHIFT, $VK.ESC)
Start-Sleep -Seconds 4
Place-Foreground 160 110 1560 840
Start-Sleep -Seconds 3
$cpu = Find-RectLike 'CPU' 'HeaderItem'
$mem = Find-RectLike 'Memory' 'HeaderItem'
Shot 'opened' @{ cpu = $cpu; mem = $mem }
if ($cpu) {
  $c = Center $cpu; Move-To $c[0] $c[1]; Shot 'hover_cpu' @{ cpu = $cpu }
  Click $c[0] $c[1]; Start-Sleep -Seconds 2
  $hog = Find-RectLike '^HeavyApp'
  Shot 'sorted_cpu' @{ cpu = $cpu; mem = $mem; hog = $hog }
  Start-Sleep -Seconds 2
  $hog = Find-RectLike '^HeavyApp'
  Shot 'sorted_cpu2' @{ cpu = $cpu; mem = $mem; hog = $hog }
}
if ($mem) {
  $c = Center $mem; Click $c[0] $c[1]; Start-Sleep -Seconds 2
  Shot 'sorted_mem' @{ mem = $mem }
  if ($cpu) { $c = Center $cpu; Click $c[0] $c[1]; Start-Sleep -Seconds 2 }
}
$hog = Find-RectLike '^HeavyApp'
Shot 'back_cpu' @{ hog = $hog; cpu = $cpu }
if ($hog) {
  $c = Center $hog; Click ($hog.x + 120) $c[1]; Start-Sleep -Seconds 1
  $end = Find-Rect 'End task'
  Shot 'selected' @{ hog = $hog; end = $end }
  if ($end) {
    $e = Center $end; Move-To $e[0] $e[1]; Shot 'hover_end' @{ end = $end }
    Click $e[0] $e[1]; Start-Sleep -Seconds 3
  }
}
if ($hogp -and -not $hogp.HasExited) { Stop-Process -Id $hogp.Id -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
Shot 'ended' @{ cpu = $cpu }
Save-Log
