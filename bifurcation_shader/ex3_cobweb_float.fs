# version 460 core
in vec4 f_color;
out vec4 fragment_color;

void main() {
    // fragment_color = vec4(1.0f, 1.0f, 1.0f, 1.0f);
    fragment_color = f_color;
}