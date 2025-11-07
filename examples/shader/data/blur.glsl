#version 150

uniform vec2 iResolution;
uniform sampler2D iChannel0;

out vec4 fragColor;

void main() {
  vec2 fragCoord = gl_FragCoord.xy;
  float Pi = 6.28318530718; // 2*Pi

  // GAUSSIAN BLUR SETTINGS
  float Directions = 16.0; // BLUR DIRECTIONS (more = slower)
  float Quality = 3.0;    // BLUR QUALITY (more = slower)
  float Size = 8.0;       // BLUR SIZE (radius)

  vec2 Radius = Size / iResolution;

  // Normalized pixel coordinates (0..1)
  vec2 uv = fragCoord / iResolution;
  vec4 Color = texture(iChannel0, uv);

  // Blur calculations
  for (float d = 0.0; d < Pi; d += Pi / Directions) {
    for (float i = 1.0 / Quality; i <= 1.0; i += 1.0 / Quality) {
      Color += texture(iChannel0, uv + vec2(cos(d), sin(d)) * Radius * i);
    }
  }

  // Normalize accumulated color
  Color /= (Quality * Directions);
  fragColor = Color;
}