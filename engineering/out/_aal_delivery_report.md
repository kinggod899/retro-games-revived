# b152 AAL 精简交付版 构建报告

基线：<WORKSPACE>\out\_aal_br2_b150.c.bak（910 行 / 40081 字节）。
变换：纯行删除 + 两处实质修正（closeAsset 真释放、剥离残余日志语句），其余保留行与基线逐行一致 = True。

## 产物

| 绝对路径 | 字节数 | sha16 (SHA-256 前 16 位) |
| --- | --- | --- |
| <WORKSPACE>\aal_delivery.c | 13903 | 5bb8f3c2bba7f042 |
| <WORKSPACE>\aal_delivery.so | 13808 | 8bee52a2929acbfc |
| <WORKSPACE>\out\_build_aal_delivery.py | 9132 | 168f9a2603a00666 |
| <WORKSPACE>\out\_aal_delivery_report.md | 4578 | 自引用 sha16 在交付摘要中实测报送 |

## 编译

规定命令：

```
<WORKSPACE>\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin\armv7a-linux-androideabi21-clang.cmd -fPIC -shared -O2 -llog -ljnigraphics <WORKSPACE>\aal_delivery.c -o <WORKSPACE>\aal_delivery.so
```

实际调用（等价，路径加引号由 cmd.exe 解析）：

```
"<WORKSPACE>\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin\armv7a-linux-androideabi21-clang.cmd" -fPIC -shared -O2 -llog -ljnigraphics "<WORKSPACE>\aal_delivery.c" -o "<WORKSPACE>\aal_delivery.so"
```

RC = 0
stdout：(empty)
stderr：(empty)

## A1 源码与 grep

源码行数 = 331（<= 400）。

| pattern | 命中数 |
| --- | --- |
| g_slots | 0 |
| g_extra | 0 |
| patch_got | 0 |
| br_gl | 0 |
| diag_ | 0 |
| fetch_gl | 0 |
| FIX | 0 |
| DIAG | 0 |
| SI  | 0 |
| B150 scale | 0 |
| AALTRACE | 0 |
| 合计 | 0 |

LOGI 残留 = 0；无 #define TAG / #define LOGI。

## A2 交付 so

存在 = True，字节数 = 13808（要求 < 31524），sha16 = 8bee52a2929acbfc。

## A3 .dynsym 实测

llvm-nm.exe -D --defined-only RC=0；llvm-readelf.exe --dyn-syms RC=0。
nm 定义符号数 = 24；readelf dynsym 行数 = 36。
24 个必需名字命中 = 24/24；缺失 = []；br_gl*/diag_* 导出 = []。
readelf 交叉验证 = 24/24。

实测导出清单（nm -D --defined-only，排序）：

```
calculateTextSizeWithCustomFont
calculateTextSizeWithFont
closeAsset
createLabelBitmapWithCustomFont
createLabelBitmapWithFont
deinit
getAsset
getAssetBuffer
getAssetByResId
getAssetFD
getAssetLength
getAssetRemainingLength
getResFD
readAsset
scaleImage
scalePVR
seekAsset
setContext
setDensity
setEnv
setScaleMode
toUTF16
utf16toutf8
wctoutf8
```

24 个必需名字逐项：setEnv, setContext, setDensity, setScaleMode, deinit, scaleImage, scalePVR, calculateTextSizeWithFont, calculateTextSizeWithCustomFont, createLabelBitmapWithFont, createLabelBitmapWithCustomFont, getAssetByResId, getAsset, getAssetBuffer, getAssetLength, getAssetRemainingLength, readAsset, seekAsset, closeAsset, getResFD, getAssetFD, utf16toutf8, wctoutf8, toUTF16

## A4 关键代码与函数区间

| 断言 | 命中数 |
| --- | --- |
| if (pScale) *pScale = 1.0f; | 1 |
| return (int)(intptr_t)a; | 1 |
| free(a->data); free(a); | 1 |

| 函数 | 入口行 | 结尾行 |
| --- | --- | --- |
| scaleImage | 143 | 201 |
| getAssetByResId | 209 | 222 |
| closeAsset | 270 | 272 |

## 运行时日志

源码零 LOGI 调用、零 __android_log_print 引用；-llog 仅按指定编译参数保留。交付 so 运行时不输出任何诊断日志。

## 错误原文

(none)

## 边界

仅本地静态校验，未装真机；未触碰 b151 基线、任何 apk / smali / AndroidManifest.xml / libwiengine*.so / build_aal.py。

## 独立复核（不依赖构建脚本自报）

- llvm-nm.exe -D --defined-only 直接实测：24 个 T 符号全部命中，0 个 br_gl*/diag_* 导出。
- llvm-readelf.exe --dyn-syms 独立交叉验证：24/24；dynsym GLOBAL FUNC 行数 35。
- 交付 so 内诊断字符串 grep -a：AALTRACE / B150 / SI / patch / VP / TI / FIX / DIAG / FIX148 / DIAG140 / b150 全部 0 命中。
- llvm-nm.exe -D 未定义符号仅 AndroidBitmap_* 与 libc（calloc/free/malloc/memcpy/realloc/strlen/__cxa_*），无 __android_log_print，无 liblog 依赖。
- 源码独立 grep（含注释）：g_slots/g_extra/g_patched/patch_got/br_gl/diag_/fetch_gl/FIX/DIAG/SI /B150/AALTRACE/LOGI/density/VP /TI /patch 等全部 0 命中。
- 禁改文件 mtime 未变：aal_br2.c 1793808309、aal_br2.so 1793808591、_aal_br2_b150.c.bak 1793808309、build_aal.py 1793482334。
- scaleImage 完整链路：decodeByteArray → AndroidBitmap_getInfo → AndroidBitmap_lockPixels → 同尺寸格式 memcpy / 最近邻 box resample（RGBA8888 拷 4B，其他按 RGB565 拆 5/6/5 位转 8888 且 a=255）→ AndroidBitmap_unlockPixels → 永远 return out。
- 5 个 stub 均 return NULL；getAssetByResId 未引入 density 变量。
