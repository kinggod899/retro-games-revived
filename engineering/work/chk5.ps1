
$adb = '<WORKSPACE>\Sdk\platform-tools\adb.exe'
$dev = '<DEVICE_ID>'
$pkg = 'com.chillingo.tinytroopersfree.android.aja'
# 找 ReviewPermissions 的 continue 按钮并点击
& $adb -s $dev shell "uiautomator dump /sdcard/ui.xml >/dev/null 2>&1"
$xml = & $adb -s $dev shell "cat /sdcard/ui.xml" 2>&1 | Out-String
$m = [regex]::Matches($xml, 'text="([^"]*)"[^>]*resource-id="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"')
foreach ($x in $m) {
  if ($x.Groups[1].Value -match '继续|CONTINUE|Continue|同意|允许|OK') {
    Write-Output ("BTN: " + $x.Groups[1].Value + " id=" + $x.Groups[2].Value + " bounds=" + $x.Groups[3].Value + "," + $x.Groups[4].Value)
  }
}
$btn = [regex]::Match($xml, 'text="(继续|CONTINUE|Continue|同意|允许|OK)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"')
if ($btn.Success) {
  $cx = ([int]$btn.Groups[2].Value + [int]$btn.Groups[4].Value) / 2
  $cy = ([int]$btn.Groups[3].Value + [int]$btn.Groups[5].Value) / 2
  Write-Output ("clicking " + $cx + "," + $cy)
  & $adb -s $dev shell "input tap $cx $cy"
} else {
  Write-Output "no continue button found; pressing dpad/enter"
  & $adb -s $dev shell "input keyevent KEYCODE_DPAD_DOWN; input keyevent KEYCODE_ENTER"
}
Start-Sleep -Seconds 15
Write-Output "=== pid ==="
& $adb -s $dev shell "pidof $pkg" 2>&1 | Out-String
Write-Output "=== top ==="
& $adb -s $dev shell "dumpsys activity activities | grep -E 'topResumedActivity'" 2>&1 | Out-String
Write-Output "=== logcat ==="
& $adb -s $dev shell "logcat -d -v brief | grep -iE 'tinytroopers|kuaiyouxi|kyx|Unity|FATAL|AndroidRuntime|mono|aja'" 2>&1 | Select-Object -Last 40 | Out-String
