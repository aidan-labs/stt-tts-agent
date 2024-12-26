#version 120

attribute vec2 in_vert;
varying vec2 frag_uv;

void main() {
    frag_uv = in_vert * 0.5 + 0.5; // Transform from [-1,1] to [0,1]
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
