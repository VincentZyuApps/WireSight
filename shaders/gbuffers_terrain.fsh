#version 120
// 🗺️ 通用地形的片元入口。读取原纹理 alpha 后绘制深绿面与荧光绿方块边线。
// 单独保留此入口能覆盖 Iris、Oculus、OptiFine 之间可能不同的地形分流方式。
#define FRAGMENT_SHADER
#include "/program/wire_grid.glsl"
