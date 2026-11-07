# 喵星忍者

## 基本信息

| 字段 | 值 |
| --- | --- |
| 原版名 | 喵星忍者（Nyanko Ninja） |
| 包名 | `com.cafgame.nyankoninja` |
| 版本 | 1.08（b37） |
| targetSdk | 9 → 36（minSdk 保持 7） |
| 引擎 | WiEngine（wiyun 引擎，cocos2d 系分支）+ Box2D，纯 native 渲染 |

## 修复项

- **兼容高版本安卓**：`targetSdkVersion` 由 9 提升到 36，`minSdkVersion` 保持 7。
- **解锁内购**：改写 `BillingService`、`CheckoutPayment` 与 `Skeleton` 中的购买校验与发放路径，购买直接走成功回调；支付类已做类加载与运行验证。
- **剪除内置广告**：清空 `Skeleton.onCreate` 中 Tapjoy / Admob / ChartBoost / SponsorPay / Flurry 的初始化，相关展示方法全部改为空实现，并从清单移除对应 Activity / Receiver 与 `READ_PHONE_STATE` 权限，删除布局中的广告视图。运行时日志对这些广告 SDK 的匹配为 0 条。
- **修复闪退**：三个独立根因全部处理。

### 三大闪退根因

| 根因 | 机制 | 处理 |
| --- | --- | --- |
| AAL `dlopen` 失败触发 `exit(1)` | 引擎的 `setupAAL` 在 Android 6+ 找不到系统 AAL 库，打印 "Cannot open android adapter layer" 后走 `exit(1)` | 自研 AAL stub 补齐 24 个导出符号，资源读取改走 Java 层 AssetManager |
| `.so` 压缩存储且未页对齐 | 原 APK 内 `.so` 为 DEFLATED、未按 4KB 对齐；Android 6+ 默认不解压原生库而要求直接 mmap，导致 `dlopen` 失败、启动即闪退 | 清单声明 `extractNativeLibs="true"`，`.so` 改为 STORED，并用 `zipalign -p 4096` 做 4KB 页对齐 |
| Android 8+ 移除 `libstdc++.so` | 多个游戏 `.so` 的 `DT_NEEDED` 声明该库，系统自 API 26 起不再提供，linker 加载即失败 | 将兼容壳打包进 APK 的原生库目录 |

附带保留的兼容性处理：telephony 设备标识改为常量、移除游戏 `.so` 的 `DT_TEXTREL`。

## 下载

| 变体 | Release 资产 |
| --- | --- |
| 兼容修复版 | `喵星忍者_1.08_兼容修复版.apk` |

APK 二进制只走 Releases，不进仓库；资产中文名逐字固定。

## 事实来源

本页技术事实逐条取自以下本地交付 / 接手说明（文件名）：

- `喵星忍者_交付说明.md`
- `NyankoNinja_接手报告.md`