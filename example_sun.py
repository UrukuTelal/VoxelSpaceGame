import math
import time
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *

from pyrr import Matrix44, quaternion, matrix44
from core.block_types import *
from core.block_registry import *
from rendering.geometry import *
from rendering.shader import load_shaders
from core.utility_belt import * 
from world.block import *
from core.lighting import *
from tqdm import tqdm
from world.planet_generator import *

WINDOW_SIZE = (1200, 720)

def init_pygame():
    pygame.init()
    pygame.display.set_mode(WINDOW_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Voxel Space Game - Star Example")

def setup_opengl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def load_texture(path):
    surface = pygame.image.load(path)
    image = pygame.image.tostring(surface, "RGB", True)
    width, height = surface.get_size()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id

def main():
    init_pygame()
    setup_opengl()

    # Load height map (required for your sphere generator)
    height_map = load_height_map("assets/2k_sun_grayscale.jpg")

    # Generate blocks with spherical layering
    vao_outer, index_count, instance_count_outer, outer_blocks = generate_spherical_blocks(
        radius=32.0,
        block_scale=1.0,
        grid_resolution=96,
        height_map=height_map,
        height_scale=0.1,
        layer_definitions=[(0.0, "_sun_molten_hydrogen_helium")]
    )
    # For brevity, assume inner and core blocks generated similarly...

    # Combine all blocks for lighting etc
    blocks = outer_blocks  # + inner_blocks + core_blocks if you want

    # Load and compile shaders - must return shader program id
    shader = load_shaders("shaders/star.vert", "shaders/star.frag")

    # Use shader program before setting uniforms
    glUseProgram(shader)

    # Load textures and assign texture units explicitly
    tex_color = load_texture("assets/2k_sun_color.jpg")               # GL_TEXTURE0
    tex_inverted = load_texture("assets/2k_sun_color_inverted.jpg")   # GL_TEXTURE1
    tex_gray = load_texture("assets/2k_sun_grayscale.jpg")            # GL_TEXTURE2
    tex_gray_contrast = load_texture("assets/2k_sun_color_inverted.jpg") # GL_TEXTURE3

    # Bind textures and set uniform samplers ONCE
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, tex_color)
    glUniform1i(glGetUniformLocation(shader, "sun_color"), 0)

    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, tex_inverted)
    glUniform1i(glGetUniformLocation(shader, "sun_map"), 1)

    glActiveTexture(GL_TEXTURE2)
    glBindTexture(GL_TEXTURE_2D, tex_gray)
    glUniform1i(glGetUniformLocation(shader, "sun_grayscale"), 2)

    glActiveTexture(GL_TEXTURE3)
    glBindTexture(GL_TEXTURE_2D, tex_gray_contrast)
    glUniform1i(glGetUniformLocation(shader, "sun_grayscale_contrast"), 3)

    # Camera setup
    eye = [130.0, 130.0, 130.0]
    view = Matrix44.look_at(eye=eye, target=[0,0,0], up=[0,1,0])
    proj = Matrix44.perspective_projection(45.0, WINDOW_SIZE[0]/WINDOW_SIZE[1], 0.1, 1000.0)

    glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view.astype('float32'))
    glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, proj.astype('float32'))

    # Set constant uniforms
    glUniform1f(glGetUniformLocation(shader, "alpha"), 1.0)
    glUniform3f(glGetUniformLocation(shader, "light_pos"), 0.0, 0.0, 0.0)
    glUniform3f(glGetUniformLocation(shader, "view_pos"), *eye)
    glUniform1f(glGetUniformLocation(shader, "wobble_strength"), 0.02)
    glUniform1f(glGetUniformLocation(shader, "animation_speed"), 1.0)
    glUniform1f(glGetUniformLocation(shader, "emissive"), 2.5)
    glUniform1f(glGetUniformLocation(shader, "pulse"), 1.5)
    glUniform3f(glGetUniformLocation(shader, "tint"), 1.0, 0.8, 0.3)
    glUniform1f(glGetUniformLocation(shader, "ambient_strength"), 0.3)

    clock = pygame.time.Clock()
    spin_angle = 0.0
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
        model_rotation = tilt_matrix @ Matrix44(spin_matrix)

        model_matrix = model_rotation

        # Upload model matrix
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model_matrix.astype("float32"))
        glUniform1f(glGetUniformLocation(shader, "time"), pygame.time.get_ticks() / 1000.0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw your blocks
        glBindVertexArray(vao_outer)
        glDrawElementsInstanced(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None, instance_count_outer)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
