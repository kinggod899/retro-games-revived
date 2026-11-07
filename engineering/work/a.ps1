
param([string]$Dev = '<DEVICE_ID>', [string]$Cmd = 'status')
$adb = '<WORKSPACE>\Sdk\platform-tools\adb.exe'
$pkg = 'com.chillingo.tinytroopersfree.android.aja'
$p = ((& $adb -s $Dev shell "pidof $pkg") -join '').Trim()
Write-Output "PID=$p"
switch ($Cmd) {
  'status' {
    & $adb -s $Dev shell "dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'"
    & $adb -s $Dev shell "dumpsys activity activities | grep -E 'topResumedActivity'"
  }
  'maps' { if ($p) { & $adb -s $Dev shell ("grep -E 'libunity|libmono|houdini' /proc/$p/maps") } }
  'log' { if ($p) { & $adb -s $Dev logcat -d -v brief | Select-String -SimpleMatch " $p " | Select-Object -First 60 | ForEach-Object { $_.Line } } }
  'threads' { if ($p) { & $adb -s $Dev shell ("ls /proc/$p/task | wc -l; cat /proc/$p/wchan; echo; cat /proc/$p/stat | cut -d' ' -f3") } }
}
