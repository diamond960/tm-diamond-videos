# aitest03: ChatGPT (no account) at 1280x720 with Edge zoom 125% - where is the box, how big is the text?
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'aitest03' 1280 720
Set-DarkMode
Start-Process 'msedge.exe' -ArgumentList '--no-first-run','--no-default-browser-check','--start-maximized','https://chatgpt.com/'
Start-Sleep -Seconds 15
Dismiss-Popups
Shot 'loaded_100'
$verify = Find-Anywhere '(verify you are human|are you a robot|security check|just a moment)'
if ($verify) { Shot 'verify_wall' @{} 'bot check shown - stopping'; Save-Log; return }
# Edge zoom 125%: Ctrl + plus twice (110%, 125%)
[System.Windows.Forms.SendKeys]::SendWait('^{ADD}'); Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait('^{ADD}'); Start-Sleep -Seconds 2
Shot 'loaded_125'
# ChatGPT focuses its box on load; type straight away (no click needed)
[System.Windows.Forms.SendKeys]::SendWait('{ESC}'); Start-Sleep -Milliseconds 300
Type-Shots 'Explain RAM like I am 10' 'typed'
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
foreach ($s in 1, 2, 3, 5, 8) { Start-Sleep -Seconds 1; Shot "answer_$s" }
Save-Log
