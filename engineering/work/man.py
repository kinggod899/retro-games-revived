import sys
sys.stdout.reconfigure(encoding="utf-8")
from pyaxmlparser import APK
a = APK(r"<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk")
m = a.get_android_manifest_xml()
s = m.toprettyxml(indent=" ")
open(r"<WORKSPACE>\work\manifest.xml","w",encoding="utf-8").write(s)
print("len", len(s))
print(s[:200])
print("--- activities ---")
for act in a.get_activities():
    print(" A", act)
for s2 in a.get_services():
    print(" S", s2)
for r2 in a.get_receivers():
    print(" R", r2)
print("--- permissions ---")
for p in a.get_permissions():
    print(" P", p)
print("--- xmltree of uses-sdk ---")
