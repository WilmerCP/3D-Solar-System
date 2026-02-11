precision mediump float;
uniform vec3 color;
uniform sampler2D texture;

varying vec2 vTextCoord;
void main() {

    vec4 color = texture(texture, vTextCoord);

    float alpha = color.a;
    if(alpha < 0.1)
        discard;

    gl_FragColor = color;
}