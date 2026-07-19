#version 120
// 🌿 镂空地形的片元入口。核心程序读取纹理 alpha 并 discard 透明区域。
// 原纹理 RGB 不参与输出，所以可见部分仍保持统一的面色与边线色。
#define FRAGMENT_SHADER
#include "/program/wire_grid.glsl"
