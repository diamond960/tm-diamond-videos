# aitest02: ChatGPT without an account (its normal free no-login mode) - ask one question and film the real answer.
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'aitest02'
Set-DarkMode
Start-Process 'msedge.exe' -ArgumentList '--no-first-run','--no-default-browser-check','--start-maximized','https://chatgpt.com/'
Start-Sleep -Seconds 15
Dismiss-Popups
Shot 'loaded'
$verify = Find-Anywhere '(verify you are human|are you a robot|security check|just a moment)'
if ($verify) { Shot 'verify_wall' @{} 'bot check shown - stopping'; Save-Log; return }
# the "Ask ChatGPT" box (web content is not exposed by name, so click where it is drawn: 707..1473 x 525..575)
Move-To 1060 550; Start-Sleep -Milliseconds 300
Click 1060 550; Start-Sleep -Milliseconds 700
Shot 'box_clicked'
Type-Shots 'Give me 3 YouTube titles for a video about fixing a slow laptop' 'typed'
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
foreach ($s in 2, 4, 7, 11, 16, 24) { Start-Sleep -Seconds ($s - ($(if ($prev) {$prev} else {0}))); $prev = $s; Shot "answer_$s" }
Save-Log
