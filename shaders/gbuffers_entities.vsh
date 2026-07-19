#version 120
// 👤 生物、掉落物、载具等普通实体的顶点入口。
// 共享纯色纹理程序会传递 UV，并按世界法线计算上/侧/下三档绿色亮度。
#define VERTEX_SHADER
#include "/program/flat_textured.glsl"
