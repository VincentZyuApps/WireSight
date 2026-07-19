#version 120
// 🔤 通用带纹理、无额外光照内容的顶点入口，常包含世界空间文字。
// 使用颜色直通程序，传递 UV 与顶点色，以恢复玩家名称和 Text Display 可读性。
#define VERTEX_SHADER
#include "/program/passthrough_textured.glsl"
