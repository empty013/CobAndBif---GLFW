#version 460 core
layout (location = 0) in vec2 position;

layout (location = 1) uniform mat4 trafo_func;
layout (location = 2) uniform float x_scale;
layout (location = 3) uniform float x_offset;
layout (location = 4) uniform float y_scale;
layout (location = 5) uniform float y_offset;
layout (location = 6) uniform float a;
uniform int n;

float f(float x, float a) {
    // return a * x * (1 - pow(x, 2));
    return a * sin(x) * (1 - pow(x, 2)) - 1;
}

float f_iter(float x, float a, int n) {
    for (int i=0; i<n; i++) {
        x = f(x, a);
    }
    return x;
}


void main() {
    float x = position.x * x_scale + x_offset;
    float y = f_iter(x, a, n);
    float y_pos = (y - y_offset) / y_scale;
// 
    // vec4 tmp = trafo_func * vec4(x, y, 0.0, 1.0);
    gl_Position = vec4(position.x, y_pos, 0.0, 1.0);

}