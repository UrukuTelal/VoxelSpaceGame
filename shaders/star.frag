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
uniform float scale;

// Permutation and noise functions

vec3 mod289(vec3 x) {
    return x - floor(x * (1.0 / 289.0)) * 289.0;
}

vec4 mod289(vec4 x) {
    return x - floor(x * (1.0 / 289.0)) * 289.0;
}

vec4 permute(vec4 x) {
    return mod289(((x*34.0)+1.0)*x);
}

vec4 taylorInvSqrt(vec4 r) {
    return 1.79284291400159 - 0.85373472095314 * r;
}

float perlin_noise(vec3 P) {
    vec3 Pi0 = floor(P);        // Integer part for indexing
    vec3 Pi1 = Pi0 + vec3(1.0); // Integer part + 1
    Pi0 = mod289(Pi0);
    Pi1 = mod289(Pi1);
    vec3 Pf0 = fract(P);        // Fractional part for interpolation
    vec3 Pf1 = Pf0 - vec3(1.0);

    vec4 ix = vec4(Pi0.x, Pi1.x, Pi0.x, Pi1.x);
    vec4 iy = vec4(Pi0.y, Pi0.y, Pi1.y, Pi1.y);
    vec4 iz0 = vec4(Pi0.z);
    vec4 iz1 = vec4(Pi1.z);

    vec4 ixy = permute(permute(ix) + iy);
    vec4 ixy0 = permute(ixy + iz0);
    vec4 ixy1 = permute(ixy + iz1);

    vec4 gx0 = fract(ixy0 * (1.0 / 41.0)) * 2.0 - 1.0;
    vec4 gy0 = abs(gx0) - 0.5;
    vec4 tx0 = floor(gx0 + 0.5);
    gx0 = gx0 - tx0;

    vec4 gx1 = fract(ixy1 * (1.0 / 41.0)) * 2.0 - 1.0;
    vec4 gy1 = abs(gx1) - 0.5;
    vec4 tx1 = floor(gx1 + 0.5);
    gx1 = gx1 - tx1;

    vec3 g000 = vec3(gx0.x, gy0.x, gx0.y);
    vec3 g100 = vec3(gx0.z, gy0.z, gx0.w);
    vec3 g010 = vec3(gx0.y, gy0.y, gx0.z);
    vec3 g110 = vec3(gx0.w, gy0.w, gx0.w); // fixed here: last component from gx0.w (was gx0.x)

    vec3 g001 = vec3(gx1.x, gy1.x, gx1.y);
    vec3 g101 = vec3(gx1.z, gy1.z, gx1.w);
    vec3 g011 = vec3(gx1.y, gy1.y, gx1.z);
    vec3 g111 = vec3(gx1.w, gy1.w, gx1.x);

    vec4 norm0 = taylorInvSqrt(vec4(dot(g000,g000), dot(g010,g010), dot(g100,g100), dot(g110,g110)));
    g000 *= norm0.x;
    g010 *= norm0.y;
    g100 *= norm0.z;
    g110 *= norm0.w;

    vec4 norm1 = taylorInvSqrt(vec4(dot(g001,g001), dot(g011,g011), dot(g101,g101), dot(g111,g111)));
    g001 *= norm1.x;
    g011 *= norm1.y;
    g101 *= norm1.z;
    g111 *= norm1.w;

    float n000 = dot(g000, Pf0);
    float n100 = dot(g100, vec3(Pf1.x, Pf0.yz));
    float n010 = dot(g010, vec3(Pf0.x, Pf1.y, Pf0.z));
    float n110 = dot(g110, vec3(Pf1.xy, Pf0.z));
    float n001 = dot(g001, vec3(Pf0.xy, Pf1.z));
    float n101 = dot(g101, vec3(Pf1.x, Pf0.y, Pf1.z));
    float n011 = dot(g011, vec3(Pf0.x, Pf1.yz));
    float n111 = dot(g111, Pf1);

    vec3 fade_xyz = Pf0 * Pf0 * Pf0 * (Pf0 * (Pf0 * 6.0 - 15.0) + 10.0);
    vec4 n_z = mix(vec4(n000, n100, n010, n110), vec4(n001, n101, n011, n111), fade_xyz.z);
    vec2 n_yz = mix(n_z.xy, n_z.zw, fade_xyz.y);
    float n_xyz = mix(n_yz.x, n_yz.y, fade_xyz.x);

    return 2.2 * n_xyz; // Scale result to [-1,1]
}

float fractal_noise(vec3 pos) {
    float total = 0.0;
    float freq = 1.0;
    float amp = 1.0;
    float maxA = 0.0;
    for(int i=0; i<6; i++){
        total += perlin_noise(pos * freq) * amp;
        maxA += amp;
        freq *= 2.0;
        amp *= 0.5;
    }
    return total / maxA;
}

vec2 get_sphere_uv(vec3 pos) {
    float u = 0.5 + atan(pos.z, pos.x) / (2.0 * 3.14159265359);
    float v = 0.5 - asin(pos.y) / 3.14159265359;
    return vec2(u, v);
}

void main() {
    
    float noiseVal = perlin_noise(vec3(frag_position.x * scale, frag_position.y * scale, time));

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

    color = clamp(color, 0.0, 1.0);
    color = pow(color, vec3(1.0/2.2));

    out_color = vec4(color, alpha);
}
