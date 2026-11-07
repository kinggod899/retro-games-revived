import re, zipfile, struct

z = zipfile.ZipFile(r'<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk')

# 1) 43KB libunity.so 是什么
d = z.read('lib/armeabi-v7a/libunity.so')
print('=== lib/armeabi-v7a/libunity.so (43KB) ===')
print('size', len(d))
ss = [s.decode('latin1') for s in re.findall(rb'[\x20-\x7e]{5,}', d)]
print('strings:', ', '.join(ss[:40]))
print()
print('=== lib/armeabi-v7a/libmono.so (84KB) strings ===')
m = z.read('lib/armeabi-v7a/libmono.so')
print('size', len(m), [s.decode('latin1') for s in re.findall(rb'[\x20-\x7e]{6,}', m)][:30])

# 2) 真实 libunity.so 导出 JNI 符号(判断是否 UnityPlayer 正常)
u = z.read('assets/libs/armeabi-v7a/libunity.so')
print()
print('=== real libunity.so JNI exports ===')
print([s.decode() for s in re.findall(rb'Java_[A-Za-z0-9_]{5,}', u)][:20])

# 3) dex 里是否有 arm64 / x86 相关
print()
print('=== apk abi folders ===')
print([n for n in z.namelist() if n.startswith('lib/') or n.startswith('assets/libs/')][:20])
