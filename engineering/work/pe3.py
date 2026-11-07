import struct, sys, io

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

def read_str(d, streams, idx):
    off, size = streams['#Strings']
    if idx == 0: return ''
    p = off + idx
    e = d.index(b'\x00', p)
    return d[p:e].decode('utf-8','replace')

path = r'<WORKSPACE>\work\apk_raw\assets\bin\Data\Managed\Assembly-CSharp.dll'
d, streams = load(path)
off, size = streams['#~']
p = off + 4
major, minor, heap_sizes, r2 = struct.unpack_from('<BBBB', d, p); p += 4
valid, = struct.unpack_from('<Q', d, p); p += 8
p += 8
rows = {}
present = []
for i in range(64):
    if valid & (1 << i):
        rows[i] = struct.unpack_from('<I', d, p)[0]; p += 4
        present.append(i)

str_sz = 4 if heap_sizes & 1 else 2
guid_sz = 4 if heap_sizes & 2 else 2
blob_sz = 4 if heap_sizes & 4 else 2

mod_off = p
p += rows.get(0,0) * (2 + str_sz + 3*guid_sz)
typeref_off = p
p += rows.get(1,0) * (2 + str_sz + str_sz)
typedef_off = p
td_row = 4 + str_sz + str_sz + 2 + 2 + 2
p += rows.get(2,0) * td_row
methoddef_off = p  # after TypeDef comes Field(0x04) then MethodDef(0x06)

field_off = typedef_off + rows.get(2,0)*td_row
fd_row = 2 + str_sz + blob_sz
method_off = field_off + rows.get(4,0)*fd_row
md_row = 4 + 2 + 2 + str_sz + blob_sz + 2

print('TypeDef names (664):')
out = []
for i in range(rows[2]):
    o = typedef_off + i*td_row
    flags, = struct.unpack_from('<I', d, o)
    name_i, = struct.unpack_from('<I', d, o+4)
    ns_i, = struct.unpack_from('<I', d, o+8)
    nm = read_str(d, streams, name_i)
    ns = read_str(d, streams, ns_i)
    out.append((ns, nm, flags))

import collections
by_ns = collections.Counter(ns for ns, nm, f in out)
print('namespaces:', len(by_ns))
for k, v in by_ns.most_common(30):
    print('%4d  %s' % (v, k if k else '<global>'))
print()
print('=== global namespace classes ===')
for ns, nm, f in out:
    if ns == '':
        print(' ', nm)
