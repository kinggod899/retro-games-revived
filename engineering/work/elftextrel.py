
import struct, sys

class ELF:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        d = self.data
        assert d[:4] == b"\x7fELF", "not elf"
        self.cls = d[4]        # 1=32
        self.end = "<" if d[5] == 1 else ">"
        e = self.end
        (self.e_type, self.e_machine, self.e_version, self.e_entry, self.e_phoff,
         self.e_shoff, self.e_flags, self.e_ehsize, self.e_phentsize, self.e_phnum,
         self.e_shentsize, self.e_shnum, self.e_shstrndx) = struct.unpack_from(e+"HHIIIIIHHHHHH", d, 16)
        self.phdrs = []
        for i in range(self.e_phnum):
            off = self.e_phoff + i*self.e_phentsize
            self.phdrs.append(struct.unpack_from(e+"IIIIIIII", d, off))
        self.shdrs = []
        for i in range(self.e_shnum):
            off = self.e_shoff + i*self.e_shentsize
            self.shdrs.append(struct.unpack_from(e+"IIIIIIIIII", d, off))
        shstr = self.shdrs[self.e_shstrndx]
        self.shstr = d[shstr[4]:shstr[4]+shstr[5]]
        for s in self.shdrs:
            nm = self.shstr[s[0]:].split(b"\x00")[0].decode("latin1")
            s_name = nm
            self.__dict__.setdefault("shnames", []).append(nm)

    def secname(self, i):
        s = self.shdrs[i]
        return self.shstr[s[0]:].split(b"\x00")[0].decode("latin1")

    def dynamic(self):
        dyn = None
        for p in self.phdrs:
            if p[0] == 2:  # PT_DYNAMIC
                dyn = p
        out = []
        if dyn is None: return out
        off, fsz = dyn[1], dyn[4]
        for i in range(fsz//8):
            tag, val = struct.unpack_from(self.end+"iI", self.data, off+i*8)
            out.append((off+i*8, tag, val))
        return out

def analyze(path):
    e = ELF(path)
    print("=====", path, len(e.data), "bytes")
    print("  type=%d machine=%d flags=0x%x" % (e.e_type, e.e_machine, e.e_flags))
    print("  sections:", e.e_shnum, " phdrs:", e.e_phnum)
    # executable segments
    execsegs = [(i,p) for i,p in enumerate(e.phdrs) if p[0]==1 and (p[6] & 1)]
    print("  PT_LOAD exec segments:", [(i, hex(p[2]), hex(p[2]+p[4])) for i,p in execsegs])
    dyntags = {}
    for off, tag, val in e.dynamic():
        dyntags.setdefault(tag, []).append(val)
    print("  DT_TEXTREL present:", 22 in dyntags, dyntags.get(22))
    print("  DT_FLAGS:", [hex(x) for x in dyntags.get(30, [])], " DF_TEXTREL=4")
    print("  DT_FLAGS_1:", [hex(x) for x in dyntags.get(0x6ffffffb, [])])
    print("  DT_REL/RELENT/RELSZ:", dyntags.get(17), dyntags.get(16), dyntags.get(18))
    print("  DT_PLTREL/PLTRELSZ:", dyntags.get(20), dyntags.get(2))
    # relocation sections and their target sections
    n = len(e.shdrs)
    textrel_secs = []
    for i in range(n):
        s = e.shdrs[i]
        sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_align, sh_entsize = s[1:]
        nm = e.secname(i)
        if sh_type in (4, 9):  # REL, RELA
            tname = e.secname(sh_info) if sh_info < n else "?"
            tflags = e.shdrs[sh_info][2] if sh_info < n else 0
            isexec = bool(tflags & 4)
            mark = "  <== TEXTREL" if isexec else ""
            print("    %-22s type=%d size=%-8d -> %-22s exec=%s%s" % (nm, sh_type, sh_size, tname, isexec, mark))
            if isexec: textrel_secs.append((nm, tname, sh_size, sh_entsize))
    print("  TEXTREL relocation sections:", textrel_secs)

for p in sys.argv[1:]:
    analyze(p)
