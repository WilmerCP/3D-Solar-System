attribute vec3 position;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;
varying vec3 normal;
varying vec3 coord;
varying vec3 world_pos;
varying vec2 vTexCoord;

#define PI 3.14159265359

void main(){

    vec4 transformed = projection * view * model * vec4(position,1.0);
    gl_Position = transformed;

    mat3 N = transpose(inverse(mat3(model)));
    normal = N * position;

    coord = position;

    // Calculate world-space position
    world_pos = (model * vec4(position, 1.0)).xyz;

    float u = 0.5 + atan(position.z, position.x) / (2.0 * PI); // longitude
    float v = 0.5 - asin(position.y) / PI;                 // latitude


    vTexCoord = vec2(u,v);

}