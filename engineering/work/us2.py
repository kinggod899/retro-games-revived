import struct, re, io

path = r'<WORKSPACE>\work\apk_raw\assets\bin\Data\Managed\Assembly-CSharp.dll'
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

heapoff, heapsize = streams['#US']
heap = d[heapoff:heapoff+heapsize]
out = []
i = 0
while i < len(heap) - 2:
    j = i; chars = []
    while j + 1 < len(heap):
        ch = struct.unpack_from('<H', heap, j)[0]
        if 0x20 <= ch < 0x7f:
            chars.append(chr(ch)); j += 2
        else:
            break
    if len(chars) >= 6:
        out.append(''.join(chars)); i = j
    else:
        i += 1
uniq = []
for s in out:
    if s not in uniq: uniq.append(s)
open(r'<WORKSPACE>\work\user_strings.txt','w',encoding='utf-8').write('\n'.join(uniq))
print('written', len(uniq))

pats = re.compile(r'LOCK|lock|LEVEL_|MISSION_|CHAPTER|POPUP_|FULL|PREMIUM|TRIAL|DEMO|BUY_FULL|UPGRADE_|RANK|TUTORIAL_HEADER', re.I)
sel = [s for s in uniq if pats.search(s)]
print('--- filtered', len(sel), '---')
for s in sel[:150]:
    print(s)
