#version 120
// 🧱 方块实体等 block 通道的片元入口，将可见表面改画成深绿面与荧光绿边线。
// 未定义 SOLID_PASS，因此核心程序会读取原纹理 alpha，兼容可能存在的镂空部分。
#define FRAGMENT_SHADER
#include "/program/wire_grid.glsl"
