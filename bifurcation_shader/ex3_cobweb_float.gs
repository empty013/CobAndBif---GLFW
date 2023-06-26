#version 460 compatibility
#define MAX_VERTICES 256
#define eps pow(10, -4)
#define cycle 2

layout(points) in;

// layout (location = 1) uniform mat4 trafo;
layout (location = 2) uniform float x_offset;
layout (location = 3) uniform float a_offset;
layout (location = 4) uniform float x_scale;
layout (location = 5) uniform float a_scale;
layout (location = 6) uniform float x0;
layout (location = 7) uniform float[10] x0s;

layout(points, max_vertices=MAX_VERTICES) out;
// out vec4 f_color;

float update_x(float x, float a) {
    return a * sin(x) * (1 - pow(x, 2)) - 1;
}

void bifurcate(float x0, float a, float x_scale, float x_offset) {
    // initial guess
    float x = x0;

    // throw away first N values in the series
    for (int i = 0; i < 50000; ++i) {
        x = update_x(x, a);
    }
    
    //float x_old[cycle];
    //x_old[0] = x;
    //for (int i = 0; i < cycle; i++) {
    //    x = update_x(x, a);
    //    x_old[i] = x;
    //}

    // emit point only if it lands inside viewspace
    int num_emitted = 0;
    
    //gl_Position = gl_in[0].gl_Position + vec4(0.0f, 0.5f, 0.0f, 0.0f);
    //EmitVertex();
    //EndPrimitive();
    //float x_old_old = x; 
    //float x_fix = x; // Check for cycles using this point: x(t+N) = x(t)
    //x = update_x(x, a);
    while (num_emitted < MAX_VERTICES / 10) {
        x = update_x(x, a);
        float pos = (x - x_offset) / x_scale;

        if(pos >= -1.0 && pos <= 1.0) {
            num_emitted++;
            gl_Position = gl_in[0].gl_Position + vec4(0.0f, pos, 0.0f, 0.0f);
            
            //for (i = 0; i < cycle; i++) {
            //    if (...
            //}
            //if (abs(x - x_old) < eps || abs(x - x_old_old) < eps) {
            //    f_color = vec4(1.0f, 0.0f, 0.0f, 1.0f);
            //}
            //else {
            //    f_color = vec4(1.0f, 1.0f, 1.0f, 1.0f);
            //}
            
            EmitVertex();
            EndPrimitive();
        }
        //x_old_old = x_old;
    }
}

void main() {
    float a = a_scale * gl_in[0].gl_Position.x + a_offset;
    for (int i=0; i < x0s.length(); i++) {
        bifurcate(x0s[i], a, x_scale, x_offset);
    }
    // bifurcate(-x0, a, x_scale, x_offset);
}