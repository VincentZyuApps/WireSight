#version 120
// ✋ 第一人称手臂与手持物的片元入口。
// 保留纹理透明轮廓并输出实体绿，不执行方块世界坐标网格算法。
#define FRAGMENT_SHADER
#include "/program/flat_textured.glsl"
