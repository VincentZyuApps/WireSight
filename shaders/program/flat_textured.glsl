#include "/lib/settings.glsl"

/*
 * 带纹理轮廓、使用统一纯色的轻量程序 👤
 *
 * 实体、手持物、粒子和天气仍需要原纹理的 alpha 来保留外形，例如角色皮肤
 * 四周的透明区域不能变成矩形。但纹理的 RGB 会被忽略，实际可见部分统一改成
 * WIRESIGHT_ENTITY_COLOR，再根据表面朝向给出三档亮度。
 */

#ifdef VERTEX_SHADER

// 将法线从相机空间旋回世界方向，用于判断面朝上、朝下还是朝侧面。
uniform mat4 gbufferModelViewInverse;

varying vec2 wsTexCoord;
varying float wsFaceShade;

void main() {
    // 📐 变换顶点，并把经过纹理矩阵处理的 UV 传给片元阶段。
    gl_Position = ftransform();
    wsTexCoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;

#if WIREFRAME_SHADING == 0
    // 关闭方向色阶时，所有可见纹理片元使用同一种实体绿。
    wsFaceShade = 1.0;
#else
    // 🧭 这里与 wire_grid.glsl 的面色阶一致：上亮、侧中、下暗。
    // 只变换方向，因此使用 mat3 丢掉矩阵中的平移分量。
    vec3 worldNormal = normalize(
        mat3(gbufferModelViewInverse) * (gl_NormalMatrix * gl_Normal)
    );
    if (worldNormal.y > 0.5) {
        wsFaceShade = 1.0;
    } else if (worldNormal.y < -0.5) {
        wsFaceShade = 0.38;
    } else {
        wsFaceShade = 0.68;
    }
#endif
}

#endif

#ifdef FRAGMENT_SHADER

uniform sampler2D texture;

varying vec2 wsTexCoord;
varying float wsFaceShade;

void main() {
    // 🪟 这里只需要原纹理的透明度。它保存实体、粒子和雨雪的真实剪影，
    // 同时避免材质花纹干扰统一的“黑客建模视图”配色。
    float alpha = texture2D(texture, wsTexCoord).a;
    if (alpha < 0.01) discard;

    // 🟩 实体基础绿乘以方向亮度；沿用原 alpha 以保留柔和粒子边缘。
    gl_FragData[0] = vec4(WIRESIGHT_ENTITY_COLOR * wsFaceShade, alpha);
}

#endif
