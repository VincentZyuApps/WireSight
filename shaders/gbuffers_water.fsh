#version 120
// 🌊 水与半透明地形的片元入口。保留 alpha 剪影，但最终作为不透明建模面输出。
#define FRAGMENT_SHADER
// WATER_PASS 只切换到当前主题的水体面色；边线仍使用同一主题的边线色。
#define WATER_PASS
#include "/program/wire_grid.glsl"
