#version 120
// 🧊 完全不透明地形的顶点入口，也是普通方块最常用、最省成本的路径。
#define VERTEX_SHADER
// SOLID_PASS 告诉共享程序：无需声明或采样原版方块纹理。
#define SOLID_PASS
#include "/program/wire_grid.glsl"
