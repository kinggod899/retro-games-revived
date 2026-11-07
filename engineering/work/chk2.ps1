
$adb = '<WORKSPACE>\Sdk\platform-tools\adb.exe'
$dev = '<DEVICE_ID>'
$pkg = 'com.chillingo.tinytroopersfree.android.aja'
& $adb -s $dev logcat -c 2>&1 | Out-Null
& $adb -s $dev shell "am start -W -n $pkg/com.kuaiyouxi.gamepad.sdk.shell.KyxShellActivity" 2>&1 | Out-String
Start-Sleep -Seconds 6
Write-Output "=== full logcat relevant ==="
& $adb -s $dev shell "logcat -d -v brief | grep -iE 'tinytroopers|kuaiyouxi|chillingo|kyx|FATAL|AndroidRuntime|ActivityManager: Start|ActivityTaskManager|PackageManager.*aja|Process.*aja'" 2>&1 | Select-Object -First 80 | Out-String
