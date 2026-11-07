
$adb = '<WORKSPACE>\Sdk\platform-tools\adb.exe'
$dev = '<DEVICE_ID>'
$pkg = 'com.chillingo.tinytroopersfree.android.aja'
# 点“继续”按钮(ReviewPermissions 的 continue 按钮通常在底部)
& $adb -s $dev shell "input keyevent KEYCODE_BACK" 2>&1 | Out-Null
Start-Sleep -Seconds 2
& $adb -s $dev shell "am start -n $pkg/com.kuaiyouxi.gamepad.sdk.shell.KyxShellActivity" 2>&1 | Out-Null
Start-Sleep -Seconds 12
Write-Output "=== pid ==="
& $adb -s $dev shell "pidof $pkg" 2>&1 | Out-String
Write-Output "=== top ==="
& $adb -s $dev shell "dumpsys activity activities | grep -E 'topResumedActivity'" 2>&1 | Out-String
Write-Output "=== logcat game ==="
& $adb -s $dev shell "logcat -d -v brief | grep -iE 'tinytroopers|kuaiyouxi|kyx|Unity|FATAL|AndroidRuntime|mono|aja|ReviewPermissions'" 2>&1 | Select-Object -Last 50 | Out-String
