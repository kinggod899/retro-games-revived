
import struct, sys, shutil, os

DT_NULL = 0
DT_TEXTREL = 22

def patch(src, dst):
    d = bytearray(open(src, "rb").read())
    end = "<" if d[5] == 1 else ">"
    (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize,
     e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from(end+"HHIIIIIHHHHHH", d, 16)
    dyn_off = dyn_size = None
    for i in range(e_phnum):
        p = struct.unpack_from(end+"IIIIIIII", d, e_phoff + i*e_phentsize)
        if p[0] == 2:
            dyn_off, dyn_size = p[1], p[4]
    assert dyn_off is not None, "no PT_DYNAMIC"
    n = dyn_size // 8
    ents = [struct.unpack_from(end+"iI", d, dyn_off + k*8) for k in range(n)]
    idx_textrel = [k for k,(t,v) in enumerate(ents) if t == DT_TEXTREL]
    idx_null = [k for k,(t,v) in enumerate(ents) if t == DT_NULL]
    print("  entries=%d  DT_TEXTREL at %s  first DT_NULL at %s" % (n, idx_textrel, idx_null[:1]))
    if not idx_textrel:
        print("  no DT_TEXTREL, copy as-is")
        shutil.copy2(src, dst)
        return
    ir = idx_textrel[0]
    inull = idx_null[0]
    assert ir < inull, "DT_TEXTREL after terminator?"
    # shift 28..inull-1 left by one, write DT_NULL at inull-1
    for k in range(ir, inull-1):
        struct.pack_into(end+"iI", d, dyn_off + k*8, ents[k+1][0], ents[k+1][1])
    struct.pack_into(end+"iI", d, dyn_off + (inull-1)*8, DT_NULL, 0)
    open(dst, "wb").write(bytes(d))
    # verify
    d2 = open(dst, "rb").read()
    ents2 = [struct.unpack_from(end+"iI", d2, dyn_off + k*8) for k in range(n)]
    print("  after patch: DT_TEXTREL present =", any(t == DT_TEXTREL for t,v in ents2),
          " textrel slot0=%s" % (ents2[ir],))
    print("  size %d -> %d" % (os.path.getsize(src), os.path.getsize(dst)))

patch(sys.argv[1], sys.argv[2])
