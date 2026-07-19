#version 120
// 🌌 无纹理天空几何的片元入口。默认输出不透明纯黑，衬托绿色网格。
// 不做光照、渐变或大气散射计算，是有意保持的极简设计。
#define FRAGMENT_SHADER
#include "/program/sky.glsl"
