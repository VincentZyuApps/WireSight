#version 120
// 💡 受光照纹理内容的片元入口。保留完整颜色，优先保证世界文字可读。
// 名字里的 lit 是 Minecraft 的通道分类；本极简程序没有额外动态光照计算。
#define FRAGMENT_SHADER
#include "/program/passthrough_textured.glsl"
