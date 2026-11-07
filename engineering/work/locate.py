
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
targets = [0xd7595ee5, 0xd7594ee5, 0xd75adee5, 0xd7c22e88, 0xd79b4ff4]
maps = open(r"<WORKSPACE>\work\maps.txt", encoding="utf-8", errors="replace").read().splitlines()
ranges = []
for line in maps:
    m = re.match(r"([0-9a-f]+)-([0-9a-f]+)\s+(\S+)\s+([0-9a-f]+)\s+(\S+)\s+(\d+)\s*(.*)", line)
    if m:
        ranges.append((int(m.group(1),16), int(m.group(2),16), m.group(3), int(m.group(4),16), m.group(7).strip()))
print("ranges:", len(ranges))
for t in targets:
    hit = [r for r in ranges if r[0] <= t < r[1]]
    if hit:
        r = hit[0]
        off = t - r[0] + r[3]
        print(f"0x{t:x} -> {r[4] or '[anon]'} base=0x{r[0]:x} perms={r[2]} fileoff=0x{r[3]:x} vaddr_off=0x{t-r[0]:x} file_off=0x{off:x}")
    else:
        print(f"0x{t:x} -> NOT IN ANY MAPPING")
print("--- mappings near d7500000-d7a00000 ---")
for r in ranges:
    if 0xd7000000 <= r[0] < 0xd8000000:
        print(f"  0x{r[0]:x}-0x{r[1]:x} {r[2]} off=0x{r[3]:x} {r[4]}")
