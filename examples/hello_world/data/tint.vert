#version 150
in vec2 position;
in vec2 texcoord0;
out vec2 v_texcoord;
void main() {
    v_texcoord = texcoord0;
    gl_Position = vec4(position, 0.0, 1.0);
}
