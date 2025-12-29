attribute vec3 position;
varying vec2 vUv;

void main(){
    vUv = position.xy * 0.5 + 0.5; // Map from [-1,1] to [0,1]
    gl_Position = vec4(position.xy,0,1.0);

}