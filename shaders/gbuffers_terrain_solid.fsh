#version 120
// 🧊 完全不透明地形的片元入口，直接计算纯色面与解析式荧光绿边线。
#define FRAGMENT_SHADER
// 跳过 texture2D 与 alpha 测试，是核心地形路径保持轻量的关键之一。
#define SOLID_PASS
#include "/program/wire_grid.glsl"
