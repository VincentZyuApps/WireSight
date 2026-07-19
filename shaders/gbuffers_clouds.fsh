#version 120
// ☁️ 原版云层的片元入口。复用 program/sky.glsl，默认把云输出为纯黑背景色。
// 不采样云纹理，有助于维持干净的 WireSight 轮廓画面。
#define FRAGMENT_SHADER
#include "/program/sky.glsl"
