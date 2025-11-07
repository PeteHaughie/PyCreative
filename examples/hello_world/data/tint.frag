#version 150
in vec2 v_texcoord;           // depends on presenter vertex shader; many use texcoord0->v_texcoord
out vec4 fragColor;
uniform sampler2D iChannel0;

void main() {
    // sample the incoming image and tint it magenta so we can verify
    // the shader pipeline is active and receiving the texture.
    vec4 src = texture(iChannel0, v_texcoord);
    // fragColor = vec4(src.rgb * vec3(1.0, 0.0, 1.0), src.a);
    fragColor = vec4(1.0, 0.0, 1.0, 1.0);
}