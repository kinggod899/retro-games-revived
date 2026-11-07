# b152 重建报告（去红探针 / 去 WYDIR·WYSKEL 诊断 / 补 uses-library）

生成时间：2026-11-05
工作目录：<WORKSPACE>\nyan_b152（源自 <WORKSPACE>\nyan_b46，<WORKSPACE>\nyan_b46 未修改）
java：openjdk 17.0.16 LTS（Microsoft build 17.0.16+8-LTS）
apktool：<WORKSPACE>\tools\apktool\apktool_2.12.1.jar

## 1. 产物与哈希（sha16 = SHA-256 前 16 位十六进制）

| 产物 | 绝对路径 | 字节数 | sha16 |
| --- | --- | --- | --- |
| classes.dex | <WORKSPACE>\out\_b152_classes.dex | 1297136 | 739680242b6b6f6a |
| AndroidManifest.xml（AXML） | <WORKSPACE>\out\_b152_AndroidManifest.xml | 4916 | 48fbad82114a598b |
| 重建包 | <WORKSPACE>\out\_b152_rebuild.apk | 28374884 | 6e06be8dc7fde1ed |

基线（<WORKSPACE>\nyan_b46\build\apk\ 下同名条目）对照：

| 项 | 基线字节数 | 基线 sha16 | 判定 |
| --- | --- | --- | --- |
| classes.dex | 1297924 | 009f8200bff84ed5 | 新包 1297136 / 739680242b6b6f6a，**不等于基线**（符合预期） |
| AndroidManifest.xml | 4704 | 623e5679602d1af2 | 新包 4916 / 48fbad82114a598b，**不等于基线**（符合预期） |
| resources.arsc | 59496 | d73b7ab12db9b656 | 新包 59496 / **d73b7ab12db9b656，与基线完全一致**（B3 通过） |

重建 apk 条目数 717，classes.dex / AndroidManifest.xml / resources.arsc 三个入口均存在。

## 2. 删除清单（行号均指 <WORKSPACE>\nyan_b46 基线文件的行号）

### <WORKSPACE>\nyan_b46\smali\com\wiyun\engine\nodes\Director.smali（基线 1389 行 → 新 1293 行）

| 基线行号 | 内容 | 说明 |
| --- | --- | --- |
| 1117-1125 | `const-string v0, "WYDIR"` + StringBuilder 链 + `Log.i` + 尾随空行 | onDrawFrame 的 "drawFrame enter" 诊断 |
| 1127-1188 | `# probe: set red clear color BEFORE native draw, no glClear`（1128）+ 4 条 const（1129-1132）+ `invoke-interface {p1, v0, v1, v2, v3}, GL10;->glClearColor(FFFF)V`（1133）+ surf/scene/proj/uiPaused 诊断（1135-1165）+ "drawFrame glErr=" 诊断（1167-1178）+ "drawFrame leave" 诊断（1180-1187）+ 尾随空行 | 红探针 + 3 段 WYDIR 诊断整段删除 |
| 1199-1210 | `const-string v0, "WYDIR"` + "surfaceChanged " 拼接 + `Log.i` | onSurfaceChanged 入参诊断 |
| 1217-1221 | `const-string v0, "WYDIR"` + `const-string v1, "forced 3D projection for viewport"` + `Log.i` + 尾随空行 | onSurfaceChanged 3D 投影诊断 |
| 1223-1226 | `const-string v0, "WYDIR"` + `const-string v1, "forced 2D projection"` + `Log.i` | onSurfaceChanged 2D 投影诊断 |
| 1249-1252 | `const-string v0, "WYDIR"` + `const-string v1, "created: forced 3D projection for viewport"` + `Log.i` | onSurfaceCreated 诊断 |

删除后 onDrawFrame 为 7 行骨架（新 Director.smali:1112-1120）：

```
.method public onDrawFrame(Ljavax/microedition/khronos/opengles/GL10;)V
    .locals 9
    .param p1, "gl"    # Ljavax/microedition/khronos/opengles/GL10;

    .prologue
    invoke-direct {p0}, Lcom/wiyun/engine/nodes/Director;->nativeOnDrawFrame()V

    return-void
.end method
```

.locals 9 未改；`nativeOnDrawFrame()V`、`nativeOnSurfaceChanged(II)V`、`nativeOnSurfaceCreated()V` 与 set3DProjection/set2DProjection 调用全部保留，未动任何 native 签名。

### <WORKSPACE>\nyan_b46\smali\com\wiyun\engine\skeleton\Skeleton.smali（基线 1333 行 → 新 1318 行）

| 基线行号 | 内容 | 说明 |
| --- | --- | --- |
| 928-942 | `const-string v3, "WYSKEL"` + StringBuilder 链（"screen=" + screenWidth + "x" + screenHeight + " scaleMode=" + v6）+ `move-result-object v4` + `invoke-static {v3, v4}, Landroid/util/Log;->i(...)I` | 屏幕尺寸/缩放模式诊断整块，紧跟其后的 `invoke-static {}, Director;->getInstance()` 保留 |

两块改动均以基线字节按行裁剪生成，除删除行外逐字节保持原样（含原有 CRLF 行尾；Skeleton.smali 基线本身在 1070-1130 行有 56 处裸 LF，已原样保留）。

## 3. AndroidManifest.xml 改动

<WORKSPACE>\nyan_b152\AndroidManifest.xml:4 在 `<application ...>` 开标签之后、首个 `<activity>` 之前插入一行：

```
        <uses-library android:name="org.apache.http.legacy" android:required="false"/>
```

未新增 `<uses-sdk>`，apktool.yml 未改动。源文本 AXML 2250 B → 2338 B（+88 B，即 86 B 行内容 + CRLF）。

## 4. 构建命令与返回码

```
cd <WORKSPACE>
java -jar "<WORKSPACE>\tools\apktool\apktool_2.12.1.jar" b "<WORKSPACE>\nyan_b152" -o "<WORKSPACE>\out\_b152_rebuild.apk" -f
```

输出：

```
I: Using Apktool 2.12.1 on nyan_b41_a.apk with 8 threads
I: Smaling smali folder into classes.dex...
I: Building resources with aapt2...
I: Building apk file...
I: Importing lib...
I: Built apk into: <WORKSPACE>\out\_b152_rebuild.apk
RC=0
```

提取两个目标文件（python zipfile 直读重建 apk，不经二次改包）：`classes.dex` → <WORKSPACE>\out\_b152_classes.dex，`AndroidManifest.xml` → <WORKSPACE>\out\_b152_AndroidManifest.xml。

## 5. 校验结果

### B1 · 新 dex 诊断串命中

用 `java -jar apktool_2.12.1.jar d <WORKSPACE>\out\_b152_rebuild.apk -r -f` 反编译新包后统计：

| 检索项 | 结果 |
| --- | --- |
| `WYDIR` 所在 smali 文件数 | 0 |
| `WYSKEL` 所在 smali 文件数 | 0 |
| `WYDIR` 总命中 | 0 |
| Director.smali 内 `glClearColor` 命中 | 0 |
| onDrawFrame 内 `WYDIR` / `glClearColor` 命中 | 0 |
| 全 smali `glClearColor` 命中 | 2 |

那 2 处 `glClearColor` 位于 `smali/com/cafgame/glprobe/ProbeRenderer.smali:42` 与 `:116`，属既有的独立 GlProbeActivity 渲染器，不在本次删除指令范围内，也不在主渲染路径（Director.onDrawFrame）上；基线与新包中该文件完全相同。

### B2 · 新 AXML 的 uses-library

`<WORKSPACE>/Sdk/build-tools/36.0.0/aapt dump xmltree <WORKSPACE>\out\_b152_rebuild.apk AndroidManifest.xml`：

```
      E: uses-library (line=4)
        A: android:name(0x01010003)="org.apache.http.legacy" (Raw: "org.apache.http.legacy")
        A: android:required(0x0101028e)=(type 0x12)0x0
```

`android:required` 为 0x0，即 false。uses-sdk 段仍为 `minSdkVersion=0x7 / targetSdkVersion=0x24`，与基线一致；二进制层面 AXML 中 `uses-sdk` 出现次数基线 1、新包 1（未新增）。

### B3 · resources.arsc

新包 59496 B / `d73b7ab12db9b656`，与基线 `d73b7ab12db9b656` 相同 —— 资源表未被本次改动波及。

### B4 · 产物存在性

<WORKSPACE>\out\_b152_classes.dex（1297136 B）与 <WORKSPACE>\out\_b152_AndroidManifest.xml（4916 B）均已落盘，路径与哈希见第 1 节。

## 6. 过程记录与偏差

- robocopy 首次尝试返回 RC=16，原始错误：`错误: 无效参数 #3:"<DRIVE>/"`（原因是 MSYS2 bash 把 `<WORKSPACE>\...` 反斜杠路径转成了 `<DRIVE>/`，robocopy 因此解析失败；仅产生一次失败调用，未写入任何文件）。改用 `powershell -NoProfile -Command "Copy-Item -Path '<WORKSPACE>\nyan_b46' -Destination '<WORKSPACE>\nyan_b152' -Recurse -Force"` 成功，输出 `COPY_OK`，7 个顶层项（build / lib / original / res / smali / AndroidManifest.xml / apktool.yml）齐全。
- 首轮 smali 编辑用文本替换完成，后续发现新文件被写成纯 LF，与基线 CRLF 不一致；为保证除删除行外逐字节一致，改为**从基线按行号裁剪重建**（保留每行原始行尾），重建结果与首轮内容等价但行尾恢复原状，随后才做最终打包。首轮打包产物已被 `-f` 覆盖，不参与交付。
- <WORKSPACE>\nyan_b46 全程只读；未改动任何 apk、AAL、libwiengine*.so；未执行 adb、未装机、未签名。

## 7. 结论

B1 / B2 / B3 / B4 全部通过。<WORKSPACE>\out\_b152_rebuild.apk 可直接进入签名与装机流程（本任务不执行）。
