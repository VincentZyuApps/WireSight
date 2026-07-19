#version 120
// ✨ 普通粒子的片元入口。原纹理 alpha 保存烟雾、火花等形状，可见部分染成绿色。
// 共享程序会丢弃完全透明区域，避免整个粒子四边形遮挡背景。
#define FRAGMENT_SHADER
#include "/program/flat_textured.glsl"
