#include "/lib/settings.glsl"

/*
 * WireSight 的核心：在普通三角形表面上绘制“方块面 + 方块边线” 🧊
 *
 * 这里没有把方块真的改画成 12 条 GL 线段，也没有使用几何着色器。
 * Minecraft 仍按原方式提交方块表面的三角形，所以深度测试、遮挡关系和固体渲染
 * 都可以继续工作。片元阶段只根据世界坐标判断当前像素离整数方块边界有多近，
 * 然后在当前主题的面色与明亮边线色之间混合。这就是本项目的低成本线框方案。
 *
 * 同一个文件会被编译两次：入口定义 VERTEX_SHADER 时编译顶点部分，
 * 定义 FRAGMENT_SHADER 时编译片元部分。这样两阶段可以共享一份算法文件。
 */

#ifdef VERTEX_SHADER

// Iris / OptiFine 提供的视图矩阵逆矩阵：用于从相机空间返回玩家/世界方向空间。
uniform mat4 gbufferModelViewInverse;

// 相机在世界中的位置。数值很大时浮点精度会下降，下面只使用它的小数部分。
uniform vec3 cameraPosition;

// varying 由顶点着色器输出，经三角形插值后交给片元着色器。
varying vec2 wsTexCoord;
varying vec2 wsGridCoord;
varying float wsFaceShade;
varying float wsViewDistance;

// 🧭 根据世界空间法线选择三档纯色亮度，廉价地保留方块的立体方向感。
float getFaceShade(vec3 normal) {
#if WIREFRAME_SHADING == 0
    // 用户关闭方向色阶时，不改变基础面色。
    return 1.0;
#else
    // 朝上的面最亮，朝下的面最暗，四个侧面使用中间亮度。
    // 对轴对齐的 Minecraft 方块来说，这些分支的结果在一个面内基本一致。
    if (normal.y > 0.5) return 1.0;
    if (normal.y < -0.5) return 0.38;
    return 0.68;
#endif
}

void main() {
    // 📐 ftransform() 等价于使用 Minecraft 当前的模型视图投影矩阵变换顶点。
    // GLSL 1.20 的兼容写法有利于同时照顾 Iris、Oculus 和 OptiFine。
    gl_Position = ftransform();

    // 保存经过纹理矩阵处理的 UV。固体方块不需要采样；树叶、草等 cutout
    // 仍要读取纹理 alpha，才能丢弃原纹理中本来透明的部分。
    wsTexCoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;

    // gl_ModelViewMatrix 先把当前顶点变到相机空间；逆矩阵再去掉相机旋转，
    // 得到以玩家为局部原点的位置。局部坐标比巨大世界坐标拥有更好的浮点精度。
    vec4 viewPosition = gl_ModelViewMatrix * gl_Vertex;
    vec3 playerPosition = (gbufferModelViewInverse * viewPosition).xyz;

    // 🧩 补回相机世界坐标的小数部分，使网格始终对齐 Minecraft 的整数方块边界。
    // 不补这一项时，玩家在一个方块内部移动会让整张网格跟随镜头滑动。
    // 不使用 cameraPosition 的整数部分，是为了避免远离世界原点后的精度抖动；
    // 对周期为 1 格的网格来说，整数平移不会改变结果，所以可以安全省略。
    vec3 worldPosition = playerPosition + fract(cameraPosition);

    // 法线先由 Minecraft 的法线矩阵变到相机空间，再由逆视图旋回世界方向。
    vec3 worldNormal = normalize(
        mat3(gbufferModelViewInverse) * (gl_NormalMatrix * gl_Normal)
    );
    vec3 normalWeight = abs(worldNormal);

    // 🗺️ 把三维方块表面投影到最合适的二维平面：
    // - 法线主要沿 X：这是东西侧面，使用 YZ 坐标；
    // - 法线主要沿 Y：这是顶面或底面，使用 XZ 坐标；
    // - 法线主要沿 Z：这是南北侧面，使用 XY 坐标。
    // 被法线指向的那一维在整个平面上近似不变，因此将它丢掉后，剩余两维
    // 正好形成每隔 1 格重复一次的方形网格。max 分量判断也能兼容非标准斜面。
    if (normalWeight.x >= normalWeight.y && normalWeight.x >= normalWeight.z) {
        wsGridCoord = worldPosition.yz;
    } else if (normalWeight.y >= normalWeight.z) {
        wsGridCoord = worldPosition.xz;
    } else {
        wsGridCoord = worldPosition.xy;
    }

    // 亮度和相机距离只需在顶点计算，然后让光栅化器在面内插值。
    wsFaceShade = getFaceShade(worldNormal);
    wsViewDistance = length(viewPosition.xyz);
}

#endif

#ifdef FRAGMENT_SHADER

// SOLID_PASS 由 gbuffers_terrain_solid 入口定义。固体地形没有镂空区域，
// 因而完全不必读取原版纹理；跳过一次 texture2D 是这个方案的重要省时点。
#ifndef SOLID_PASS
uniform sampler2D texture;
#endif

varying vec2 wsTexCoord;
varying vec2 wsGridCoord;
varying float wsFaceShade;
varying float wsViewDistance;

/*
 * ✨ 计算当前片元被边线覆盖的比例，返回 0.0（纯面）到 1.0（纯边线）。
 * coordinate 是前面选出的二维世界坐标，每个整数都对应一条方块边界。
 */
float getGridCoverage(vec2 coordinate) {
    // fract(x + 0.5) 把坐标折回一个宽度为 1 的重复单元；减 0.5 再取绝对值，
    // 得到当前点到最近整数网格线的距离。X/Y 两个分量分别代表两组垂直线。
    // 示例：坐标 3.02 距离整数 3 只有 0.02，因此非常接近一条边线。
    vec2 distanceToLine = abs(fract(coordinate + 0.5) - 0.5);

    // 📏 fwidth 大致等于该坐标跨过一个屏幕像素时的变化量
    //（内部是 abs(dFdx) + abs(dFdy)）。将世界单位距离与 pixelSpan 比较，
    // 就能让 EDGE_WIDTH 表示近似屏幕像素，而不是随远近变化的世界单位宽度。
    // max 下限避免极端情况下除零式的不稳定和退化导数。
    vec2 pixelSpan = max(fwidth(coordinate), vec2(0.0001));
    float halfWidth = EDGE_WIDTH * 0.5;

    // smoothstep 在内外边缘间生成柔和过渡，相当于给线条做廉价抗锯齿。
    // ±0.5 像素为抗锯齿过渡区；线内 coverage 接近 1，线外接近 0。
    vec2 innerEdge = pixelSpan * max(halfWidth - 0.5, 0.0);
    vec2 outerEdge = pixelSpan * (halfWidth + 0.5);
    vec2 coverage = 1.0 - smoothstep(innerEdge, outerEdge, distanceToLine);

    // 🌫️ 远处一个像素可能横跨多个方块，这时已经无法稳定分辨每条格线。
    // pixelSpan 从 0.18 增长到 0.50 时逐渐压低线条，避免闪烁和摩尔纹。
    // 这主要改善画质稳定性；它不会减少已经产生的片元数量。
    float undersampling = 1.0 - smoothstep(
        0.18,
        0.50,
        max(pixelSpan.x, pixelSpan.y)
    );

    // 两组网格线取最大覆盖率，任何一组命中都会发亮；交叉点仍保持 1.0，
    // 不会因为把两组覆盖率相加而过曝。
    return max(coverage.x, coverage.y) * undersampling;
}

void main() {
#ifndef SOLID_PASS
    // 🌿 cutout 地形（树叶、草、栅栏纹理孔洞等）必须尊重原纹理透明度。
    // 这里只采样 alpha，不保留纹理 RGB，因此仍呈现 WireSight 的统一纯色。
    if (texture2D(texture, wsTexCoord).a < 0.10) discard;
#endif

    // 从 EDGE_FADE_START 开始，在 EDGE_FADE_LENGTH 格距离内把边线淡到 0。
    // “起点 + 长度”始终能得到有效终点，不会出现终点早于起点的设置组合。
    float distanceFade = 1.0 - smoothstep(
        EDGE_FADE_START,
        EDGE_FADE_START + EDGE_FADE_LENGTH,
        wsViewDistance
    );
    float grid = getGridCoverage(wsGridCoord) * distanceFade;

#ifdef WATER_PASS
    // 🌊 水和其他半透明地形使用当前主题的水体面色，但仍作为不透明表面写入深度。
    // 这是视觉上的建模视图，不是真正透视；可以避开透明混合带来的 overdraw。
    vec3 faceColor = WIRESIGHT_WATER_COLOR * wsFaceShade;
#else
    // 普通地形的主题基础颜色乘以三档方向亮度。
    vec3 faceColor = WIRESIGHT_FACE_COLOR * wsFaceShade;
#endif

    // 🎨 最终混色：grid=0 输出纯 faceColor，grid=1 输出当前主题的边线色，
    // 抗锯齿过渡区则输出两者之间的颜色。alpha 固定为 1，继续写入可靠深度。
    gl_FragData[0] = vec4(mix(faceColor, WIRESIGHT_EDGE_COLOR, grid), 1.0);
}

#endif
