#version 330 core

layout (location = 0) in vec3 a_position;
layout (location = 1) in vec3 a_normal;
layout (location = 2) in vec3 instance_offset;  // <-- Re-add this for instancing

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform float time;
uniform float animation_speed;

out vec3 frag_position;
out vec3 frag_normal;
out float time_offset;

void main() {
    vec3 world_position = a_position + instance_offset;

    frag_position = vec3(model * vec4(world_position, 1.0));
    frag_normal = mat3(transpose(inverse(model))) * a_normal;

    // Optional: variation to desync animations per vertex
    time_offset = sin(dot(world_position, vec3(12.9898, 78.233, 37.719))) * 43758.5453;

    gl_Position = projection * view * vec4(frag_position, 1.0);
}
