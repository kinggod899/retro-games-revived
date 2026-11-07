
$adb = '<WORKSPACE>\Sdk\platform-tools\adb.exe'
$dev = '<DEVICE_ID>'
& $adb -s $dev shell "getprop ro.build.version.sdk" | Out-String
Write-Output "=== install ==="
& $adb -s $dev install -r "<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk" 2>&1 | Out-String
Write-Output "=== launch ==="
& $adb -s $dev shell am start -n com.chillingo.tinytroopersfree.android.aja/com.kuaiyouxi.gamepad.sdk.shell.KyxShellActivity 2>&1 | Out-String
Start-Sleep -Seconds 8
Write-Output "=== logcat (pid filter) ==="
& $adb -s $dev shell "pidof com.chillingo.tinytroopersfree.android.aja" 2>&1 | Out-String
& $adb -s $dev logcat -d -t 300 2>&1 | Select-String -Pattern 'tinytroopers|kuaiyouxi|Unity|mono|libunity|AndroidRuntime|dlopen|SELinux|avc:' | Select-Object -Last 60 | Out-String
