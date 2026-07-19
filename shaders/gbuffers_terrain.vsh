#version 120
// 🗺️ 通用地形的顶点入口。部分客户端会把未细分的地形批次送入这个通道。
// wire_grid.glsl 会为每个顶点生成稳定对齐方块边界的二维网格坐标。
#define VERTEX_SHADER
#include "/program/wire_grid.glsl"
