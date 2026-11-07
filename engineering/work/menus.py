import re, zipfile

z = zipfile.ZipFile(r'<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk')

def strs(n):
    d = z.read(n)
    uniq = []
    for s in re.findall(rb'[\x20-\x7e]{4,}', d):
        t = s.decode('latin1')
        if t not in uniq: uniq.append(t)
    return uniq

for i in [31,34,36,37,38,43,44,45,46,47,48]:
    n = 'assets/bin/Data/level%d' % i
    u = strs(n)
    keep = [s for s in u if re.search(r'Menu|Store|Shop|Credits|Briefing|Chapter|Level|Campaign|Zombie|Upgrade|Splash|EULA|Settings|World|Map$|MapMove|Tutorial|Boot', s)]
    print('level%-3d %s' % (i, ', '.join(dict.fromkeys(keep))[:220]))

print()
print('=== 关卡数统计 (level1..level30 -> 真实游戏关) ===')
game = []
for i in range(1, 32):
    n = 'assets/bin/Data/level%d' % i
    u = strs(n)
    lv = sorted({s for s in u if re.match(r'^Level\d+$', s)})
    game.append((i, lv))
for i, lv in game:
    print('level%-3d %s' % (i, lv))
