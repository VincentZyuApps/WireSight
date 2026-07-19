#include "/lib/settings.glsl"

#ifdef VERTEX_SHADER

uniform mat4 gbufferModelViewInverse;
uniform vec3 cameraPosition;

varying vec2 wsTexCoord;
varying vec2 wsGridCoord;
varying float wsFaceShade;
varying float wsViewDistance;

float getFaceShade(vec3 normal) {
#if WIREFRAME_SHADING == 0
    return 1.0;
#else
    if (normal.y > 0.5) return 1.0;
    if (normal.y < -0.5) return 0.38;
    return 0.68;
#endif
}

void main() {
    gl_Position = ftransform();
    wsTexCoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;

    vec4 viewPosition = gl_ModelViewMatrix * gl_Vertex;
    vec3 playerPosition = (gbufferModelViewInverse * viewPosition).xyz;
    vec3 worldPosition = playerPosition + fract(cameraPosition);
    vec3 worldNormal = normalize(
        mat3(gbufferModelViewInverse) * (gl_NormalMatrix * gl_Normal)
    );
    vec3 normalWeight = abs(worldNormal);

    if (normalWeight.x >= normalWeight.y && normalWeight.x >= normalWeight.z) {
        wsGridCoord = worldPosition.yz;
    } else if (normalWeight.y >= normalWeight.z) {
        wsGridCoord = worldPosition.xz;
    } else {
        wsGridCoord = worldPosition.xy;
    }

    wsFaceShade = getFaceShade(worldNormal);
    wsViewDistance = length(viewPosition.xyz);
}

#endif

#ifdef FRAGMENT_SHADER

#ifndef SOLID_PASS
uniform sampler2D texture;
#endif

varying vec2 wsTexCoord;
varying vec2 wsGridCoord;
varying float wsFaceShade;
varying float wsViewDistance;

float getGridCoverage(vec2 coordinate) {
    vec2 distanceToLine = abs(fract(coordinate + 0.5) - 0.5);
    vec2 pixelSpan = max(fwidth(coordinate), vec2(0.0001));
    float halfWidth = EDGE_WIDTH * 0.5;
    vec2 innerEdge = pixelSpan * max(halfWidth - 0.5, 0.0);
    vec2 outerEdge = pixelSpan * (halfWidth + 0.5);
    vec2 coverage = 1.0 - smoothstep(innerEdge, outerEdge, distanceToLine);

    float undersampling = 1.0 - smoothstep(
        0.18,
        0.50,
        max(pixelSpan.x, pixelSpan.y)
    );
    return max(coverage.x, coverage.y) * undersampling;
}

void main() {
#ifndef SOLID_PASS
    if (texture2D(texture, wsTexCoord).a < 0.10) discard;
#endif

    float distanceFade = 1.0 - smoothstep(
        GRID_FADE_START,
        max(GRID_FADE_START + 1.0, GRID_FADE_END),
        wsViewDistance
    );
    float grid = getGridCoverage(wsGridCoord) * distanceFade;

#ifdef WATER_PASS
    vec3 faceColor = WIRESIGHT_WATER_COLOR * wsFaceShade;
#else
    vec3 faceColor = WIRESIGHT_FACE_COLOR * wsFaceShade;
#endif

    gl_FragData[0] = vec4(mix(faceColor, WIRESIGHT_EDGE_COLOR, grid), 1.0);
}

#endif
