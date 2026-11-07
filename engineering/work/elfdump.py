
import struct, sys

def dump(path):
    d = open(path, "rb").read()
    end = "<" if d[5] == 1 else ">"
    (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize,
     e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from(end+"HHIIIIIHHHHHH", d, 16)
    print("=====", path)
    print("-- program headers --")
    for i in range(e_phnum):
        p = struct.unpack_from(end+"IIIIIIII", d, e_phoff + i*e_phentsize)
        names = {1:"LOAD",2:"DYNAMIC",3:"INTERP",4:"NOTE",6:"PHDR",7:"TLS",0x6474e550:"GNU_EH_FRAME",0x6474e551:"GNU_STACK",0x6474e552:"GNU_RELRO"}
        fl = ("R" if p[6]&4 else "-") + ("W" if p[6]&2 else "-") + ("X" if p[6]&1 else "-")
        print("  %-12s off=0x%06x vaddr=0x%08x filesz=0x%06x memsz=0x%06x flags=%s align=0x%x" % (
            names.get(p[0], hex(p[0])), p[1], p[2], p[4], p[5], fl, p[7]))
    shstr = d[e_shoff + e_shstrndx*e_shentsize:][:64]
    soff = struct.unpack_from(end+"I", d, e_shoff + e_shstrndx*e_shentsize + 4)[0]
    ssize = struct.unpack_from(end+"I", d, e_shoff + e_shstrndx*e_shentsize + 5*4)[0]
    shstrb = d[soff:soff+ssize]
    print("-- sections --")
    for i in range(e_shnum):
        s = struct.unpack_from(end+"IIIIIIIIII", d, e_shoff + i*e_shentsize)
        nm = shstrb[s[0]:].split(b"\x00")[0].decode("latin1")
        fl = ("W" if s[2]&1 else "-") + ("A" if s[2]&2 else "-") + ("X" if s[2]&4 else "-")
        print("  %-20s type=%-3d flags=%-3s addr=0x%08x off=0x%06x size=0x%06x" % (nm, s[1], fl, s[3], s[4], s[5]))

dump(sys.argv[1])
