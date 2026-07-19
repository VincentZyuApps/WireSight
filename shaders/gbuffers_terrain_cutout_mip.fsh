#version 120
// 🌲 使用 mipmap 的镂空地形片元入口。alpha 测试保存远处叶片等对象的外形。
// 网格自身由解析坐标生成，不依赖原纹理的 mipmap 颜色。
#define FRAGMENT_SHADER
#include "/program/wire_grid.glsl"
