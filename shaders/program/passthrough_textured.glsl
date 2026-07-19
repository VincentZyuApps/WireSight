/*
 * 带纹理颜色直通程序 🔤
 *
 * gbuffers_textured 与 gbuffers_textured_lit 常承载玩家头顶名称、Text Display、
 * 告示牌文字等必须阅读的世界空间内容。若像实体那样把纹理 RGB 强制改成纯绿，
 * 字形和背景可能失去对比度，看起来像“文字消失”。因此这条路径保留完整纹理颜色。
 *
 * 代价是这些通道中的其他内容也会保留原色；这是为可读性和跨版本兼容做的取舍。
 */

#ifdef VERTEX_SHADER

varying vec2 wsTexCoord;
varying vec4 wsColor;

void main() {
    // 📐 标准顶点变换。
    gl_Position = ftransform();

    // UV 经过纹理矩阵后再插值，兼容 Minecraft 对字形图集和其他纹理的处理。
    wsTexCoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;

    // 顶点色通常包含文字颜色、亮度调制或透明度，必须一同保留。
    wsColor = gl_Color;
}

#endif

#ifdef FRAGMENT_SHADER

uniform sampler2D texture;

varying vec2 wsTexCoord;
varying vec4 wsColor;

void main() {
    // 🎨 将纹理 RGBA 与顶点 RGBA 相乘，复现兼容管线的基本着色方式。
    // 对文字而言，纹理提供字形覆盖率，顶点色提供文字本身的颜色与透明度。
    vec4 color = texture2D(texture, wsTexCoord) * wsColor;

    // 完全透明区域不写颜色和深度，避免字形四周的透明矩形遮挡后方内容。
    if (color.a < 0.01) discard;
    gl_FragData[0] = color;
}

#endif
