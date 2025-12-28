varying vec3 normal; //World space normal
varying vec3 coord; //Object space coordinate
varying vec3 world_pos; //World space position
varying vec2 vTexCoord;
uniform sampler2D texture;

void main() {

    vec3 n = normalize(normal);

    vec3 color = texture2D(texture, vTexCoord).rgb;

    vec3 lightDir = normalize(vec3(0.0)-world_pos);
    // Lambert lighting
    float light = dot(n,lightDir);
    //Force it to be between 0 and 1
    light = clamp(light, 0.0, 1.0);

    vec3 shadedColor = mix(
        color * 0.6,                // shadow
        mix(color, vec3(1.0), 0.4), // highlight
        light
    );

    gl_FragColor = vec4(shadedColor,1.0);
}