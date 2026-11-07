
$adb = '<WORKSPACE>\Sdk\platform-tools\adb.exe'
$dev = '<DEVICE_ID>'
$pkg = 'com.chillingo.tinytroopersfree.android.aja'
Write-Output "=== pid ==="
& $adb -s $dev shell "pidof $pkg" 2>&1 | Out-String
Write-Output "=== top activity ==="
& $adb -s $dev shell "dumpsys activity activities | grep -E 'mResumedActivity|topResumedActivity'" 2>&1 | Out-String
Write-Output "=== crash log ==="
& $adb -s $dev logcat -d -b crash -t 100 2>&1 | Select-Object -Last 40 | Out-String
Write-Output "=== app logcat ==="
& $adb -s $dev shell "logcat -d -t 500 | grep -iE 'tinytroopers|kuaiyouxi|chillingo|kyx'" 2>&1 | Select-Object -Last 40 | Out-String
