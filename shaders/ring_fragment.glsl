precision mediump float;
uniform sampler2D texture;

uniform vec3 planetCenter;
uniform float planetRadius;

varying vec2 vTextCoord;
varying vec3 world_pos;

void main() {

    vec3 origin = vec3(0,0,0); //Sun position

    vec3 distance_vector = world_pos - origin; //Vector between fragment and sun

    vec3 dir = normalize(distance_vector);

    float a = dot(dir,dir);

    vec3 L = origin - planetCenter; //Vector between sun and planet center

    float b = 2 * dot(dir,L);
    float c = dot(L,L) - pow(planetRadius,2);

    float discriminant = pow(b,2) - (4 * a * c);

    float dist_planet = sqrt(pow(L.x,2)+pow(L.y,2)+pow(L.z,2));

    float dist_fragment = sqrt(pow(distance_vector.x,2)+pow(distance_vector.y,2)+pow(distance_vector.z,2));

    //Min Distance from line to planet center = sqrt(-DL^2 + LL)
    //discriminant is actually = 4[R^2 - dMin^2]

    //distance between two intersections t1-t2 = sqrt(discriminant)
    float inter_distance = sqrt(discriminant);

    //normalize
    float penetration = inter_distance / (2 * planetRadius);

    //Full penetration from center -> 1
    //At the edges -> 0
    float shadowFactor = clamp(penetration, 0.0, 1.0);

    vec4 color = texture(texture, vTextCoord);

    float alpha = color.a;
    if(alpha < 0.1)
        discard;

    float shadow = 0;

    if (discriminant >=0 && dist_fragment > dist_planet ){
        shadowFactor = smoothstep(0.0, 1.0, shadowFactor);
        shadow = 0.2;
    }

    gl_FragColor = color * (1 - shadow * shadowFactor);
}