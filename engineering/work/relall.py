
import struct, sys

def classify(loads, addr):
    for i,p in loads:
        if p[2] <= addr < p[2]+p[5]:
            return "PT_LOAD%d %s%s%s" % (i, "R", "W" if p[6]&2 else "-", "X" if p[6]&1 else "-")
    return "OUTSIDE"

def check(path):
    d = open(path,"rb").read()
    end = "<" if d[5]==1 else ">"
    (e_type,e_machine,e_version,e_entry,e_phoff,e_shoff,e_flags,e_ehsize,
     e_phentsize,e_phnum,e_shentsize,e_shnum,e_shstrndx) = struct.unpack_from(end+"HHIIIIIHHHHHH", d, 16)
    ph = [struct.unpack_from(end+"IIIIIIII", d, e_phoff+i*e_phentsize) for i in range(e_phnum)]
    loads = [(i,p) for i,p in enumerate(ph) if p[0]==1]
    sh = [struct.unpack_from(end+"IIIIIIIIII", d, e_shoff+i*e_shentsize) for i in range(e_shnum)]
    shstr = d[sh[e_shstrndx][4]:sh[e_shstrndx][4]+sh[e_shstrndx][5]]
    def nm(i):
        return shstr[sh[i][0]:].split(b"\x00")[0].decode("latin1")
    print("=====", path.rsplit("\\",1)[-1])
    total_text = 0
    for i in range(e_shnum):
        s = sh[i]
        if s[1] != 9: continue
        off, size, ent = s[4], s[5], s[9] or 8
        buckets = {}
        text_examples = []
        for k in range(size//ent):
            r_off, r_info = struct.unpack_from(end+"II", d, off+k*ent)
            c = classify(loads, r_off)
            buckets[c] = buckets.get(c,0)+1
            if "X" in c and len(text_examples) < 5:
                text_examples.append((hex(r_off), r_info & 0xff))
        print("  %-12s n=%-6d %s" % (nm(i), size//ent, buckets))
        if text_examples: print("     text targets:", text_examples)
        total_text += sum(v for k,v in buckets.items() if "X" in k)
    print("  TOTAL relocations into executable segment:", total_text)

for p in sys.argv[1:]:
    check(p)
