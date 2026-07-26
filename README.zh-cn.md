> **[📖 English](README.md)**
> **[📖 简体中文(大陆)](README.zh-cn.md)**

![WireSight](https://socialify.git.ci/VincentZyuApps/WireSight/image?custom_language=Shell&description=1&font=JetBrains+Mono&forks=1&issues=1&language=1&logo=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2F6%2F6a%2FGLSL_Logo_%2528Unofficial%2529.svg%2F960px-GLSL_Logo_%2528Unofficial%2529.svg.png%3F_%3D20250822083621&name=1&owner=1&pulls=1&stargazers=1&theme=Auto)

# 🟢 WireSight

🧱 WireSight 是一款实验性、低开销的 Minecraft Java 版光影包，它将整个世界渲染成类似实体建模视图的效果：方块表面呈深绿色，方块边线则呈明亮的绿色。

⚙️ 本光影包面向 Iris、Oculus 与 OptiFine 共同支持的 OptiFine 光影包格式。其核心路径使用 GLSL 1.20、单次地形渲染、常规深度写入，并且不包含阴影或全屏后处理。

[![Modrinth](https://img.shields.io/badge/Modrinth-1BD96A?style=for-the-badge&logo=modrinth&logoColor=white)](https://modrinth.com/shader/wiresight)
[![CurseForge](https://img.shields.io/badge/CurseForge-F16436?style=for-the-badge&logo=curseforge&logoColor=white)](https://www.curseforge.com/minecraft/shaders/wiresight)

[![QQ群](https://img.shields.io/badge/QQ群-1085190201-12B7F5?style=flat-square&logo=qq&logoColor=white)](https://qm.qq.com/q/4vjto4V7Di)

<p><del>💬 光影包使用问题 / 🐛 Bug 反馈 / 👨‍💻 光影开发交流，欢迎加入 QQ 群：<b>259248174</b> 🎉（这个群已失效）</del></p>
<p>💬 光影包使用问题 / 🐛 Bug 反馈 / 👨‍💻 光影开发交流，欢迎加入 QQ 群：<b>1085190201</b> 🎉</p>
<p>💡 在群里直接艾特我，回复会更快哦 ~ ✨</p>

---

## 🖼️ 预览

![WireSight 将 Minecraft 世界渲染为绿色线框几何体](docs/images/preview/preview.png)

## 🎨 默认主题色

🎯 WireSight 默认使用以下基础颜色（RGB 与十六进制值表示同一种颜色）：

| 🎯 渲染目标 | RGB | 十六进制 | 外观 |
|---|---|---|---|
| 🧱 普通方块面 | `RGB(6, 17, 11)` | `#06110B` | 深绿色 |
| 🌊 水与半透明地形 | `RGB(5, 21, 19)` | `#051513` | 深青绿色 |
| ✨ 方块边线 | `RGB(53, 255, 120)` | `#35FF78` | 荧光绿 |
| 👤 实体、手持物、粒子和天气 | `RGB(14, 61, 34)` | `#0E3D22` | 纯色绿 |
| 🌌 天空、太阳、月亮和云 | `RGB(0, 0, 0)` | `#000000` | 纯黑 |

💡 这些数值是基础颜色；方向面色阶会进一步调暗地形与实体的侧面和底面。

## 🎛️ 光影设置

⚙️ WireSight 使用 Iris、Oculus 与 OptiFine 共同支持的 OptiFine ShaderPack 通用选项格式。不同加载器的界面皮肤可能不同，但控件及排列顺序保持一致。

### 🧭 主设置页

```text
+--------------------------------+--------------------------------+
| 主题预设：WireSight 绿         | 自定义主题色...                 |
| 方向面色阶：开启               | 边线宽度：1.5                   |
| 边线淡出起点：96 格            | 边线淡出长度：64 格             |
+--------------------------------+--------------------------------+
```

- 🌓 `方向面色阶`为顶面、侧面和底面使用固定亮度；它不是动态光照。
- 📏 `边线宽度`控制方块边线近似占用的屏幕像素宽度。
- 🌫️ `边线淡出起点`是边线开始变淡时与玩家的距离。
- 📐 `边线淡出长度`是完成淡出所用的距离，因此默认终点为 `96 + 64 = 160` 格。

### 🌈 自定义主题色

```text
+----------------------+----------------------+----------------------+
| 主题预设：自定义                                                    |
+----------------------+----------------------+----------------------+
| 方块面 R：6          | 方块面 G：17         | 方块面 B：11         |
| 水体 R：5            | 水体 G：21           | 水体 B：19           |
| 方块边线 R：53       | 方块边线 G：255      | 方块边线 B：120      |
| 实体 R：14           | 实体 G：61           | 实体 B：34           |
| 天空与天体 R：0      | 天空与天体 G：0      | 天空与天体 B：0      |
+----------------------+----------------------+----------------------+
```

> **⚠️ 注意：** 只有将 `主题预设` 设置为 `自定义` 时，自定义 RGB 数值才会生效。

🔢 每个通道都具有从 `0` 到 `255` 的完整整数精度。选择其他预设时会保留自定义数值，重新切回 `自定义` 后仍会恢复原值。

### 🧩 内置预设

| 🎨 表面 | WireSight 绿 | 青色 | 琥珀色 | 黑白 |
|---|---|---|---|---|
| 🧱 方块面 | `#06110B` | `#061116` | `#171006` | `#111111` |
| 🌊 水体 | `#051513` | `#051522` | `#071417` | `#151515` |
| ✨ 方块边线 | `#35FF78` | `#35E7FF` | `#FFC247` | `#F2F2F2` |
| 👤 实体 | `#0E3D22` | `#0E3540` | `#5E3D10` | `#3D3D3D` |
| 🌌 天空与天体 | `#000000` | `#000000` | `#000000` | `#000000` |

🟠 琥珀色预设有意保留冷暗水体，使其与暖色地形明显区分。修改选项时，加载器可能短暂地重新编译光影。

## 🔍 当前范围

- 🧱 在地形和方块实体上显示可见的 1x1 方块边界
- 🌓 使用三档纯色面明暗增强空间辨识度
- ✨ 使用像素宽度稳定且带抗锯齿的主题色边线
- 🌫️ 自动过滤远距离网格以减少闪烁
- 🍃 为树叶和植物等镂空几何体保留透明度
- 👤 使用纯色渲染实体、粒子、天气效果和手持物品
- 🏷️ 为名称标签和世界空间文字保留原始颜色与透明度
- 🌊 使用不透明的风格化水体与可配置天空

⚠️ WireSight 只能勾勒可见的几何体。它不是透视光影，也不会渲染 Minecraft 已从区块网格中剔除的表面。

## 🧪 兼容性目标

> 🧪 本光影有意避免使用计算着色器、几何着色器以及加载器专属扩展。
>
> | 🔌 环境 | Minecraft | 光影加载器 | 配套组件 |
> |---|:---:|---|---|
> | 🥽 Oculus | `1.20.1` | `Oculus 1.8.0` | `Embeddium 0.3.31` |
> | 🌈 Iris | `1.21.8` | `Iris 1.9.1` | `Sodium 0.6.31` |
> | 🔭 OptiFine | `1.8.9` | `OptiFine HD U M5` | `Forge 11.15.1.2318` |

📚 OptiFine 构建面向 Minecraft 1.8 至 1.21.x 的全部正式版本；未列出的组合基于兼容接口提供支持，尚未逐版本实测。

## 📦 安装

📥 将发布的 zip 文件放入 Minecraft 实例的 `shaderpacks` 目录，然后在光影包菜单中选择 WireSight。

## 💻 VS Code

🧩 安装 [Shader languages support for VS Code](https://marketplace.visualstudio.com/items?itemName=slevesque.shader) 以获得 GLSL 语法高亮。已跟踪的 `.vscode/settings.json` 会将 `.glsl`、`.fsh` 和 `.vsh` 文件关联到 GLSL，`.vscode/extensions.json` 则会自动推荐该扩展。

```bash
code --install-extension slevesque.shader
```

## 🚀 构建、Release 与平台发布

🐍 使用 [uv](https://docs.astral.sh/uv/) 与 Python 3.13 在本地构建：

```bash
uv venv
uv run python ./scripts/build_shaderpack.py
uv run python ./scripts/validate_publish.py
```

📦 两个可复现 ZIP 及其对应的 SHA-256 文件会写入 `dist/`。`metadata.toml` 是 WireSight 版本、变体支持范围、平台项目 ID 与加载器的唯一配置来源。

| 📦 变体 | 构建文件 | Modrinth loader | Minecraft 范围 |
|---|---|:---:|---|
| 🌈 Iris / Oculus | `WireSight-X.Y.Z-iris-oculus.zip` | `iris` | `1.20` 至 `1.21.x` |
| 🔭 OptiFine | `WireSight-X.Y.Z-optifine.zip` | `optifine` | `1.8` 至 `1.21.x` |

⚙️ GitHub Actions 会在推送时检查以下准确的提交标题后缀：

| 🎯 模式 | 提交标题后缀 | Actions 产物 | GitHub Release | Modrinth / CurseForge |
|---|---|:---:|:---:|:---:|
| 🛠️ 构建 | `(build action)` | ✅ | ❌ | ❌ |
| 🏷️ Release | `(build release)` | ✅ | ✅ | ❌ |
| 🚀 完整发布 | `(build publish)` | ✅ | ✅ | ✅ |

📝 工作流只检查标题行；提交正文中出现的相同文字会被忽略。

🔁 Pull Request 始终会执行构建。构建、Release 与平台发布也可以手动启动；推送 `v*` 标签只会创建对应的 GitHub Release。

📖 完整的流水线图、平台项目创建流程、GitHub Secrets、发布元数据、支持的 Minecraft 版本及发布说明格式，请参阅[构建、Release 与平台发布指南](.github/workflows/build.zh-cn.md)。

```bash
# 🛠️ 构建并上传 Actions 产物，但不创建 Release。
git commit --allow-empty -m "ci: test WireSight package (build action)"

# 🏷️ 构建并发布 metadata.toml 中声明的版本。
git commit -m "release: vX.Y.Z summary (build release)"

# 🚀 构建、创建 GitHub Release，并发布到 Modrinth 与 CurseForge。
git commit -m "release: vX.Y.Z summary (build publish)"
```
