import re, zipfile, io, struct, collections

z = zipfile.ZipFile(r'<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk')
names = ["assets/bin/Data/level%d" % i for i in range(49)]
print('=== scene hint strings per level ===')
for n in names:
    try:
        d = z.read(n)
    except KeyError:
        print(n, 'MISSING'); continue
    ss = [s.decode('latin1') for s in re.findall(rb'[\x20-\x7e]{6,}', d)]
    # heuristics: scene-ish words
    keep = [s for s in ss if re.search(r'Menu|Level|Scene|Chapter|Mission|Zombie|Survival|Briefing|Campaign|Bootcamp|BootCamp|Intro|Credits|Splash|Store|HQ|Cemetery|Gamemode', s)]
    # dedupe preserving order
    seen = []
    for s in keep:
        if s not in seen: seen.append(s)
    print(n, '->', ', '.join(seen[:9]) if seen else '(none)')

print()
print('=== free/demo markers in Assembly-CSharp strings heap ===')
dz = z.read('assets/bin/Data/Managed/Assembly-CSharp.dll')
for kw in [b'free', b'Free', b'demo', b'Demo', b'full version', b'FullVersion', b'buy', b'Purchase', b'chapter', b'Chapter', b'Tiny Troopers', b'kukouri', b'Chillingo']:
    c = dz.count(kw)
    print('  %-18s %d' % (kw.decode(), c))
