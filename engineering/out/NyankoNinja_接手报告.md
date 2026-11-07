# 喵星忍者（Nyanko Ninja）逆向修复 — 团队接手报告

> 版本：v1 · 状态：**进行中，未交付** · 最后更新：2026-10-23
> 本报告面向接手工程师，包含全部已验证事实、文件位置、哈希、踩坑与下一步路线。所有结论均有实测证据支撑，不确定项已明确标注。

---

## 0. 一句话现状

原始 APK 在 MuMu 模拟器（Android 6.0，houdini ARM→x86 翻译）上已能**稳定运行进程（27fps、不崩溃、CPU 从 96% 降到 3.8%）、广告全清**，但**画面仍纯黑**（引擎实际渲染输出为零，glReadPixels 读回的 1280×720 帧缓冲全部像素 = (0,0,0,255)）；**内购解锁未做**；**真机（用户手机）装包直接崩溃**，崩溃原因待 logcat 确认。

---

## 1. 任务目标与完成情况

| # | 目标（用户 m02083 提出） | 状态 |
|---|---|---|
| ① | 适配最新安卓系统 | 🟡 大部分完成：targetSdk 9→36，已可安装/启动/常驻 |
| ② | 去除广告 | ✅ 完成（smali 层 8 个广告入口置空 + 清单残留待清） |
| ③ | 解锁内购 | ❌ 未做（方案已勘察，见 §8.2） |
| ④ | 画面正常渲染 | ❌ **当前最大阻塞**：帧缓冲全零，见 §6 |

验收标准（自定）：真机 Android 12+ 上能进主菜单并实际游玩、无广告、内购项可直接获得。

---

## 2. 原始包档案

- 路径：`<WORKSPACE>\com.cafgame.nyankoninja.apk`
- 大小 20,090,446 B，SHA-256 `96313F2FFFC83A9088E10EEFA66ECA2FC196056A288B14B1A344114E8131502A`
- 包名 `com.cafgame.nyankoninja`，versionCode 10 / versionName 1.08，**minSdk 7 / targetSdk 9**
- 引擎：**WiEngine（wiyun 引擎，cocos2d 系分支）+ Box2D**，纯 native C++ 渲染（GLES 1.1）
- ABI 仅 `armeabi`（ARMv5 时代，无 v7a 后缀目录）
- **资源全在 `res/raw/`**（372 个 .tmx 地图 / 145 .png / 62 .mp3 / 60 .sprite / 24 .plist），`assets/` 为空
- 原始 11 个 .so 全部带 **DT_TEXTREL**（Android 6+ 拒绝加载的直接原因之一）
- 广告 SDK：Tapjoy、Chartboost、AdMob(google.ads)、SponsorPay、Flurry、自研 feelingtouch bannerad/GameADLoader
- 支付：`com.feelingtouch.payment.*`（仿 Google Play Billing v1/v2 架构：BillingService/BillingReceiver/CheckoutPayment/Security）

---

## 3. 目录地图（工作区）

| 路径 | 内容 |
|---|---|
| `<WORKSPACE>\nyan\` | **当前工作解码树**（apktool 2.12.1），targetSdk 已改 36，⚠️含探针残留（见 §5） |
| `<WORKSPACE>\nyan_orig_man\` | 原始包 apktool 解码（未动），`classes.dex` 1,302,056 B — **还原 smali 的唯一干净来源** |
| `<WORKSPACE>\nyan_orig\` | 原始 lib/ 解出的 11 个 .so |
| `<WORKSPACE>\fixed\` | 修过的 so 变体：`libwiengine.so`（哈希 5D0F…19DD）与 `libwiengine_aalsofth.so`（4B3C…C7，**当前树里用的就是它**，与 nyan\lib\armeabi\libwiengine.so 同哈希） |
| `<WORKSPACE>\aalstub3\libaal.so` | 自写 stub 最终版 15,504 B（SHA-256 `69FC9E5C…94ED3435`），源码 `<WORKSPACE>\aal_real.c`（12,536 B，SHA-256 `3E45ED…6F84141`） |
| `<WORKSPACE>\nyan_b22_s.apk` | **最新构建** 20,586,392 B，SHA-256 `2629076394A1F25C093D9F2D480D77023C19A126791A9BFFDE94EC7A94DAB50E`（⚠️ 含 fb200 探针，不是交付候选） |
| `<WORKSPACE>\apktool.jar` | apktool 2.12.1（构建日志 `b22log.txt` 证实版本） |
| `<WORKSPACE>\<KEYSTORE_FILE>` | 签名密钥（alias <REDACTED> / pass <REDACTED>） |
| `<WORKSPACE>\gltest\` | 独立 GL 探针工程（main.c / main8888.c / libgltest.so / gltest.apk），验证模拟器 EGL 正常 |
| `<WORKSPACE>\nyan_patch_*.py` | 26 个补丁/探针脚本，全部保留，见 §7 |
| `<WORKSPACE>\out\` | 上一个任务（小小部队）的交付目录，**Nyanko 尚未有任何产物进入** |

工具链：JDK21 `<WORKSPACE>\rea-tools\jdk-21.0.12.1+1`；build-tools `<WORKSPACE>\Sdk\build-tools\36.0.0`（zipalign/apksigner）；adb `<WORKSPACE>\Sdk\platform-tools\adb.exe`；NDK 27（llvm-strings/objdump）；Python 3.13（PIL、pyelftools 已装）。

---

## 4. 已完成的修改（全部实测生效）

### 4.1 清单（<WORKSPACE>\nyan\AndroidManifest.xml）
- `apktool.yml`：`minSdkVersion: 7`、`targetSdkVersion: 36`（uses-sdk 由 apktool 注入，清单内无此标签）
- **入口 Activity 已从壳改为** `com.wiyun.engine.skeleton.Skeleton`（MAIN+LAUNCHER，exported=true，landscape，singleTop，Theme.NoTitleBar.Fullscreen）
- `BannerAdActivity` 改为 exported=false 并摘除 intent-filter
- aapt2 验证 b22：targetSdkVersion=36、launchable-activity = Skeleton ✅

### 4.2 原生库修复（17 个 .so 全部就位）
对原始 11 个 .so 做三件事（脚本 `nyan_fixall.py` / `nyan_fixlib.py` / `nyan_var.py`）：
1. **清 exec 重定位**：DT_REL(17) 表中 r_offset 落在可执行段（PF_X 的 PT_LOAD）内的条目 r_info 置 0（变成 R_ARM_NONE）
2. **删 DT_TEXTREL(22)** 动态表项，DT_NULL 填充
3. 结果验证（本报告重新实测）：11 个游戏 so textrel=0；每库残留 excess_relocs=2（无害，为已知良性条目）

**自带 6 个非 public 系统库**（Android 7+ 命名空间限制，app 无法链接私有系统库）：`libcutils.so`(3,836)、`libutils.so`(3,584)、`libsqlite.so`(1,208,672)、`libandroidicu.so`(16,932)、`libbase.so`(239,828)、`libc++.so`(637,072)。依据 `<WORKSPACE>\public_libs.txt`（NDK PlatformApis 公开库清单）对比 DT_NEEDED 得出。

**libaal 三件套替换为自写 stub**：原始 libaal.so / libaal_honeycomb.so / libaal_jellybean.so（各 107,632 B）是引擎对 Android AssetManager 的私有 API 封装，在新系统上缺符号无法加载。自写 stub（源码 `aal_real.c`）导出全部 24 个符号：setEnv/setContext/setDensity/setScaleMode/deinit、getAsset/getAssetByResId/getAssetBuffer/getAssetLength/getAssetRemainingLength/readAsset/seekAsset/closeAsset/getAssetFD/getResFD、scaleImage/scalePVR（**passthrough：直接返回输入 data 指针**）、calculateTextSizeWithFont/WithCustomFont、createLabelBitmapWithFont/WithCustomFont（返回 NULL）、utf16toutf8/wctoutf8/toUTF16。资源读取路径改为 Java 层 AssetManager.open + 反射 `android/app/ActivityThread.currentActivityThread().getApplication()` 拿 Context（**不依赖引擎传参**）。带 `AALTRACE` 日志 tag。三个文件名放的是同一份 stub（15,504 B，哈希相同）。

**libwiengine.so exit 补丁**：`nyan_patch_exit.py` 把 6 处 exit(1) 调用点（0xbc03a / 0xbc080 / 0xbc192 / 0xbc1e2 / 0xbc20a / 0xbc074）改写为 Thumb `b 0xbbfc2`（跳过退出路径），产物即 aalsofth 变体。

### 4.3 smali 层修改（已生效）
- `nyan_patch_ads_tel.py`：
  - **telephony 常量替换**（修 SecurityException 崩溃）：Skeleton.smali ×2、nodes\f.smali ×3、nodes\_A.smali ×1、Director.smali ×1 的 `TelephonyManager.getDeviceId()` → `"000000000000000"`，`getLine1Number()` → `""`
  - Skeleton.onCreate 删除三段广告初始化：Tapjoy（requestTapjoyConnect + getTapPoints）、BannerAd.batchInit/initSlideAd、Chartboost
  - BannerAd$2.run() 置空（.locals 0 + return-void）
- `nyan_patch_ads2.py`：Skeleton 8 个方法改空实现 —— showAd(I)V / hideAd()V / showExit()V / showOfferWall(I)V / showChartBoost()V / initAdmobAd()V / initChartBoost()V / initSponsorPay()V；`onBackPressed()` 改为纯 super 调用（原为退出广告）；onStart/onStop 内 Chartboost 块删除
- 效果实测：**广告 SDK 不再初始化，进程 CPU 96% → 3.8%，进程稳定 27fps 常驻**

### 4.4 构建链（已跑通 22 轮）
```
java -jar <WORKSPACE>\apktool.jar b -f -o <WORKSPACE>\nyan_bN.apk <WORKSPACE>\nyan
zipalign -f -p 4 nyan_bN.apk nyan_bN_a.apk
apksigner sign --ks <WORKSPACE>\<KEYSTORE_FILE> --ks-pass pass:<REDACTED> --key-pass pass:<REDACTED> --ks-key-alias <REDACTED> --out nyan_bN_s.apk nyan_bN_a.apk
```
构建日志样例 `<WORKSPACE>\b22log.txt`。历史包 nyan_b1_s…b22_s.apk（b13 缺号）全在 <WORKSPACE> 根，b4 起 20,586,392 B（b1–b3 为 20,701,080 B，差异来自库替换）。

---

## 5. ⚠️ 重要：当前解码树不干净

`<WORKSPACE>\nyan\smali\com\wiyun\engine\nodes\Director.smali` 的 `onDrawFrame` 目前是 **b22 探针版**（第 1115 行起，含 `.field static dcount:I`、`glReadPixels`、写 `fb200.raw` 到 getExternalFilesDir）。**出交付包前必须先还原此方法**。

还原方式（目录里没有任何备份，已核实）：用 apktool 重新解包原始 APK 或对 `<WORKSPACE>\nyan_orig_man\classes.dex` 反编译，取出干净 `Director.smali`，再**重放** §4.3 的 telephony 常量替换（Director.smali 里有 1 处）——其余补丁不涉及该文件。

残留清单（grep `DFBO_|DVP_|DFRAME|DPX_|DSCENE|fb200|fb300| DERR `）：仅 Director.smali 1 处真探针；FixtureAnimation.smali 4 处为 DERR 子串误命中。

清单残留（去广告收尾未做）：manifest 仍含 3 个 tapjoy Activity、`com.google.ads.AdActivity`、`com.sponsorpay...OfferWallActivity`。4 处孤立 `TelephonyManager.getDeviceId()` 调用未改（AndroidUtil.smali:156、FlurryAgent.smali:5154、HostInfo.smali:116、TapjoyConnectCore.smali:3077）——广告初始化已删，实际走不到，风险低。Flurry 仍存活（Skeleton.smali:1455 onStartSession，key `3WRPD88JWVTK4Q57WMPY`）。

---

## 6. 当前阻塞：画面纯黑（核心问题）

### 6.1 实测证据链
- 进程稳定存活 27fps，无 crash（logcat crash buffer 空），声音/log 正常 → Java 层、资源加载、引擎主循环都活着
- b18/b19 探针（onDrawFrame 里 glClearColor 纯红 + glClear）：**屏幕确实变纯红**（b19.png = 921,600 像素全 (255,0,0)）→ EGL 上下文、swap chain、GL 调用本身**完全正常**
- b22 探针（nativeOnDrawFrame 之后整屏 glReadPixels 1280×720 RGBA 落盘 fb200.raw）：**921,600 像素全部 = (0,0,0,255)** → **引擎 native 渲染产出为零**。不是上屏问题，是引擎根本没画
- 独立探针 app `gltest.apk` 在同一模拟器上 EGL/GLES 正常出图 → 排除模拟器 GL 环境整体损坏
- MuMu 截图陷阱：d11.png 曾被误判为"引擎有输出"，实为 MuMu 自己的"屏幕截图"预览面板 UI（有按钮文字可辨）。**用 screencap 判断前先看有没有 MuMu UI 元素**

### 6.2 三个假设（未决）
1. **MuMu houdini 翻译层问题**：引擎 armeabi(ARMv5) 代码经 houdini 翻译执行，某些路径（如 GLES 1.1 固定管线状态）翻译后静默失效。真机原生 ARM 可能直接正常 —— **这是概率最高的假设，也是为什么必须上真机验证**
2. **引擎初始化静默失败**：某个 native 初始化步骤（场景图/纹理/投影矩阵）在新系统返回错误但被吞掉（引擎有大量 exit(1) 路径，已 patch 的 6 处只是其中一部分）
3. **libaal stub 行为差异**：scaleImage/createLabelBitmap 返回 passthrough/NULL，若引擎依赖缩放后的真实位图或文字位图，画面元素可能因此为空（但背景色/纯色 quad 也应该画出来，故此假设解释力较弱）

### 6.3 下一步排查动作（按优先级）
1. **真机装 b22（或还原探针后的干净包）**——用户已反馈"真机直接崩"（m04817），**先抓真机 crash logcat**（附录 B 有指引），这同时回答"真机是否也走黑屏路径"和"崩溃原因"两个问题
2. 若真机也黑：在 libaal stub 的 AALTRACE 日志里核对资源是否全部被正确读取（len 是否合理）
3. 给 nativeOnDrawFrame 前后加 glGetError 轮询（DFBO/DERR 探针脚本已备好：nyan_patch_fbo.py / fbo2.py / state*.py）
4. 用 `<WORKSPACE>\wi_dis.txt`（libwiengine 反汇编 14.6MB）查渲染入口是否早退

---

## 7. 补丁/探针脚本索引（<WORKSPACE> 根）

| 脚本 | 用途 |
|---|---|
| `nyan_fixall.py` + `nyan_var.py` | so 修复主流程：清 exec 重定位 + 删 DT_TEXTREL |
| `nyan_patch_needed.py` | 从 ELF .dynamic 删除指定 DT_NEEDED 条目 |
| `nyan_needed.py` | 审计所有 so 的非 public 依赖（对照 public_libs.txt） |
| `nyan_patch_exit.py` | libwiengine 6 处 exit(1) → 跳转 |
| `nyan_patch_ads_tel.py` / `nyan_patch_ads2.py` | 广告/telephony 修复（§4.3，**交付包必需**） |
| `nyan_patch_red.py` / red2 / red3 | 探针：onDrawFrame 强制 glClear 纯红（验证 GL 链路） |
| `nyan_patch_fbdump.py` | 探针：第 200 帧整屏 glReadPixels → fb200.raw（b22 当前状态） |
| `nyan_patch_state3.py` | 探针：DSCENE 场景 id + fb300.raw（未跑成） |
| `nyan_patch_frames.py` / `nyan_patch_vp*.py` / `nyan_patch_fbo*.py` / `nyan_patch_diag*.py` / `nyan_patch_shot*.py` | 帧计数/视口/FBO/诊断/截图探针 |
| `an.py` / an2 / an3 / an_fb / an_rgba / raw2png | 像素统计与 raw→png 转换 |
| `nyan_ld.log` / nyan_l2 / nyan_l3 / nyan_t*_ld.txt | 早期 linker 日志：全是 undefined symbol glBindFramebufferOES / glNamedFramebufferSampleLocationsfvNV(OES) 时代遗物（已通过自带库+stub 解决） |

---

## 8. 待办清单

### 8.1 适配收尾（约半天）
- [ ] 还原 Director.onDrawFrame（§5）
- [ ] 删清单内 tapjoy ×3 / AdActivity / OfferWallActivity 残留
- [ ] （可选）移除 Flurry：Skeleton.smali onStartSession/onEndSession + FLURRY_API_KEY
- [ ] （可选）清 4 处孤立 getDeviceId 调用
- [ ] 出干净包 → MuMu 回归（进程稳定 + 无广告 + 无 crash）

### 8.2 内购解锁（估 1–2 小时，纯 smali 层）
目标文件：`<WORKSPACE>\nyan\smali\com\feelingtouch\payment\`（BillingService 25KB、CheckoutPayment 16KB、Security 21KB、PurchaseObserver、ResponseHandler、Consts 等）。
建议路线（最省事）：**跳过签名验证**——`Security.verifyPurchase` / `Security$VerifiedPurchase` 改为直接返回已验证；或让 `BillingService$CheckBillingSupported` 恒返回 supported、`CheckoutPayment.purchaseSuccess()` 直接触发成功回调。动手前先反编译读一遍 `CheckoutPayment.smali` 的 `purchaseSuccess()` 与 `InappPurchaseObserver` 确认回调链。
注意：manifest 里 BillingService / BillingReceiver（3 个 com.android.vending.billing action）**保留**，否则购买流程起不来。

### 8.3 黑屏（§6，优先级最高）

### 8.4 真机验证 + 交付
- 真机 Android 12+ 安装、进主菜单、玩一关、商店购买一项
- 产物放入 `<WORKSPACE>\out\`，附哈希与说明（参照同目录小小部队交付说明.md 的格式）

---

## 9. 环境与操作注意

1. **MuMu 端口漂移**：用户硬约束（m02100）"调试只准用端口号 5557/16416 的 MuMu"，但 MuMu 重启后实际端口变成了 **16384**（当前 adb devices 只挂 <DEVICE_ID>）。接手时先 `adb devices -l` 实测，必要时改脚本里的 $dev
2. **run.ps1 里写死的包名是小小部队的**（com.chillingo…），那是上一任务的脚本；Nyanko 包名 `com.cafgame.nyankoninja`，勿混用
3. 截图判断必须排除 MuMu overlay（§6.1 教训）
4. apktool 构建的 `doNotCompress: arsc,jpg,mp3,png` 已在 apktool.yml 里配好，不要动
5. 设备 shell 探针脚本（comp.sh / lat.sh / probe*.sh / sample.sh / thr.sh）推送到设备 /data/local/tmp 执行；宿主侧截 MuMu 画面的 cap_*.ps1 全部失败，别再用
6. <WORKSPACE> 已占 10.75 GB，其中大量是历史诊断产物（lu_dis.txt 65MB、wi_dis.txt 14.6MB、t*/v*/p* 等旧解码树），清理前先确认

---

## 10. 给接手人的三个关键判断

1. **不要从 smali 重打补丁开始**——先还原 Director.smali，再决定其他；当前树只有这一个文件脏
2. **黑屏大概率不是 GL 链路问题**——纯红 clear 能上屏证明链路通；问题在"引擎决定画什么"的那一层（场景图/资源/初始化返回值）
3. **真机崩溃与 MuMu 黑屏可能是两个独立问题**——真机是原生 ARM 不需要 houdini，崩溃更可能是 targetSdk 36 引入的运行时行为（权限/SELinux/存储），拿到 logcat 前不要合并假设

---

## 附录 A · 关键哈希速查

| 文件 | SHA-256 |
|---|---|
| 原始 APK | 96313F2FFFC83A9088E10EEFA66ECA2FC196056A288B14B1A344114E8131502A |
| nyan_b22_s.apk（最新，含探针） | 2629076394A1F25C093D9F2D480D77023C19A126791A9BFFDE94EC7A94DAB50E |
| stub libaal.so（×3 同名同哈希） | 69FC9E5C1FBB86E9327A1838408F9C164EC622A087F1551D7BF8A35494ED3435 |
| aal_real.c | 3E45EDC3B5FC1F07131CDAD9ED0ED7376118E6FC458FBBF29A442D63D6F84141 |
| libwiengine.so（aalsofth 变体，树内在用） | 4B3C1CB945EB94B05AA72181159A48AE4D010E038EF82E9AB44A0FBA282B7AC7 |
| libwiengine.so（fixed 目录另一变体） | 5D0F1F54469311481A1B68E5F7B2B66F274022B0A5C1A006DD0B5E93484619DD |
| nyan_fixall.py | 4244DCB60C0A8464BF52B289A27B2746033F00BE2280EE7E292FB59DC150A76A |

## 附录 B · 真机 logcat 抓取指引（给用户/测试）

1. 手机开 USB 调试，连电脑
2. `adb logcat -c` 清空
3. 安装并启动 APK：`adb install <WORKSPACE>\nyan_b22_s.apk` → 点图标
4. 崩溃后立即执行：`adb logcat -d -b crash -b main > nyan_crash.txt`
5. 把 nyan_crash.txt 发回来，重点看 FATAL EXCEPTION / DEBUG / linker 三段
