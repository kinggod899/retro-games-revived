import struct, re, zipfile, io, os

def load(path):
    d = open(path,'rb').read()
    pe_off = struct.unpack_from('<I', d, 0x3C)[0]
    coff = pe_off + 4
    num_sec, = struct.unpack_from('<H', d, coff+2)
    opt_size, = struct.unpack_from('<H', d, coff+16)
    opt = coff + 20
    magic, = struct.unpack_from('<H', d, opt)
    dd_off = opt + (112 if magic == 0x20b else 96)
    clr_rva, _ = struct.unpack_from('<II', d, dd_off + 14*8)
    sec_off = opt + opt_size
    secs = []
    for i in range(num_sec):
        o = sec_off + i*40
        vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', d, o+8)
        secs.append((vaddr, vsize, raddr, rsize))
    def rva2off(rva):
        for vaddr, vsize, raddr, rsize in secs:
            if vaddr <= rva < vaddr + max(vsize, rsize):
                return raddr + (rva - vaddr)
    clr = rva2off(clr_rva)
    meta_rva, _ = struct.unpack_from('<II', d, clr+8)
    meta = rva2off(meta_rva)
    vlen, = struct.unpack_from('<I', d, meta+12)
    p = meta + 16 + vlen + 2
    nstreams, = struct.unpack_from('<H', d, p); p += 2
    streams = {}
    for i in range(nstreams):
        s_off, s_size = struct.unpack_from('<II', d, p); p += 8
        e = d.index(b'\x00', p)
        nm = d[p:e].decode('latin1'); p = e + 1
        p = (p + 3) & ~3
        streams[nm] = (meta + s_off, s_size)
    return d, streams

path = r'<WORKSPACE>\work\apk_raw\assets\bin\Data\Managed\Assembly-CSharp.dll'
d, streams = load(path)
off, size = streams['#US']
heap = d[off:off+size]
# user strings: compressed length then UTF-16LE
# crude: extract utf-16 sequences of >=6 printable chars
out = []
i = 0
while i < len(heap) - 2:
    j = i
    chars = []
    while j + 1 < len(heap):
        ch = struct.unpack_from('<H', heap, j)[0]
        if 0x20 <= ch < 0x7f or ch in (0x0a,):
            chars.append(chr(ch)); j += 2
        else:
            break
    if len(chars) >= 6:
        out.append(''.join(chars))
        i = j
    else:
        i += 1

uniq = []
for s in out:
    if s not in uniq: uniq.append(s)
print('user strings:', len(uniq))
kws = re.compile(r'free|Free|buy|Buy|purchase|Purchase|unlock|Unlock|full version|Chapter|chapter|store|Store|crystal|Crystal|dog tag|Dog Tag|upgrade|Upgrade|IAP|WMD|survival|Survival', re.I)
hits = [s for s in uniq if kws.search(s)]
print('--- keyword hits (%d) ---' % len(hits))
for s in hits[:120]:
    print(repr(s))
