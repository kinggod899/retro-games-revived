import sys, struct, zipfile, io, os
sys.stdout.reconfigure(encoding="utf-8")
apk = r"<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk"
z = zipfile.ZipFile(apk)
names = [n for n in z.namelist() if n.endswith(".dex")]
print("dex files:", names)
def parse_dex(data, fname):
    string_ids_size, string_ids_off = struct.unpack_from("<II", data, 56)
    type_ids_size, type_ids_off = struct.unpack_from("<II", data, 64)
    def uleb(off):
        r = 0; s = 0
        while True:
            b = data[off]; off += 1
            r |= (b & 0x7f) << s
            if not (b & 0x80): break
            s += 7
        return r, off
    strs = []
    for i in range(string_ids_size):
        off = struct.unpack_from("<I", data, string_ids_off + i*4)[0]
        l, o = uleb(off)
        strs.append(data[o:o+l].decode("utf-8", "replace"))
    types = []
    for i in range(type_ids_size):
        idx = struct.unpack_from("<I", data, type_ids_off + i*4)[0]
        types.append(strs[idx])
    return types
alltypes = []
for n in names:
    data = z.read(n)
    t = parse_dex(data, n)
    alltypes.extend(t)
print("total type ids:", len(alltypes))
for pref in ["Lcom/unity3d/player/", "Lcom/chillingo/", "Lcom/prime31/"]:
    sel = sorted(set(x for x in alltypes if x.startswith(pref)))
    print(f"--- {pref} ({len(sel)}) ---")
    if pref != "Lcom/prime31/":
        for s in sel: print("  ", s)
    else:
        for s in sel[:15]: print("  ", s)
        print("   ...")
