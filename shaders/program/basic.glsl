/*
 * 无纹理颜色直通程序 🎨
 *
 * 这个共享程序服务于 gbuffers_basic。它不套用绿色线框，而是保留 Minecraft
 * 随顶点传入的原始颜色与透明度，主要用于不依赖纹理的基础几何和文字背景等内容。
 * 具体进入该通道的对象可能随 Minecraft 版本、加载器和模组而变化。
 */

#ifdef VERTEX_SHADER

// 顶点颜色需要经过 varying 插值后交给片元阶段。
varying vec4 wsColor;

void main() {
    // 使用兼容管线提供的标准模型-视图-投影变换。
    gl_Position = ftransform();

    // gl_Color 包含 Minecraft 为当前顶点准备的 RGBA 颜色。
    wsColor = gl_Color;
}

#endif

#ifdef FRAGMENT_SHADER

varying vec4 wsColor;

void main() {
    // 🪟 完全透明或几乎透明的片元没有保留价值，直接丢弃并避免写入深度。
    if (wsColor.a < 0.01) discard;

    // 原样输出插值后的颜色，让文字背景、线条等基础元素保持可辨认。
    gl_FragData[0] = wsColor;
}

#endif
