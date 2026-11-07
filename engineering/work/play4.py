import subprocess, time, os
adb = r"<WORKSPACE>\Sdk\platform-tools\adb.exe"
dev = "<DEVICE_ID>"
def sh(c, t=90):
    return subprocess.run([adb,"-s",dev,"shell",c], capture_output=True, text=True, errors="ignore", timeout=t)
def shot(name):
    sh("screencap -p /sdcard/%s.png" % name)
    subprocess.run([adb,"-s",dev,"pull","/sdcard/%s.png" % name, "<WORKSPACE>\\work\\%s.png" % name], capture_output=True, timeout=60)
    return os.path.getsize("<WORKSPACE>\\work\\%s.png" % name)
sh("input tap 1000 400")
time.sleep(4)
print("mv1:", shot("mv1"))
sh("input tap 1100 300")
time.sleep(5)
print("mv2:", shot("mv2"))
print(sh("logcat -d -s Unity:V | tail -8").stdout)