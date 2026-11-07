
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
raw = open(r"<WORKSPACE>\work\maps.txt", "rb").read()
if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
    text = raw.decode("utf-16")
elif raw[:3] == b"\xef\xbb\xbf":
    text = raw.decode("utf-8-sig")
else:
    text = raw.decode("utf-8", "replace")
lines = text.splitlines()
print("lines:", len(lines))
print("sample:", lines[0] if lines else "EMPTY")
targets = [0xd7595ee5, 0xd7594ee5, 0xd75adee5, 0xd7c22e88, 0xd79b4ff4]
ranges = []
for line in lines:
    m = re.match(r"([0-9a-fA-F]+)-([0-9a-fA-F]+)\s+(\S+)\s+([0-9a-fA-F]+)\s+(\S+)\s+(\d+)\s*(.*)", line)
    if m:
        ranges.append((int(m.group(1),16), int(m.group(2),16), m.group(3), int(m.group(4),16), m.group(7).strip()))
print("ranges:", len(ranges))
for t in targets:
    hit = [r for r in ranges if r[0] <= t < r[1]]
    if hit:
        r = hit[0]
        print(f"0x{t:x} -> {r[4] or '[anon]'} range=0x{r[0]:x}-0x{r[1]:x} perms={r[2]} fileoff=0x{r[3]:x} delta=0x{t-r[0]:x} file_off=0x{t-r[0]+r[3]:x}")
    else:
        print(f"0x{t:x} -> NOT MAPPED")
print("--- regions in d7000000-d8000000 ---")
for r in ranges:
    if 0xd7000000 <= r[0] < 0xd8000000:
        print(f"  0x{r[0]:x}-0x{r[1]:x} {r[2]} off=0x{r[3]:x} {r[4] or '[anon]'}")
