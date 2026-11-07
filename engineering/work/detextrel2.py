
import struct, sys, shutil, os
DT_TEXTREL = 22
DT_BIND_NOW = 24

def patch(src, dst):
    d = bytearray(open(src, "rb").read())
    end = "<" if d[5] == 1 else ">"
    (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize,
     e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from(end+"HHIIIIIHHHHHH", d, 16)
    dyn_off = dyn_size = None
    for i in range(e_phnum):
        p = struct.unpack_from(end+"IIIIIIII", d, e_phoff + i*e_phentsize)
        if p[0] == 2: dyn_off, dyn_size = p[1], p[4]
    n = dyn_size // 8
    idx = [k for k in range(n) if struct.unpack_from(end+"iI", d, dyn_off+k*8)[0] == DT_TEXTREL]
    if not idx:
        shutil.copy2(src, dst); print("  no DT_TEXTREL"); return
    for k in idx:
        struct.pack_into(end+"iI", d, dyn_off+k*8, DT_BIND_NOW, 0)
    open(dst,"wb").write(bytes(d))
    print("  replaced %d DT_TEXTREL with DT_BIND_NOW (no shift)" % len(idx))

patch(sys.argv[1], sys.argv[2])
