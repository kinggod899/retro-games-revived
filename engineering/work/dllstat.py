import struct, re, os

base = r'<WORKSPACE>\work\apk_raw\assets\bin\Data\Managed'
for f in ['Assembly-CSharp.dll','Assembly-CSharp-firstpass.dll','UnityEngine.dll']:
    p = os.path.join(base, f)
    d = open(p,'rb').read()
    # .NET metadata: look for #~ stream and count MethodDef/TypeDef via heuristics -> instead grep names
    print('===', f, len(d), 'bytes')
    # find #Strings stream names
    strs = re.findall(rb'[\x20-\x7e]{4,}', d)
    names = [s.decode() for s in strs]
    # heuristic: class names often capitalized identifiers
    print('  sample strings:', names[:1])

d = open(os.path.join(base,'Assembly-CSharp.dll'),'rb').read()
print()
print('=== Assembly-CSharp.dll string sample (unique, filtered) ===')
seen = []
for s in re.findall(rb'[\x20-\x7e]{4,}', d):
    t = s.decode()
    if t.startswith(('get_','set_','<','System.','Unity')):
        continue
    seen.append(t)
print('total strings', len(seen))
print(', '.join(seen[:120]))
