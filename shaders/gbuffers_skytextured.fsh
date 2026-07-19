#version 120
// 🌙 带纹理天空对象的片元入口。忽略原纹理并输出统一天空色。
// shaders.properties 也会关闭常规日月星，但入口仍为兼容性保留。
#define FRAGMENT_SHADER
#include "/program/sky.glsl"
