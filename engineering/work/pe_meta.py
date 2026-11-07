import struct, re, os

def parse_pe_metadata_strings(path):
    d = open(path,'rb').read()
    pe_off = struct.unpack_from('<I', d, 0x3C)[0]
    assert d[pe_off:pe_off+4] == b'PE\x00\x00'
    coff = pe_off + 4
    num_sec, = struct.unpack_from('<H', d, coff+2)
    opt_size, = struct.unpack_from('<H', d, coff+16)
    opt = coff + 20
    magic, = struct.unpack_from('<H', d, opt)
    is64 = magic == 0x20b
    dd_off = opt + (112 if is64 else 96)
    # CLR runtime header = data dir index 14
    clr_rva, clr_size = struct.unpack_from('<II', d, dd_off + 14*8)
    sec_off = opt + opt_size
    secs = []
    for i in range(num_sec):
        o = sec_off + i*40
        name = d[o:o+8].rstrip(b'\x00').decode('latin1')
        vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', d, o+8)
        secs.append((name, vaddr, vsize, raddr, rsize))
    def rva2off(rva):
        for name, vaddr, vsize, raddr, rsize in secs:
            if vaddr <= rva < vaddr + max(vsize, rsize):
                return raddr + (rva - vaddr)
        return None
    clr = rva2off(clr_rva)
    meta_rva, meta_size = struct.unpack_from('<II', d, clr+8)
    meta = rva2off(meta_rva)
    assert d[meta:meta+4] == b'BSJB', d[meta:meta+4]
    vlen, = struct.unpack_from('<I', d, meta+12)
    p = meta + 16 + vlen
    p += 2  # flags
    nstreams, = struct.unpack_from('<H', d, p); p += 2
    streams = {}
    for i in range(nstreams):
        s_off, s_size = struct.unpack_from('<II', d, p); p += 8
        e = d.index(b'\x00', p)
        nm = d[p:e].decode('latin1'); p += (e - p) + 1
        p = (p + 3) & ~3
        streams[nm] = (meta + s_off, s_size)
    return d, streams

for f in ['Assembly-CSharp.dll','Assembly-CSharp-firstpass.dll','UnityEngine.dll']:
    path = os.path.join(r'<WORKSPACE>\work\apk_raw\assets\bin\Data\Managed', f)
    d, streams = parse_pe_metadata_strings(path)
    off, size = streams.get('#Strings', (0,0))
    print('===', f, 'streams:', list(streams.keys()), 'strings heap', size)
    if not size: continue
    heap = d[off:off+size]
    names = [s.decode('utf-8','replace') for s in heap.split(b'\x00') if len(s) > 2]
    print('  total names:', len(names))
    interesting = [n for n in names if re.fullmatch(r'[A-Z][A-Za-z0-9_]{2,40}', n)]
    print('  sample:', ', '.join(interesting[:60]))
