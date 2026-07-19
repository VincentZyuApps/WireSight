#version 120
// 🔤 通用带纹理内容的片元入口。完整保留纹理 RGB、顶点色与 alpha。
// 它有意不套用实体纯绿，避免名称标签、告示牌等文字失去前景/背景对比。
#define FRAGMENT_SHADER
#include "/program/passthrough_textured.glsl"
