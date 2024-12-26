#version 120

uniform vec2 u_resolution;
uniform float u_time;
uniform float u_pulse_factor;

varying vec2 frag_uv;

vec2 hash(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(dot(hash(i + vec2(0.0, 0.0)), f - vec2(0.0, 0.0)),
                   dot(hash(i + vec2(1.0, 0.0)), f - vec2(1.0, 0.0)), u.x),
               mix(dot(hash(i + vec2(0.0, 1.0)), f - vec2(0.0, 1.0)),
                   dot(hash(i + vec2(1.0, 1.0)), f - vec2(1.0, 1.0)), u.x), u.y);
}

vec3 getGradientColor(float t) {
    vec3 purple = vec3(137.0/255.0, 41.0/255.0, 173.0/255.0);
    vec3 blue = vec3(67.0/255.0, 106.0/255.0, 172.0/255.0);
    vec3 teal = vec3(67.0/255.0, 183.0/255.0, 187.0/255.0);
    
    float cycle = fract(t);
    
    if (cycle < 0.33) {
        return mix(purple, blue, smoothstep(0.0, 1.0, cycle * 3.0));
    } else if (cycle < 0.66) {
        return mix(blue, teal, smoothstep(0.0, 1.0, (cycle - 0.33) * 3.0));
    } else {
        return mix(teal, purple, smoothstep(0.0, 1.0, (cycle - 0.66) * 3.0));
    }
}

void main() {
    vec2 uv = frag_uv;
    uv = uv * 2.0 - 1.0;

    uv.x *= u_resolution.x / u_resolution.y;

    float radius = 0.6 + u_pulse_factor * 0.1;
    float edgeThickness = 0.05;
    float dist = length(uv) - radius;

    float n = noise(uv * 4.0 + vec2(u_time * 0.5, u_time * 0.5)) * 0.1;
    n += noise(uv * 8.0 + vec2(u_time * 0.3, -u_time * 0.3)) * 0.05;

    float edge = smoothstep(edgeThickness, 0.0, dist + n);

    float gradientSpeed = 0.02;
    float gradientPosition = fract(uv.x * 0.25 - u_time * gradientSpeed); 
    vec3 color = getGradientColor(gradientPosition);

    color *= edge;

    gl_FragColor = vec4(color, edge);
}
