
import subprocess, time, os
adb = r"<WORKSPACE>\Sdk\platform-tools\adb.exe"
dev = "<DEVICE_ID>"
def sh(c, t=90):
    return subprocess.run([adb,"-s",dev,"shell",c], capture_output=True, text=True, errors="ignore", timeout=t)
def shot(name):
    sh("screencap -p /sdcard/%s.png" % name)
    subprocess.run([adb,"-s",dev,"pull","/sdcard/%s.png" % name, r"<WORKSPACE>\work\%s.png" % name], capture_output=True, timeout=60)
    return os.path.getsize(r"<WORKSPACE>\work\%s.png" % name)

time.sleep(10)
print("shot after wait:", shot("w1"))
time.sleep(15)
print("shot after wait2:", shot("w2"))
print(sh("logcat -d -s Unity:V | tail -20").stdout)
