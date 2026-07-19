#include "/lib/settings.glsl"

#ifdef VERTEX_SHADER

uniform mat4 gbufferModelViewInverse;

varying vec2 wsTexCoord;
varying float wsFaceShade;

void main() {
    gl_Position = ftransform();
    wsTexCoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;

#if WIREFRAME_SHADING == 0
    wsFaceShade = 1.0;
#else
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
    float alpha = texture2D(texture, wsTexCoord).a;
    if (alpha < 0.01) discard;
    gl_FragData[0] = vec4(WIRESIGHT_ENTITY_COLOR * wsFaceShade, alpha);
}

#endif
