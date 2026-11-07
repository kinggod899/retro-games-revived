
import re, os, shutil
src = r"<WORKSPACE>\apt"
dst = r"<WORKSPACE>\t2"
if os.path.exists(dst): shutil.rmtree(dst)
shutil.copytree(src, dst)

mf = os.path.join(dst, "AndroidManifest.xml")
s = open(mf, encoding="utf-8").read()

# 1. 去掉 Kyx ShellApplication
s = s.replace(' android:name="com.kuaiyouxi.gamepad.sdk.shell.ShellApplication"', '')

# 2. 找到 LauncherActivity 的 launcher intent-filter 并改成 UnityPlayerActivity
print("--- launcher activity block ---")
m = re.search(r'<activity[^>]*LauncherActivity[^>]*>(.*?)</activity>', s, re.S)
print(m.group(0)[:600] if m else "NOT FOUND")

open(mf, "w", encoding="utf-8").write(s)
print("manifest written, len", len(s))

# 3. 替换 lib 为真实库
sdir = r"<WORKSPACE>\work\apk_raw\assets\libs\armeabi-v7a"
tdir = os.path.join(dst, "lib", "armeabi-v7a")
for n in ("libunity.so", "libmono.so"):
    shutil.copy2(os.path.join(sdir, n), os.path.join(tdir, n))
    print(n, os.path.getsize(os.path.join(tdir, n)))
