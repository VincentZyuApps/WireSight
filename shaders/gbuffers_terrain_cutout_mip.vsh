#version 120
// 🌲 使用 mipmap 的镂空地形顶点入口，通常覆盖树叶等远距离纹理对象。
// 世界坐标网格算法与其他地形一致，入口拆分由客户端渲染管线要求。
#define VERTEX_SHADER
#include "/program/wire_grid.glsl"
