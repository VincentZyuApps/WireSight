#version 120
// 🎨 基础无纹理几何的顶点入口。逐顶点变换位置，并把原始顶点色传给片元阶段。
// 实际算法位于 program/basic.glsl；入口宏让共享文件只编译其中的顶点部分。
#define VERTEX_SHADER
#include "/program/basic.glsl"
