#version 120
// 🌧️ 雨雪等天气效果的片元入口。原纹理 alpha 保留雨丝或雪片形状。
// 可见部分输出主题实体色，使天气仍可见但不会破坏整体配色。
#define FRAGMENT_SHADER
#include "/program/flat_textured.glsl"
