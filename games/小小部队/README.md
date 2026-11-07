# 小小部队

## 基本信息

| 字段 | 值 |
| --- | --- |
| 原版名 | 小小部队（Tiny Troopers） |
| 包名 | `com.chillingo.tinytroopersfree.android.aja` |
| 版本 | 1.0.6（versionCode 106） |
| targetSdk | 33 / 35 / 36 三个变体；**api36 = targetSdk 36（Android 16），推荐先装** |
| minSdk | 8 |

各 `targetSdk` 变体除清单与签名条目外逐字节相同；装不上或异常再依次试 api35 / api33。同一包名下两个版本不能同时安装。

## 两个版本差异

| 项目 | Clean · 原版复活 | Unlocked · 无限资源版 |
| --- | --- | --- |
| 启动修复 / 去广告 / 内购免费 | 有 | 有 |
| 命令点数（CP） | 原版逻辑，靠打关卡攒 | `GetCommandPoints()` 恒返回 999999，`ReduceCommandPoints` 空实现 |
| 狗牌（DogTags） | 原版逻辑 | `GetDogTags()` 恒返回 9999，`ReduceDogTags` 空实现 |
| 关卡进度 | 原版，从第 1 关打起 | `levelProgress = 30`，三章 30 关全开 |
| 教程 | 原版，先打教学任务 | 自动置 `isTutorialAccomplished = true`，战役 / 任务开局即可点 |
| 专家解锁门槛 | 原版门槛 | `isSpecialistUnlockLevelPassed` 恒 true |
| 每关星级 | 原版 | 补到 2 星（不补 3 星，3 星会让敌人寻路加速） |
| 教学提示弹窗 | 原版 | 6 个提示全置 true，不再打断 |

「内购免费」两版都保留：原包所依赖的 Google Play Billing v2 已停服，原版内购链路本就是死的；补丁让点「购买」直接走游戏自己的成功回调，不弹支付界面、不发网络请求。

Clean 版刻意保持经济、教程、关卡进度原样，适合想自己从零打的玩家；Unlocked 版适合直接爽玩。**换版本前清一次数据**，否则 Unlocked 的存档会被 Clean 照读。

## 启动修复要点

- 用 `assets/libs/` 内的真实 `libunity.so` / `libmono.so` 直接替换 `lib/` 下的壳加载器，绕过模拟器 ARM 转译层整数除零崩溃。
- 消除 `libunity.so` 的 `DT_TEXTREL`：把落在可执行段的重定位改写成 PC 相对指令，段权限保持原样 R-X（不采用真机会拒绝的 RWX 段）。
- `targetSdk` 提到 23 以上，消除 Android 6+ 每次启动弹出的权限复核页。
- 清单移除广告 / 渠道壳组件，入口改为 `UnityPlayerActivity`。

## 下载

| 变体 | Release 资产 |
| --- | --- |
| 原版复活（Clean，原版经济） | `小小部队_1.0.6_原版复活.apk` |
| 无限资源版（Unlocked） | `小小部队_1.0.6_无限资源版.apk` |

APK 二进制只走 Releases，不进仓库；资产中文名逐字固定。

## 事实来源

本页技术事实逐条取自以下本地交付说明（文件名）：

- `交付说明.md`