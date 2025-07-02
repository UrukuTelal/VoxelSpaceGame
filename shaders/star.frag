#version 330 core

in vec3 frag_normal;
in vec3 frag_position;
in float time_offset;
in float animation_speed;

uniform float time;
uniform float alpha;
uniform float emissive;
uniform float pulse;
uniform vec3 light_pos;
uniform vec3 view_pos;

uniform float ambient_strength;
uniform vec3 tint;

uniform sampler2D sun_color;
uniform sampler2D sun_map;
uniform sampler2D sun_grayscale;
uniform sampler2D sun_grayscale_contrast;

uniform float wobble_strength;

out vec4 out_color;

// === get_sphere_uv() ===
vec2 get_sphere_uv(vec3 pos) {
    float u = 0.5 + atan(pos.z, pos.x) / (2.0 * 3.14159265359);
    float v = 0.5 - asin(pos.y) / 3.14159265359;
    return vec2(u, v);
}

/// === Perlin Noise Functions ===
vec4 permute(vec4 x) {
    return mod(((x * 34.0) + 1.0) * x, 289.0);
}

vec4 taylorInvSqrt(vec4 r) {
    return 1.79284291400159 - 0.85373472095314 * r;
}

float perlin_noise(vec3 v) {
    const vec2 C = vec2(1.0 / 6.0, 1.0 / 3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

    vec3 i = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);

    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);

    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;

    i = mod(i, 289.0);
    vec4 p = permute(permute(permute(
                i.z + vec4(0.0, i1.z, i2.z, 1.0))
              + i.y + vec4(0.0, i1.y, i2.y, 1.0))
              + i.x + vec4(0.0, i1.x, i2.x, 1.0));

    float n_ = 1.0 / 7.0;
    vec3 ns = n_ * D.wyz - D.xzx;

    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);
    vec4 x = x_ * ns.x + ns.yyyy;
    vec4 y = y_ * ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);

    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);

    vec4 s0 = floor(b0) * 2.0 + 1.0;
    vec4 s1 = floor(b1) * 2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));

    vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;

    vec3 g0 = vec3(a0.xy, h.x);
    vec3 g1 = vec3(a0.zw, h.y);
    vec3 g2 = vec3(a1.xy, h.z);
    vec3 g3 = vec3(a1.zw, h.w);

    vec4 norm = taylorInvSqrt(vec4(dot(g0,g0), dot(g1,g1), dot(g2,g2), dot(g3,g3)));
    g0 *= norm.x;
    g1 *= norm.y;
    g2 *= norm.z;
    g3 *= norm.w;

    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1),
                            dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;

    return 42.0 * dot(m * m, vec4(dot(g0,x0), dot(g1,x1), dot(g2,x2), dot(g3,x3)));
}

float fractal_noise(vec3 pos) {
    float total = 0.0;
    float frequency = 1.0;
    float amplitude = 1.0;
    float maxValue = 0.0;

    for (int i = 0; i < 6; i++) {
        total += perlin_noise(pos * frequency) * amplitude;
        maxValue += amplitude;
        frequency *= 2.0;
        amplitude *= 0.5;
    }

    return total / maxValue;
}


void main() {
    vec3 norm = normalize(frag_normal);
    vec3 frag_pos = frag_position;

    // Calculate light direction and diffuse
    vec3 light_dir = normalize(light_pos - frag_pos);
    float diff = max(dot(norm, light_dir), 0.0);

    // Optional: Specular lighting
    vec3 view_dir = normalize(view_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0); // shininess
    float specular_strength = 0.5;

    // Animate UV
    vec3 surface_pos = normalize(frag_position);
    float local_time = time * animation_speed + time_offset;
    vec2 uv = get_sphere_uv(surface_pos);
    uv += wobble_strength * vec2(
        sin(time * 2.0 + surface_pos.y * 8.0),
        cos(time * 1.5 + surface_pos.x * 8.0)
    );

    vec3 base_color = texture(sun_color, uv).rgb;
    vec3 inverted_color = texture(sun_map, uv).rgb;
    float grayscale = texture(sun_grayscale, uv).r;
    float height_factor = texture(sun_grayscale_contrast, uv).r;

    vec3 noise_input = surface_pos * 0.3 + vec3(time * 0.2, time * 0.1, time * 0.15);
    float detail_noise = fractal_noise(noise_input);
    float spot = smoothstep(0.1, 0.9, detail_noise * grayscale);
    spot *= 0.6 + 0.4 * sin(local_time * 1.5);

    float glow = emissive + pulse * 0.5 * sin(local_time * 2.0) + spot * 3.5;

    vec3 mixed_color = mix(base_color, inverted_color, 0.75);
    vec3 red_hot = mix(mixed_color, vec3(1.0, 0.1, 0.0), spot);

    vec3 lighting = glow * tint;  // Emissive is primary
    lighting += ambient_strength * red_hot; // minor base glow
    lighting += 0.5 * red_hot; // force additional flat color regardless of light_dir
    lighting += 0.2 * diff * red_hot;
    lighting += 0.1 * specular_strength * spec * red_hot;

    out_color = vec4(lighting, alpha);
}