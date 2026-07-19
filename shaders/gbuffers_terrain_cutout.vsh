#version 120
// 🌿 不透明镂空地形的顶点入口，例如叶片、草和带透明孔洞的方块纹理。
// 顶点阶段仍按普通地形计算网格坐标；透明轮廓会在片元阶段恢复。
#define VERTEX_SHADER
#include "/program/wire_grid.glsl"
