#version 120
// 🌊 水与其他半透明地形的顶点入口，网格坐标计算与普通方块相同。
#define VERTEX_SHADER
// WATER_PASS 让共享程序选择当前主题的水体基础色。
#define WATER_PASS
#include "/program/wire_grid.glsl"
