import zipfile, struct, io

data = open(r'<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk','rb').read()
z = zipfile.ZipFile(io.BytesIO(data))
ax = z.read('AndroidManifest.xml')

def parse_string_pool(buf, off):
    typ, hsz, sz = struct.unpack_from('<HHI', buf, off)
    cnt, styc, flags, strstart, styoff = struct.unpack_from('<IIIII', buf, off+8)
    utf8 = bool(flags & 0x100)
    offs = struct.unpack_from('<%dI'%cnt, buf, off+28)
    out = []
    base = off + strstart
    for o in offs:
        p = base + o
        if utf8:
            l16 = buf[p]; p += 1
            if l16 & 0x80: p += 1
            l8 = buf[p]; p += 1
            if l8 & 0x80:
                l8 = ((l8 & 0x7f) << 8) | buf[p]; p += 1
            out.append(buf[p:p+l8].decode('utf-8', 'replace'))
        else:
            l = struct.unpack_from('<H', buf, p)[0]; p += 2
            if l & 0x8000:
                l = ((l & 0x7fff) << 16) | struct.unpack_from('<H', buf, p)[0]; p += 2
            out.append(buf[p:p+l*2].decode('utf-16-le', 'replace'))
    return out

strings = []
resmap = []
off = 8
while off < len(ax):
    typ, hsz, sz = struct.unpack_from('<HHI', ax, off)
    if typ == 0x0001 and not strings:
        strings = parse_string_pool(ax, off)
    elif typ == 0x0180:
        n = (sz - hsz)//4
        resmap = list(struct.unpack_from('<%dI'%n, ax, off+hsz))
    off += sz

ANDROID = {0x0101021b:'versionCode',0x0101021c:'versionName',0x01010270:'minSdkVersion',
        0x01010271:'targetSdkVersion',0x01010003:'name',0x01010000:'theme',
        0x01010010:'exported',0x0101000f:'enabled',0x0101021e:'resizeableActivity',
        0x01010018:'authorities',0x01010001:'label',0x01010002:'icon',
        0x01010572:'extractNativeLibs',0x0101021f:'hardwareAccelerated',
        0x01010020:'description',0x0101000e:'permission',0x01010006:'permission',
        0x0101021d:'sharedUserId',0x0101031f:'required',0x01010272:'targetSdkVersionX'}

def fmt_val(dt, d, raw):
    if dt == 0x03: return strings[d] if d < len(strings) else '?'
    if dt == 0x01: return ('0x%08x' % d)
    if dt == 0x10: return str(d)
    if dt == 0x12: return 'true' if d else 'false'
    if dt == 0x11: return str(struct.unpack('<f', struct.pack('<I', d))[0])
    if raw != 0xffffffff and raw < len(strings): return strings[raw]
    return str(d)

out = []
off = 8
depth = 0
while off < len(ax):
    typ, hsz, sz = struct.unpack_from('<HHI', ax, off)
    if typ == 0x0102:
        ns_i, name_i, astart, asize, acount = struct.unpack_from('<IIHHH', ax, off+16)
        name = strings[name_i]
        out.append('  ' * depth + '<' + name)
        depth += 1
        for i in range(acount):
            a = off + astart + i*asize
            ans, aname, raw, vsz, r0, dt, dv = struct.unpack_from('<IIIHBBI', ax, a)
            if aname < len(resmap) and resmap[aname]:
                nm = ANDROID.get(resmap[aname], 'res#0x%08x' % resmap[aname])
            elif aname != 0xffffffff and aname < len(strings):
                nm = strings[aname]
            else:
                nm = '?'
            out.append('  ' * depth + '    ' + nm + ' = ' + str(fmt_val(dt, dv, raw)))
    elif typ == 0x0103:
        depth = max(0, depth-1)
        out.append('  ' * depth + '/>')
    off += sz

print('\n'.join(out))
