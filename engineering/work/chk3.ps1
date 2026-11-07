
$adb = '<WORKSPACE>\Sdk\platform-tools\adb.exe'
$dev = '<DEVICE_ID>'
$pkg = 'com.chillingo.tinytroopersfree.android.aja'
Write-Output "=== ui dump ==="
& $adb -s $dev shell "uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; cat /sdcard/ui.xml" 2>&1 | Select-Object -First 3 | Out-String
Write-Output "=== grant permissions ==="
foreach ($p in @('android.permission.READ_PHONE_STATE','android.permission.WRITE_EXTERNAL_STORAGE','android.permission.ACCESS_FINE_LOCATION','android.permission.ACCESS_COARSE_LOCATION','android.permission.RECORD_AUDIO','android.permission.GET_ACCOUNTS','android.permission.BLUETOOTH_ADMIN','android.permission.SYSTEM_ALERT_WINDOW')) {
  $o = & $adb -s $dev shell "pm grant $pkg $p" 2>&1
  Write-Output ("  " + $p + " -> " + ($o -join ' '))
}
Write-Output "=== relaunch ==="
& $adb -s $dev logcat -c
& $adb -s $dev shell "am start -W -n $pkg/com.kuaiyouxi.gamepad.sdk.shell.KyxShellActivity" 2>&1 | Out-String
Start-Sleep -Seconds 10
& $adb -s $dev shell "pidof $pkg" 2>&1 | Out-String
& $adb -s $dev shell "logcat -d -v brief | grep -iE 'tinytroopers|kuaiyouxi|kyx|Unity|FATAL|AndroidRuntime|mono|aja'" 2>&1 | Select-Object -First 60 | Out-String
