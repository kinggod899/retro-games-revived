
import subprocess, time, os
adb = r"<WORKSPACE>\Sdk\platform-tools\adb.exe"
dev = "<DEVICE_ID>"
def sh(c, t=90):
    return subprocess.run([adb,"-s",dev,"shell",c], capture_output=True, text=True, errors="ignore", timeout=t)
def shot(name):
    sh("screencap -p /sdcard/%s.png" % name)
    subprocess.run([adb,"-s",dev,"pull","/sdcard/%s.png" % name, r"<WORKSPACE>\work\%s.png" % name], capture_output=True, timeout=60)
    p = r"<WORKSPACE>\work\%s.png" % name
    return os.path.getsize(p) if os.path.exists(p) else -1

print("tap OK:", sh("input tap 639 366").stdout)
time.sleep(3)
print("shot:", shot("v1"))
# tap 战役 (campaign)
print("tap campaign:", sh("input tap 1135 211").stdout)
time.sleep(6)
print("shot:", shot("v2"))
print(sh("dumpsys activity activities | grep topResumedActivity").stdout)
