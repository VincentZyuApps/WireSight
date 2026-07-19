#version 120
// 🌧️ 雨雪等天气效果的顶点入口。天气通常是面向镜头的纹理四边形。
// 因此使用实体纯色路径，而不是依赖世界表面法线的方块网格路径。
#define VERTEX_SHADER
#include "/program/flat_textured.glsl"
