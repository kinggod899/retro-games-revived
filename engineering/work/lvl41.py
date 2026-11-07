import re, zipfile, struct

z = zipfile.ZipFile(r'<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk')

# ChapterSelect scene (level41) full object name list
d = z.read('assets/bin/Data/level41')
ss = [s.decode('latin1') for s in re.findall(rb'[\x20-\x7e]{4,}', d)]
uniq = []
for s in ss:
    if s not in uniq: uniq.append(s)
print('=== level41 distinct strings (%d) ===' % len(uniq))
print(', '.join(uniq[:200]))
