#version 120
// ☁️ 原版云层的顶点入口。仅保留几何变换，云的颜色由极简天空程序统一处理。
// 即使 properties 已关闭普通云，也保留此入口以兼容不同客户端与模组调用。
#define VERTEX_SHADER
#include "/program/sky.glsl"
