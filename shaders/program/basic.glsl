#include "/lib/settings.glsl"

#ifdef VERTEX_SHADER

void main() {
    gl_Position = ftransform();
}

#endif

#ifdef FRAGMENT_SHADER

void main() {
    gl_FragData[0] = vec4(WIRESIGHT_ENTITY_COLOR, 1.0);
}

#endif
