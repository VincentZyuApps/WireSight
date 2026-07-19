#version 120
// 🧱 方块实体等 block 通道的顶点入口；具体归类会因 Minecraft 版本或模组而异。
// 复用核心网格程序，在顶点阶段准备世界网格坐标、方向亮度与相机距离。
#define VERTEX_SHADER
#include "/program/wire_grid.glsl"
