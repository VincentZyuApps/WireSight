#version 120
// 🌌 无纹理天空几何的片元入口。预设默认输出不透明纯黑，衬托明亮网格。
// 不做光照、渐变或大气散射计算，是有意保持的极简设计。
#define FRAGMENT_SHADER
#include "/program/sky.glsl"
