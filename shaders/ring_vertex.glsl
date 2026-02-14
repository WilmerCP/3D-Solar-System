attribute vec3 position;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform float inner_radius;
uniform float outer_radius;

varying vec2 vTextCoord;
varying vec3 world_pos;

#define PI 3.14159265359

void main() {

    vec4 world_pos_4d = model * vec4(position, 1.0);

    world_pos = world_pos_4d.xyz;

    float angle = atan(position.z,position.x) + PI;
    float v = angle / (2.0 * PI);

    float r = sqrt(position.x * position.x + position.z * position.z);

    float u = (r-inner_radius) / (outer_radius-inner_radius);

    vTextCoord = vec2(u,v);

    gl_Position = projection * view * model * vec4(position, 1.0);
}