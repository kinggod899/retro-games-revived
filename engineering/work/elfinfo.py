import struct, sys, os
def info(p):
    with open(p,'rb') as f:
        data = f.read(64)
        if data[:4] != b"\x7fELF":
            return f"{p}: NOT ELF"
        ei_class = data[4]; ei_data = data[5]
        e_type = struct.unpack_from('<H', data, 16)[0]
        e_machine = struct.unpack_from('<H', data, 18)[0]
        # read program headers
        with open(p,'rb') as f:
            f.seek(0)
            hdr = f.read(52)
            e_phoff = struct.unpack_from('<I', hdr, 28)[0]
            e_phentsize = struct.unpack_from('<H', hdr, 42)[0]
            e_phnum = struct.unpack_from('<H', hdr, 44)[0]
            f.seek(e_phoff)
            phs = f.read(e_phentsize*e_phnum)
        flags_all = set()
        for i in range(e_phnum):
            off = i*e_phentsize
            p_type = struct.unpack_from('<I', phs, off)[0]
            p_flags = struct.unpack_from('<I', phs, off+24)[0]
            if p_type == 1:  # PT_LOAD
                flags_all.add(p_flags)
        hasexec_load = any(fl & 1 for fl in flags_all)
        return f"{os.path.basename(p)}: type={e_type}({'DYN/PIE' if e_type==3 else 'EXEC/NON-PIE' if e_type==2 else '?'}) machine={e_machine} loadwX={hasexec_load} size={os.path.getsize(p)}"
for p in sys.argv[1:]:
    print(info(p))
