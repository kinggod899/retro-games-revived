import struct, io, zipfile, collections

d = open(r'<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk','rb').read()
z = zipfile.ZipFile(io.BytesIO(d))
dex = z.read('classes.dex')

# dex header
string_ids_size, string_ids_off = struct.unpack_from('<II', dex, 0x38)
type_ids_size, type_ids_off = struct.unpack_from('<II', dex, 0x40)
class_defs_size, class_defs_off = struct.unpack_from('<II', dex, 0x60)

def uleb(off):
    result = 0; shift = 0
    while True:
        b = dex[off]; off += 1
        result |= (b & 0x7f) << shift
        if not (b & 0x80): break
        shift += 7
    return result, off

def get_string(idx):
    off = struct.unpack_from('<I', dex, string_ids_off + idx*4)[0]
    _, off = uleb(off)  # utf16 len
    end = dex.index(b'\x00', off)
    return dex[off:end].decode('utf-8', 'replace')

types = [get_string(struct.unpack_from('<I', dex, type_ids_off + i*4)[0]) for i in range(type_ids_size)]

classes = []
for i in range(class_defs_size):
    o = class_defs_off + i*32
    class_idx, access, super_idx, ifaces, src, annot, class_data_off, static_vals = struct.unpack_from('<8I', dex, o)
    classes.append(types[class_idx])

print('dex strings:', string_ids_size, 'types:', type_ids_size, 'classes:', class_defs_size)

pkg = collections.Counter()
for c in classes:
    name = c.lstrip('L').rstrip(';')
    parts = name.split('/')
    pkg['/'.join(parts[:2]) if len(parts) > 2 else '/'.join(parts[:1])] += 1

print('\n=== top 40 packages by class count ===')
for k, v in pkg.most_common(40):
    print('%5d  %s' % (v, k))
