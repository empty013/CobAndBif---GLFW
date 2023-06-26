#version 460 core
#define eps pow(10, -6)
 layout (location = 0) in vec2 position;
layout (location = 1) uniform mat4 trafo;
uniform int n_iter;


out vec4 f_color;

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

float bifurcate(float x0, float a, int n_iter, inout vec4 color) {
    float x = x0;
    // for (int i = 0; i < n; i++) {
    //     x = f(x, a);
    // }
    x = f_iter(x, a, n_iter);

    // color = vec4(1.0f, 1.0f, 1.0f, 1.0f);
    color = vec4(1.0f, 1.0f, 1.0f, 1.0f);
    float x_1 = x;
    for (int i=0; i < 4; i++) {
        x_1 = f(x_1, a);
        if (x_1 - x < eps && x - x_1 < eps) {
            color = vec4(1.0f, 0.0f, 0.0f, 1.0f);
            break;
        }
    }
    
    // color = vec4(1.0f, 0.0f, 0.0f, 1.0f); 
    return x;
}

void main() {
    f_color = vec4(1.0f, 1.0f, 1.0f, 1.0f);
    vec4 coord = trafo * vec4(position, 0.0, 1.0);
    float x_asy = bifurcate(coord.y, coord.x, n_iter, f_color);
    vec4 x_trafo = transpose(trafo)[1];
    float x_pos = (x_asy - x_trafo[3]) / x_trafo[1];
    gl_Position = vec4(position.x, x_pos, 0.0, 1.0);
    
    // gl_Position = vec4(position, 0.0, 1.0);
}