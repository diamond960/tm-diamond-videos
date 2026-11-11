# aitest01: can ChatGPT be filmed for real on the capture PC without logging in (its free "no account" mode)?
# Opens chatgpt.com in Edge, screenshots what loads, and only if the normal chat box is there, asks one question.
# If a sign-in wall or a "verify you are human" check shows up, it stops there (never works around it).
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'aitest01'
Set-DarkMode
Start-Process 'msedge.exe' -ArgumentList '--no-first-run','--no-default-browser-check','--start-maximized','https://chatgpt.com/'
Start-Sleep -Seconds 15
Dismiss-Popups
Shot 'loaded'
Dump-Names 'loaded'
$verify = Find-Anywhere '(verify you are human|are you a robot|security check|just a moment)'
$box = Find-RectLike '^(Ask anything|Message ChatGPT)' 'Edit'
if (-not $box) { $box = Find-RectLike '(Ask anything|Message ChatGPT)' }
if ($verify) {
  Shot 'verify_wall' @{ verify = $verify } 'bot check shown - stopping, not working around it'
} elseif ($box) {
  # close a "Log in / Sign up" welcome dialog the polite way if it offers "Stay logged out"
  $stay = Find-Anywhere '^Stay logged out$'
  if ($stay) { $c = Center $stay; Click $c[0] $c[1]; Start-Sleep -Seconds 2; Shot 'stayed_logged_out' }
  $c = Center $box; Click $c[0] $c[1]; Start-Sleep -Milliseconds 600
  Type-Shots '3 title ideas for a slow PC video' 'typed'
  [System.Windows.Forms.SendKeys]::SendWait('{ENTER}'); Start-Sleep -Seconds 20
  Shot 'answer'
  Dump-Names 'answer'
} else {
  Shot 'no_chat_box' @{} 'no chat box found'
}
Save-Log
