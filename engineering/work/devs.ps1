$adb='<WORKSPACE>\Sdk\platform-tools\adb.exe'
foreach ($s in @('<DEVICE_ID>','<DEVICE_ID>','<DEVICE_ID>','<DEVICE_ID>')) {
  Write-Output ('=== ' + $s + ' ===')
  & $adb -s $s shell getprop ro.build.version.sdk 2>&1 | Out-String
  & $adb -s $s shell getprop ro.build.version.release 2>&1 | Out-String
  & $adb -s $s shell getprop ro.product.cpu.abilist 2>&1 | Out-String
  & $adb -s $s shell getprop ro.product.model 2>&1 | Out-String
}