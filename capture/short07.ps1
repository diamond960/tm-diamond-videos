# short07 (AI for Creators, Part 1): "You're using ChatGPT wrong" - the same request asked vague, then specific,
# in ChatGPT's real no-account mode (recipe: capture/aitest03.ps1 - 1280x720, Edge zoom 125%, type without clicking).
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'short07' 1280 720
Set-DarkMode
Start-Process 'msedge.exe' -ArgumentList '--no-first-run','--no-default-browser-check','--start-maximized','https://chatgpt.com/'
Start-Sleep -Seconds 15
Dismiss-Popups
$verify = Find-Anywhere '(verify you are human|are you a robot|security check|just a moment)'
if ($verify) { Shot 'verify_wall' @{} 'bot check shown - stopping'; Save-Log; return }
[System.Windows.Forms.SendKeys]::SendWait('^{ADD}'); Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait('^{ADD}'); Start-Sleep -Seconds 2
Move-To 900 520
Shot 'empty'
[System.Windows.Forms.SendKeys]::SendWait('{ESC}'); Start-Sleep -Milliseconds 300
Type-Shots 'Give me video ideas' 'typed1'
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
foreach ($s in 1, 2, 3, 5, 8, 12) { Start-Sleep -Seconds $(if ($s -le 3) {1} elseif ($s -eq 5) {2} elseif ($s -eq 8) {3} else {4}); Shot "answer1_$s" }
# the follow-up, in the same chat (ChatGPT keeps the box focused after an answer)
Type-Shots 'Give me 3 video ideas for a beginner tech channel, under 10 words each, numbered' 'typed2'
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
foreach ($s in 1, 2, 3, 5, 8) { Start-Sleep -Seconds $(if ($s -le 3) {1} elseif ($s -eq 5) {2} else {3}); Shot "answer2_$s" }
Save-Log
