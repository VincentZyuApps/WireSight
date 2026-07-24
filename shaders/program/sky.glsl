#include "/lib/settings.glsl"

/*
 * 极简天空程序 🌌
 *
 * 天空、云、太阳、月亮和星星统一输出 WIRESIGHT_SKY_COLOR。预设的纯黑背景可以
 * 最大化明亮主题边线的对比度，也省去了纹理采样和复杂大气计算。
 */

#ifdef VERTEX_SHADER

void main() {
    // 只保留 Minecraft 已提供的几何变换，不需要额外 varying。
    gl_Position = ftransform();
}

#endif

#ifdef FRAGMENT_SHADER

void main() {
    // 🌑 不透明地输出统一天空色；四套内置预设均使用纯黑。
    gl_FragData[0] = vec4(WIRESIGHT_SKY_COLOR, 1.0);
}

#endif
