# fb06: "Website won't load? Flush DNS" - real Edge error page, Run dialog and Command Prompt
. "$PSScriptRoot/../engine/wincap.ps1"
Init-Capture 'fb06'
# Edge without first-run screens
New-Item -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' -Force | Out-Null
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' -Name HideFirstRunExperience -Value 1 -Type DWord
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' -Name DefaultBrowserSettingEnabled -Value 0 -Type DWord
# a readable console font if the classic console opens
New-Item -Path 'HKCU:\Console\%SystemRoot%_system32_cmd.exe' -Force | Out-Null
Set-ItemProperty -Path 'HKCU:\Console\%SystemRoot%_system32_cmd.exe' -Name FontSize -Value 0x001C0000 -Type DWord
Set-ItemProperty -Path 'HKCU:\Console\%SystemRoot%_system32_cmd.exe' -Name FaceName -Value 'Consolas'
Shot 'desktop'
Start-Process 'msedge.exe' -ArgumentList '--no-first-run','--no-default-browser-check','--start-maximized','http://my-favourite-site.invalid/'
Start-Sleep -Seconds 7
Shot 'edge_error'
Start-Sleep -Seconds 2
Shot 'edge_error2'
(New-Object -ComObject Shell.Application).MinimizeAll()
Start-Sleep -Milliseconds 800
Key-Combo @($VK.WIN, $VK.R)
Start-Sleep -Milliseconds 1500
$open = Find-Rect 'Open:'
$ok = Find-Rect 'OK'
Shot 'run' @{ open = $open; ok = $ok }
Type-Shots 'cmd' 'run_type' @{ open = $open; ok = $ok }
Key-Combo @($VK.ENTER)
Start-Sleep -Seconds 4
Place-Foreground 300 160 1320 720
Start-Sleep -Milliseconds 800
Shot 'cmd_open'
Type-Shots 'ipconfig /flushdns' 'cmd_type'
Key-Combo @($VK.ENTER)
Start-Sleep -Seconds 3
Shot 'cmd_result'
Start-Sleep -Seconds 1
Shot 'cmd_result2'
Save-Log
