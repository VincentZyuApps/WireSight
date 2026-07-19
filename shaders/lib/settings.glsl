#ifndef WIRESIGHT_SETTINGS_GLSL
#define WIRESIGHT_SETTINGS_GLSL

/*
 * WireSight 的集中配置文件 🛠️
 *
 * 所有程序都从这里读取画面参数。把选项集中起来有两个好处：
 * 1. 修改颜色时不用逐个寻找顶点着色器和片元着色器；
 * 2. Iris、Oculus、OptiFine 可以从行尾的方括号识别可选值，并生成设置界面。
 */

// 🧭 是否根据面的朝向使用三个离散亮度：上面最亮、侧面居中、下面最暗。
// 0 = 所有面同亮；1 = 开启方向色阶。它不是动态光照，计算成本非常低。
#define WIREFRAME_SHADING 1 // [0 1]

// 📏 目标边线宽度，单位近似为屏幕像素。真正的换算在 wire_grid.glsl 中由 fwidth 完成。
#define EDGE_WIDTH 1.5 // [1.0 1.25 1.5 1.75 2.0]

// 🌫️ 方块格线从多少格视距开始淡出，并在多少格视距后完全消失。
// 远处格线会挤在少量像素里；让它们淡出既能减少摩尔纹，也让画面更稳定。
#define GRID_FADE_START 96.0 // [48.0 64.0 80.0 96.0 128.0 160.0]
#define GRID_FADE_END 160.0 // [96.0 128.0 160.0 192.0 256.0]

/*
 * 🎨 WireSight 调色板
 *
 * GLSL 的颜色分量范围是 0.0 到 1.0，而常见 RGB 范围是 0 到 255。
 * 例如 53 / 255 ≈ 0.208，所以边线颜色 (0.208, 1.000, 0.471)
 * 大约等于 RGB(53, 255, 120)，也就是十六进制 #35FF78。
 *
 * 注意：这些常量是“基础颜色”。地形和实体在输出前还可能乘以 wsFaceShade，
 * 因此朝下的面会比这里写出的颜色更暗。边线颜色不乘色阶，始终保持醒目。
 */

// 🟩 普通方块面的深绿色，约为 RGB(6, 17, 11) / #06110B。
const vec3 WIRESIGHT_FACE_COLOR = vec3(0.024, 0.067, 0.043);

// 🌊 水与半透明地形面的深青绿色，约为 RGB(5, 21, 19) / #051513。
const vec3 WIRESIGHT_WATER_COLOR = vec3(0.018, 0.082, 0.074);

// ✨ 方块边线的荧光绿，约为 RGB(53, 255, 120) / #35FF78。
const vec3 WIRESIGHT_EDGE_COLOR = vec3(0.208, 1.000, 0.471);

// 👤 实体、手持物、粒子和天气的纯色绿，约为 RGB(14, 61, 34) / #0E3D22。
const vec3 WIRESIGHT_ENTITY_COLOR = vec3(0.055, 0.240, 0.135);

// 🌌 天空、太阳、月亮和云使用纯黑，突出前景中的绿色几何结构。
const vec3 WIRESIGHT_SKY_COLOR = vec3(0.0);

#endif
