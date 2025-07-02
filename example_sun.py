import math
import time
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GL.shaders import glUseProgram

from pyrr import Matrix44, quaternion, matrix44
from core.block_types import *
from core.block_registry import *
from rendering.geometry import *
from rendering.shader import load_shaders
from core.utility_belt import *
from world.block import *
from core.lighting import *
from world.planet_generator import *
from tqdm import tqdm

DEBUG_SHADER = True  # Toggle shader debug output

WINDOW_SIZE = (1200, 720)

def init_pygame():
    pygame.init()
    pygame.display.set_mode(WINDOW_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Voxel Space Game - Star Example")

def setup_opengl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def main():
    init_pygame()
    setup_opengl()

    shader = load_shaders("shaders/star.vert", "shaders/star.frag")
    if shader == 0:
        raise RuntimeError("[🛑 Shader Error] Failed to compile/link shaders.")

    glUseProgram(shader)

    # Load height map for star surface shape
    height_map = load_height_map("assets/2k_sun_grayscale.jpg")
    vao_outer, index_count, instance_count_outer, outer_blocks = generate_spherical_blocks(
        radius=32.0,
        block_scale=1.0,
        grid_resolution=96,
        height_map=height_map,
        height_scale=0.1,
        layer_definitions=[(0.0, "_sun_molten_hydrogen_helium")]
    )

    # Bind textures with validation and error handling
    try:
        load_texture("assets/2k_sun_color.jpg", 0, shader, "sun_color")
        load_texture("assets/2k_sun_color_inverted.jpg", 1, shader, "sun_map")
        load_texture("assets/2k_sun_grayscale.jpg", 2, shader, "sun_grayscale")
        load_texture("assets/2k_sun_color_inverted.jpg", 3, shader, "sun_grayscale_contrast")
    except RuntimeError as e:
        print(f"[🛑 Texture Binding Error] {e}")
        pygame.quit()
        return

    # Camera setup
    eye = [130.0, 130.0, 130.0]
    view = Matrix44.look_at(eye=eye, target=[0, 0, 0], up=[0, 1, 0])
    proj = Matrix44.perspective_projection(45.0, WINDOW_SIZE[0] / WINDOW_SIZE[1], 0.1, 1000.0)

    # Upload matrices safely
    safe_uniform_mat4(shader, "view", view)
    safe_uniform_mat4(shader, "projection", proj)

    # Star visual properties uniforms
    safe_uniform_float(shader, "alpha", 1.0)
    safe_uniform_vec3(shader, "light_pos", 0.0, 0.0, 0.0)
    safe_uniform_vec3(shader, "view_pos", *eye)
    safe_uniform_float(shader, "wobble_strength", 0.02)
    safe_uniform_float(shader, "animation_speed", 1.0)
    safe_uniform_float(shader, "emissive", 2.5)
    safe_uniform_float(shader, "pulse", 1.5)
    safe_uniform_vec3(shader, "tint", 1.0, 0.8, 0.3)
    safe_uniform_float(shader, "ambient_strength", 0.3)
    safe_uniform_float(shader, "scale", 1.0)  # Added scale uniform for shader noise scale

    spin_angle = 0.0
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        dt = clock.tick(60) / 1000.0
        spin_angle += dt * 15.0

        axis = np.array([0.0, 1.0, 0.0])
        axis /= np.linalg.norm(axis)
        spin_quat = quaternion.create_from_axis_rotation(axis, math.radians(spin_angle))
        spin_matrix = matrix44.create_from_quaternion(spin_quat)
        tilt_matrix = Matrix44.from_x_rotation(math.radians(23.5))
        model_matrix = tilt_matrix @ Matrix44(spin_matrix)

        safe_uniform_mat4(shader, "model", model_matrix)
        safe_uniform_float(shader, "time", pygame.time.get_ticks() / 1000.0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindVertexArray(vao_outer)
        glDrawElementsInstanced(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None, instance_count_outer)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
