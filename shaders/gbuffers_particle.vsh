#version 120
// ✨ 普通粒子的顶点入口。将粒子四边形的位置和纹理坐标准备给共享程序。
// 粒子通常面向镜头，不适合套用世界方块网格，因此使用实体纯色路径。
#define VERTEX_SHADER
#include "/program/flat_textured.glsl"
