
import zipfile, shutil, os, sys
sys.stdout.reconfigure(encoding="utf-8")
src = r"<WORKSPACE>\<QQ_ID>\<QQ_ID>\base.apk"
dst = r"<WORKSPACE>\work\test1.apk"
real_unity = r"<WORKSPACE>\work\apk_raw\assets\libs\armeabi-v7a\libunity.so"
real_mono  = r"<WORKSPACE>\work\apk_raw\assets\libs\armeabi-v7a\libmono.so"
swap = {
    "lib/armeabi-v7a/libunity.so": real_unity,
    "lib/armeabi-v7a/libmono.so": real_mono,
}
zin = zipfile.ZipFile(src, "r")
out = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for info in zin.infolist():
    data = zin.read(info.filename)
    if info.filename in swap:
        newp = swap[info.filename]
        data = open(newp, "rb").read()
        print(f"swap {info.filename}: {info.file_size} -> {len(data)}")
    zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
    zi.compress_type = info.compress_type
    zi.external_attr = info.external_attr
    zi.create_system = info.create_system
    out.writestr(zi, data)
out.close(); zin.close()
print("written", dst, os.path.getsize(dst))
