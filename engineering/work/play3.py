
import subprocess, time, os
adb = r"<WORKSPACE>\Sdk\platform-tools\adb.exe"
dev = "<DEVICE_ID>"
def sh(c, t=90):
    return subprocess.run([adb,"-s",dev,"shell",c], capture_output=True, text=True, errors="ignore", timeout=t)
def shot(name):
    sh("screencap -p /sdcard/%s.png" % name)
    subprocess.run([adb,"-s",dev,"pull","/sdcard/%s.png" % name, r"<WORKSPACE>\work\%s.png" % name], capture_output=True, timeout=60)
    return os.path.getsize(r"<WORKSPACE>\work\%s.png" % name)

# try campaign
sh("input tap 1135 211"); time.sleep(8); print("campaign:", shot("c1"))
# try tutorial
sh("input tap 1135 481"); time.sleep(8); print("tutorial:", shot("c2"))
print(sh("dumpsys activity activities | grep topResumedActivity").stdout)
print(sh("logcat -d -s Unity:V | tail -12").stdout)
