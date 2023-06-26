#version 460 core
layout (location = 0) in vec2 position;

layout (location = 1) uniform mat4 trafo;

layout (location = 2) uniform float x_scale;
layout (location = 3) uniform float x_offset;
layout (location = 4) uniform float y_scale;
layout (location = 5) uniform float y_offset;


// layout (location = 2) uniform float a;
// layout (location = 3) uniform float draw_f;
// layout (location = 4) uniform float x_zoom;
// layout (location = 5) uniform float y_zoom;
// layout (location = 6) uniform float x_offset;
// layout (location = 7) uniform float y_offset;

// float f(x, a) {
//     return 
// }

void main() {
    gl_Position = trafo * vec4(position, 0.0, 1.0);
    // float x = x_zoom * position.x + x_offset;
    // gl_Position = vec4((x_zoom * position.x - x_offset) / x_zoom, (y_zoom * position.y - y_offset) / y_zoom, 0.0, 1.0);
}