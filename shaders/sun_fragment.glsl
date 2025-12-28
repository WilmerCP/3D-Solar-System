varying vec3 normal; // world space normal
varying vec3 coord;  // object space coordinate
uniform float time;

// Simple pseudo-random function for noise
float rand(vec2 co){
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

// Smooth noise by interpolating random
float noise(vec2 uv){
    vec2 i = floor(uv);
    vec2 f = fract(uv);
    float a = rand(i);
    float b = rand(i + vec2(1.0, 0.0));
    float c = rand(i + vec2(0.0, 1.0));
    float d = rand(i + vec2(1.0, 1.0));
    vec2 u = f*f*(3.0-2.0*f);
    return mix(a, b, u.x) + (c - a)*u.y*(1.0 - u.x) + (d - b)*u.x*u.y;
}

void main() {
    vec3 n = normalize(normal);
    vec3 viewDir = normalize(-coord);
    vec3 lightDir = normalize(vec3(0.2, 1.0, 0.3));

    // Lambert lighting
    float light = max(dot(n, lightDir), 0.0);

    // Core gradient
    float heat = clamp((coord.y + 1.0) * 0.5, 0.0, 1.0);
    vec3 sunColor = mix(vec3(1.0, 0.6, 0.1), vec3(1.0, 0.95, 0.8), heat);

    // Limb darkening
    float limbFactor = pow(clamp(dot(n, viewDir), 0.0, 1.0), 0.6);
    sunColor *= mix(0.6, 1.0, limbFactor);

    // Light shading
    vec3 shaded = sunColor * (0.5 + 0.5 * light);

    // Rim glow
    float rimGlow = pow(1.0 - dot(n, viewDir), 2.5);
    shaded += vec3(1.0, 0.6, 0.1) * rimGlow * 0.6;

    // --- Plasma flares ---
    float rimFlare = pow(clamp(1.0 - dot(n, viewDir), 0.0, 1.0), 3.0);
    float r = length(coord.xz);

    // swirling noise for plasma
    float swirl1 = noise(coord.xy * 5.0 + vec2(time*0.3, time*0.2));
    float swirl2 = noise(coord.yx * 8.0 - vec2(time*0.5, time*0.4));
    float plasma = pow(mix(swirl1, swirl2, 0.5), 2.0);

    float streak = smoothstep(0.9, 1.2, r);
    float flare = plasma * rimFlare * streak;

    vec3 flareColor = vec3(1.0, 0.6, 0.15);
    shaded += flareColor * flare * 0.8;

    gl_FragColor = vec4(shaded, 1.0);
}
