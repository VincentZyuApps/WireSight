#version 120
// 💡 通用带纹理且由游戏标记为受光照内容的顶点入口。
// 当前仍使用直通实现；该入口主要用于覆盖不同版本和模组的文字渲染分流。
#define VERTEX_SHADER
#include "/program/passthrough_textured.glsl"
