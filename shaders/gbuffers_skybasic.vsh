#version 120
// 🌌 无纹理天空几何的顶点入口，常用于基础天空穹顶等对象。
// 这里只执行标准位置变换，颜色由 program/sky.glsl 的片元部分统一给出。
#define VERTEX_SHADER
#include "/program/sky.glsl"
