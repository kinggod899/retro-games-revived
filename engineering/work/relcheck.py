
import struct, sys

class ELF:
    def __init__(self, path):
        self.data = bytearray(open(path, "rb").read())
        d = self.data
        assert d[:4] == b"\x7fELF"
        self.end = "<" if d[5] == 1 else ">"
        e = self.end
        (self.e_type, self.e_machine, self.e_version, self.e_entry, self.e_phoff,
         self.e_shoff, self.e_flags, self.e_ehsize, self.e_phentsize, self.e_phnum,
         self.e_shentsize, self.e_shnum, self.e_shstrndx) = struct.unpack_from(e+"HHIIIIIHHHHHH", d, 16)
        self.phdrs = [struct.unpack_from(e+"IIIIIIII", d, self.e_phoff + i*self.e_phentsize) for i in range(self.e_phnum)]
        self.shdrs = [struct.unpack_from(e+"IIIIIIIIII", d, self.e_shoff + i*self.e_shentsize) for i in range(self.e_shnum)]
        self.shstr = bytes(d[self.shdrs[self.e_shstrndx][4]:self.shdrs[self.e_shstrndx][4]+self.shdrs[self.e_shstrndx][5]])

    def secname(self, i):
        s = self.shdrs[i]
        return self.shstr[s[0]:].split(b"\x00")[0].decode("latin1")

    def loads(self):
        return [(i,p) for i,p in enumerate(self.phdrs) if p[0]==1]

    def classify(self, addr):
        for i,p in self.loads():
            if p[2] <= addr < p[2]+p[4]:
                w = bool(p[6] & 2); x = bool(p[6] & 1)
                return "PT_LOAD%d %s%s" % (i, "R", ("W" if w else "-") + ("X" if x else "-"))
        return "OUTSIDE"

def check(path):
    e = ELF(path)
    print("=====", path)
    n = len(e.shdrs)
    for i in range(n):
        s = e.shdrs[i]
        if s[1] != 9: continue   # SHT_REL
        nm = e.secname(i)
        if nm != ".rel.plt": continue
        off, size, link, info, ent = s[4], s[5], s[6], s[7], s[9]
        buckets = {}
        minaddr, maxaddr = None, None
        for k in range(size//ent):
            r_off, r_info = struct.unpack_from(e.end+"II", e.data, off + k*ent)
            c = e.classify(r_off)
            buckets[c] = buckets.get(c, 0) + 1
            minaddr = r_off if minaddr is None else min(minaddr, r_off)
            maxaddr = r_off if maxaddr is None else max(maxaddr, r_off)
        print("  %s entries=%d r_offset range 0x%x..0x%x" % (nm, size//ent, minaddr, maxaddr))
        for k, v in sorted(buckets.items()):
            print("     %-24s %d" % (k, v))
        # show the segment name owning the min addr
    # dump PT_DYNAMIC tags
    for i,p in enumerate(e.phdrs):
        if p[0] == 2:
            off, fsz = p[1], p[4]
            print("  PT_DYNAMIC at file 0x%x size %d" % (off, fsz))
            for k in range(fsz//8):
                tag, val = struct.unpack_from(e.end+"iI", e.data, off+k*8)
                if tag in (22, 30, 0x6ffffffb, 23, 25):
                    print("     idx=%d fileoff=0x%x tag=0x%x val=0x%x" % (k, off+k*8, tag, val))

for p in sys.argv[1:]:
    check(p)
