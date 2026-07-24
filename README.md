> **[📖 English](README.md)**
> **[📖 简体中文(大陆)](README.zh-cn.md)**

![WireSight](https://socialify.git.ci/VincentZyuApps/WireSight/image?custom_language=Shell&description=1&font=JetBrains+Mono&forks=1&issues=1&language=1&logo=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2F6%2F6a%2FGLSL_Logo_%2528Unofficial%2529.svg%2F960px-GLSL_Logo_%2528Unofficial%2529.svg.png%3F_%3D20250822083621&name=1&owner=1&pulls=1&stargazers=1&theme=Auto)

# WireSight

WireSight is an experimental, low-overhead Minecraft Java shaderpack that renders
the world like a solid modeling view: dark green faces with bright green block
edges.

The pack targets the OptiFine shaderpack format shared by Iris, Oculus, and
OptiFine. Its core path uses GLSL 1.20, a single terrain pass, normal depth
writes, and no shadows or full-screen post-processing.

## Preview

![WireSight rendering a Minecraft world as green wireframe geometry](docs/images/preview/preview.png)

## Default theme colors

WireSight uses the following base colors by default (RGB and hex denote the same color):

- Regular block faces: `RGB(6, 17, 11)` / `#06110B` (dark green)
- Water and translucent terrain faces: `RGB(5, 21, 19)` / `#051513` (dark cyan-green)
- Block edges: `RGB(53, 255, 120)` / `#35FF78` (fluorescent green)
- Entities, held items, particles, and weather: `RGB(14, 61, 34)` / `#0E3D22` (flat green)
- Sky, sun, moon, and clouds: `RGB(0, 0, 0)` / `#000000` (black)

These values are base colors; directional face shading further darkens terrain and entity sides and undersides.

## Shader settings

WireSight uses the common OptiFine ShaderPack option format supported by Iris, Oculus, and OptiFine. The loader skin may differ, but the controls and order remain the same.

### Main screen

```text
+--------------------------------+--------------------------------+
| Theme Preset: WireSight Green  | Custom Theme Colors...         |
| Directional Face Shading: On   | Edge Width: 1.5                |
| Edge Fade Start: 96 blocks     | Edge Fade Length: 64 blocks    |
+--------------------------------+--------------------------------+
```

- `Directional Face Shading` uses fixed brightness levels for top, side, and underside faces; it is not dynamic lighting.
- `Edge Width` controls the approximate on-screen pixel width of block edges.
- `Edge Fade Start` is the distance where edges begin fading.
- `Edge Fade Length` is the distance used to complete that fade, so the defaults end at `96 + 64 = 160` blocks.

### Custom theme colors

```text
+----------------------+----------------------+----------------------+
| Theme Preset: Custom                                               |
+----------------------+----------------------+----------------------+
| Block Face R: 6      | Block Face G: 17     | Block Face B: 11     |
| Water R: 5           | Water G: 21          | Water B: 19          |
| Block Edge R: 53     | Block Edge G: 255    | Block Edge B: 120    |
| Entity R: 14         | Entity G: 61         | Entity B: 34         |
| Sky R: 0             | Sky G: 0             | Sky B: 0             |
+----------------------+----------------------+----------------------+
```

> **Important:** Custom RGB values are applied only when `Theme Preset` is set to `Custom`.

Each channel has full integer precision from `0` to `255`. Custom values remain saved when another preset is selected and return unchanged when switching back to `Custom`.

### Built-in presets

| Surface | WireSight Green | Cyan | Amber | Monochrome |
|---|---|---|---|---|
| Block faces | `#06110B` | `#061116` | `#171006` | `#111111` |
| Water | `#051513` | `#051522` | `#071417` | `#151515` |
| Block edges | `#35FF78` | `#35E7FF` | `#FFC247` | `#F2F2F2` |
| Entities | `#0E3D22` | `#0E3540` | `#5E3D10` | `#3D3D3D` |
| Sky and celestials | `#000000` | `#000000` | `#000000` | `#000000` |

The Amber preset intentionally keeps water cool and dark to distinguish it from warm terrain. Changing an option may briefly recompile the shader.

## Current scope

- Visible 1x1 block boundaries on terrain and block entities
- Three flat face shades for spatial readability
- Pixel-stable, antialiased theme-colored edges
- Automatic distant-grid filtering to reduce shimmer
- Alpha preservation for cutout geometry such as leaves and plants
- Flat-color entities, particles, weather, and held items
- Original colors and transparency for name tags and world-space text
- Opaque stylized water and a configurable sky

Only visible geometry can be outlined. WireSight is not an X-ray shader and does
not render faces that Minecraft removes from chunk meshes.

## Compatibility target

- Minecraft Java Edition shaderpack loaders
- Iris
- Oculus
- OptiFine

The first tested target is Minecraft 1.20.1 with Oculus 1.8.0 and Embeddium
0.3.31. The shader intentionally avoids compute shaders, geometry shaders, and
loader-specific extensions.

## Install

Place the release zip in the Minecraft instance's `shaderpacks` directory, then
select WireSight from the shader pack menu.

## Build and release

Build locally with the 7-Zip CLI available in `PATH`:

```bash
./scripts/build.sh
./scripts/build.sh X.Y.Z
python scripts/build.py
python scripts/build.py X.Y.Z
```

Archives and SHA-256 checksum files are written to `dist/`. The version defaults
to the value in `VERSION`.

GitHub Actions observes these exact commit-subject suffixes on pushes:

- `(build action)`: build and upload a workflow artifact
- `(build release)`: build and publish the version in `VERSION` from `main` or
  `master`

Only the subject line is inspected; matching text in the commit body is ignored.

Pull requests are always built. Builds and releases can also be started
manually, and pushing a `v*` tag publishes the matching release version.

```bash
# Build and upload an Actions artifact without creating a Release.
git commit --allow-empty -m "ci: test WireSight package (build action)"

# Build and publish the version declared in VERSION.
git commit -m "release: vX.Y.Z summary (build release)"
```
