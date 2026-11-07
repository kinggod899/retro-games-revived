
import zipfile, os
for apk in [r"<WORKSPACE>\w33_signed.apk", r"<WORKSPACE>\v33_signed.apk", r"<WORKSPACE>\work\test1_signed.apk"]:
    if not os.path.exists(apk):
        print(apk, "MISSING"); continue
    print("=====", os.path.basename(apk), os.path.getsize(apk))
    z = zipfile.ZipFile(apk)
    for i in z.infolist():
        if i.filename.startswith("lib/") or i.filename == "AndroidManifest.xml":
            print("   %-45s size=%-10d comp=%-10d method=%d" % (i.filename, i.file_size, i.compress_size, i.compress_type))
