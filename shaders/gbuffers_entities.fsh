#version 120
// 👤 普通实体的片元入口。只借用原纹理 alpha 保存剪影，RGB 改为主题实体色。
// 因为实体不是规则方块，这条路径不尝试生成每格边线。
#define FRAGMENT_SHADER
#include "/program/flat_textured.glsl"
