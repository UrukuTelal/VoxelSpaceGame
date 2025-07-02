#version 330 core

in vec3 frag_position;
in vec3 frag_normal;
in float time_offset;

out vec4 out_color;

uniform sampler2D sun_color;
uniform sampler2D sun_map;
uniform sampler2D sun_grayscale;
uniform sampler2D sun_grayscale_contrast;

uniform float time;
uniform float animation_speed;
uniform float emissive;
uniform float pulse;
uniform float wobble_strength;
uniform float alpha;
uniform vec3 tint;
uniform float ambient_strength;
uniform vec3 light_pos;
uniform vec3 view_pos;

// Permutation and noise functions from your original shader here
// (You can copy your entire perlin_noise and fractal_noise functions)

float noise(vec3 p) {
    // Implement or copy perlin_noise or fractal_noise from your original
    return fractal_noise(p);
}

vec2 get_sphere_uv(vec3 pos) {
    float u = 0.5 + atan(pos.z, pos.x) / (2.0 * 3.14159265359);
    float v = 0.5 - asin(pos.y) / 3.14159265359;
    return vec2(u, v);
}

void main() {
    vec3 N = normalize(frag_normal);
    vec3 V = normalize(view_pos - frag_position);
    vec3 L = normalize(light_pos - frag_position);
    vec3 H = normalize(L + V);

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(N, H), 0.0), 32.0);

    vec3 sphere_pos = normalize(frag_position);
    float local_time = time * animation_speed + time_offset;

    vec2 uv = get_sphere_uv(sphere_pos);
    uv += wobble_strength * vec2(
        sin(local_time * 2.0 + sphere_pos.y * 8.0),
        cos(local_time * 1.5 + sphere_pos.x * 8.0)
    );

    vec3 base_color = texture(sun_color, uv).rgb;
    vec3 inverted_color = texture(sun_map, uv).rgb;
    float grayscale = texture(sun_grayscale, uv).r;
    float contrast = texture(sun_grayscale_contrast, uv).r;

    float n = fractal_noise(sphere_pos * 0.3 + vec3(local_time * 0.2));
    float spot = smoothstep(0.1, 0.9, n * grayscale) * (0.6 + 0.4 * sin(local_time * 1.5));
    float glow = emissive + pulse * 0.5 * sin(local_time * 2.0) + spot * 3.5;

    vec3 hot_mix = mix(base_color, inverted_color, 0.75);
    vec3 red_hot = mix(hot_mix, vec3(1.0, 0.1, 0.0), spot);

    vec3 color = glow * tint;
    color += ambient_strength * red_hot;
    color += 0.5 * red_hot;
    color += 0.2 * diff * red_hot;
    color += 0.1 * spec * red_hot;

    // Clamp and gamma correct for better glow
    color = clamp(color, 0.0, 1.0);
    color = pow(color, vec3(1.0/2.2));

    out_color = vec4(color, alpha);
}
