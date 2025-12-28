uniform vec3 color_left;
uniform vec3 color_right;
varying vec3 normal; //World space normal
varying vec3 coord; //Object space coordinate
varying vec3 world_pos; //World space position

void main() {

    vec3 n = normalize(normal);

    float t = (coord.x + 1.0) * 0.5;
    vec3 base_color = mix(color_left,color_right,t);

    vec3 lightDir = normalize(vec3(0.0)-world_pos);
    // Lambert lighting
    float light = dot(n,lightDir);
    //Force it to be between 0 and 1
    light = clamp(light, 0.0, 1.0);


    vec3 shadedColor = mix(
        base_color * 0.6,                // shadow
        mix(base_color, vec3(1.0), 0.4), // highlight
        light
    );

    gl_FragColor = vec4(shadedColor,1.0);
}