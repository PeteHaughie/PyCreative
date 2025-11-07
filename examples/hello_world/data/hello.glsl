// Simple Hello World fragment shader - solid red
#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 iResolution;

void main() {
    vec2 uv = gl_FragCoord.xy / iResolution;
    // ignore uv - output constant red
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
