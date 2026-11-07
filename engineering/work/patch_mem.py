
import struct, sys, shutil

def patch(src, dst, mode):
    d = bytearray(open(src, "rb").read())
    end = "<" if d[5] == 1 else ">"
    (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize,
     e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from(end+"HHIIIIIHHHHHH", d, 16)
    dyn_off = dyn_size = None
    changes = []
    for i in range(e_phnum):
        base = e_phoff + i*e_phentsize
        p = struct.unpack_from(end+"IIIIIIII", d, base)
        if p[0] == 2: dyn_off, dyn_size = p[1], p[4]
        if p[0] == 1 and (p[6] & 1) and not (p[6] & 2):
            newflags = p[6] | 2   # add PF_W to executable load segment
            struct.pack_into(end+"I", d, base+24, newflags)
            changes.append("PT_LOAD[%d] flags 0x%x -> 0x%x" % (i, p[6], newflags))
    if mode != "rwonly":
        n = dyn_size // 8
        for k in range(n):
            off = dyn_off + k*8
            tag, val = struct.unpack_from(end+"iI", d, off)
            if tag == 22:
                struct.pack_into(end+"iI", d, off, 0, 0)   # DT_NULL in place: ends dynamic list
                changes.append("DT_TEXTREL(idx %d) -> DT_NULL" % k)
                break
    open(dst, "wb").write(bytes(d))
    print("  mode=%s: %s" % (mode, changes))

patch(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "rwx")
