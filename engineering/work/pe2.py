import struct, os

path = r'<WORKSPACE>\work\apk_raw\assets\bin\Data\Managed\Assembly-CSharp.dll'
d = open(path,'rb').read()
pe_off = struct.unpack_from('<I', d, 0x3C)[0]
coff = pe_off + 4
num_sec, = struct.unpack_from('<H', d, coff+2)
opt_size, = struct.unpack_from('<H', d, coff+16)
opt = coff + 20
magic, = struct.unpack_from('<H', d, opt)
is64 = magic == 0x20b
dd_off = opt + (112 if is64 else 96)
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

off, size = streams['#~']
p = off
p += 4
major, minor, heap_sizes, r2 = struct.unpack_from('<BBBB', d, p); p += 4
valid, = struct.unpack_from('<Q', d, p); p += 8
p += 8
rows = {}
present = []
for i in range(64):
    if valid & (1 << i):
        rows[i] = struct.unpack_from('<I', d, p)[0]; p += 4
        present.append(i)
print('heap_sizes', heap_sizes, 'present tables', present)
print('rows', {hex(k):v for k,v in rows.items()})
print('tables data starts at', p, 'stream at', off, 'size', size)
