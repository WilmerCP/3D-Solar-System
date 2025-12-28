uniform vec3 color_left;
uniform vec3 color_right;
varying vec3 normal; // world space normal
varying vec3 coord;  // object space coordinate
uniform float time;

// Simple pseudo-random function for noise
float rand(vec2 co){
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

void main() {

    vec3 n = normalize(normal);
    vec3 viewDir = normalize(-coord);
    vec3 lightDir = normalize(vec3(0.2, 1.0, 0.3));

    // Lambert lighting
    float light = max(dot(n, lightDir), 0.0);

    // Core gradient (top = hotter, bottom = cooler)
    float heat = clamp((coord.y + 1.0) * 0.5, 0.0, 1.0);
    vec3 sunColor = mix(vec3(1.0, 0.6, 0.1), vec3(1.0, 0.95, 0.8), heat);

    // Limb darkening
    float limbFactor = pow(clamp(dot(n, viewDir), 0.0, 1.0), 0.6);
    sunColor *= mix(0.6, 1.0, limbFactor);

    // Light shading
    vec3 shaded = sunColor * (0.5 + 0.5 * light);

    // Glow
    float rimGlow = pow(1.0 - dot(n, viewDir), 2.5);
    shaded += vec3(1.0, 0.6, 0.1) * rimGlow * 0.6;

    // --- Plasma flares ---
    float rimFlare = pow(clamp(1.0 - dot(n, viewDir), 0.0, 1.0), 3.0);
    float r = length(coord.xz); // distance from center

    // Combine multiple layers of noise for organic pattern
    float n1 = pow(rand(coord.xy*3.0 + time*0.3), 2.0);
    float n2 = pow(rand(coord.xy*7.0 - time*0.5), 2.0);
    float spikes = n1 * 0.6 + n2 * 0.4;

    float streak = smoothstep(0.9, 1.2, r); // fades outward
    float flare = spikes * rimFlare * streak;

    vec3 flareColor = vec3(1.0, 0.6, 0.15);
    shaded += flareColor * flare * 0.8;

    gl_FragColor = vec4(shaded, 1.0);
}
