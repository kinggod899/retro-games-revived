import struct, re, os, zipfile, io

# 1) lib/ (43KB) vs assets/libs (6.8MB) comparison
for p in [r'<WORKSPACE>\work\apk_raw\lib\armeabi-v7a\libunity.so',
          r'<WORKSPACE>\work\apk_raw\assets\libs\armeabi-v7a\libunity.so']:
    d = open(p,'rb').read()
    print(os.path.basename(os.path.dirname(os.path.dirname(p))), 'size', len(d))
    print('  soname/strings:', [s.decode() for s in re.findall(rb'[\x20-\x7e]{6,}', d)][:12])

# 2) Assets level scene names from mainData / level files
z = zipfile.ZipFile(r'<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk')
levels = sorted([n for n in z.namelist() if re.match(r'assets/bin/Data/level\d+$', n)],
                key=lambda x: int(x.split('level')[-1]))
print()
print('level files:', len(levels))
d = z.read('assets/bin/Data/level0')
print('level0 strings:', [s.decode() for s in re.findall(rb'[\x20-\x7e]{5,}', d)][:10])

# 3) settings.xml full
print()
print('settings.xml:', z.read('assets/bin/Data/settings.xml').decode('utf-8','replace'))
# 4) version.properties
print('version.properties:', z.read('assets/version.properties')[:400])
print('kyx_version:', z.read('assets/kyx_version')[:200])
print('kyx_md5:', z.read('assets/kyx_md5')[:200])
print('kyx_data head:', z.read('assets/kyx_data')[:200])
