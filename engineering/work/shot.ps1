
$adb = '<WORKSPACE>\Sdk\platform-tools\adb.exe'
$dev = '<DEVICE_ID>'
& $adb -s $dev shell "screencap -p /sdcard/s1.png"
& $adb -s $dev pull /sdcard/s1.png "<WORKSPACE>\work\s1.png" 2>&1 | Out-Null
Write-Output "pulled"
& $adb -s $dev shell "dumpsys activity top | head -30" 2>&1 | Out-String
