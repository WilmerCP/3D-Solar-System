precision mediump float;

uniform sampler2D bgTexture;
varying vec2 vUv;

void main() {
    vec4 color = texture2D(bgTexture, vUv);
    gl_FragColor = color * 0.4; // Make the image darker
}