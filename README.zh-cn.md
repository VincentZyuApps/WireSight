> **[📖 English](README.md)**
> **[📖 简体中文(大陆)](README.zh-cn.md)**

![WireSight](https://socialify.git.ci/VincentZyuApps/WireSight/image?custom_language=Shell&description=1&font=JetBrains+Mono&forks=1&issues=1&language=1&logo=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2F6%2F6a%2FGLSL_Logo_%2528Unofficial%2529.svg%2F960px-GLSL_Logo_%2528Unofficial%2529.svg.png%3F_%3D20250822083621&name=1&owner=1&pulls=1&stargazers=1&theme=Auto)

# WireSight

WireSight 是一款实验性、低开销的 Minecraft Java 版光影包，它将整个世界
渲染成类似实体建模视图的效果：方块表面呈深绿色，方块边线则呈明亮的
绿色。

本光影包面向 Iris、Oculus 与 OptiFine 共同支持的 OptiFine 光影包格式。
其核心路径使用 GLSL 1.20、单次地形渲染、常规深度写入，并且不包含阴影
或全屏后处理。

## 预览

![WireSight 将 Minecraft 世界渲染为绿色线框几何体](docs/images/preview/preview.png)

## 当前范围

- 在地形和方块实体上显示可见的 1x1 方块边界
- 使用三档纯色面明暗增强空间辨识度
- 使用像素宽度稳定且带抗锯齿的绿色边线
- 自动过滤远距离网格以减少闪烁
- 为树叶和植物等镂空几何体保留透明度
- 使用纯色渲染实体、粒子、天气效果和手持物品
- 为名称标签和世界空间文字保留原始颜色与透明度
- 使用不透明的风格化水体与黑色天空

WireSight 只能勾勒可见的几何体。它不是透视光影，也不会渲染 Minecraft
已从区块网格中剔除的表面。

## 兼容性目标

- Minecraft Java 版光影包加载器
- Iris
- Oculus
- OptiFine

首个经过测试的目标环境为 Minecraft 1.20.1、Oculus 1.8.0 与 Embeddium
0.3.31。本光影有意避免使用计算着色器、几何着色器以及加载器专属
扩展。

## 安装

将发布的 zip 文件放入 Minecraft 实例的 `shaderpacks` 目录，然后在
光影包菜单中选择 WireSight。

## 构建与发布

使用 7-Zip 在本地构建：

```bash
./scripts/build.sh
./scripts/build.sh X.Y.Z
```

构建生成的压缩包与 SHA-256 校验文件会写入 `dist/`。默认版本号取自
`VERSION` 文件中的值。

GitHub Actions 会在推送时检查以下提交信息标记：

- `build action`：构建并上传工作流产物
- `build release`：构建并发布 `main` 或 `master` 分支中 `VERSION` 指定的
  版本

Pull Request 始终会执行构建。构建和发布也可以手动启动，推送 `v*` 标签
则会发布对应的版本。

```bash
# 构建并上传 Actions 产物，但不创建 Release。
git commit --allow-empty -m "ci: test WireSight package (build action)"

# 构建并发布 VERSION 中声明的版本。
git commit -m "release: vX.Y.Z summary (build release)"
```
