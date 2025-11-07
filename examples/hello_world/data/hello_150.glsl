#version 150

// Smoke-test variant: output a constant magenta color so we can verify
// the fragment shader executes and writes to the framebuffer.
out vec4 fragColor;
void main() {
    fragColor = vec4(1.0, 0.0, 1.0, 1.0);
}
