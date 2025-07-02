# main_star_example.py

import sys
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL

from OpenGL.GL import *

from pyrr import Matrix44

# Import your Block class
from world.block import Block
from core.block_registry import BLOCK_TYPES
from rendering.shader import load_shaders
from core.coordinates import *
from world.planet_generator import generate_sun_layers
from rendering.geometry import generate_cube
# Window settings
WINDOW_SIZE = (800, 600)

def init_pygame():
    pygame.init()
    pygame.display.set_mode(WINDOW_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Voxel Space Game - Star Example")

def setup_opengl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)  # black background




def main():
    init_pygame()
    setup_opengl()

    shaders = load_shaders("shaders/star.vert", "shaders/star.frag")
    glUseProgram(shaders)

    # Setup projection and view matrices (perspective camera)
    proj = Matrix44.perspective_projection(45.0, WINDOW_SIZE[0]/WINDOW_SIZE[1], 0.1, 1000.0)
    view = Matrix44.look_at(
        eye=[90.0, 90.0, 90.0],
        target=[0.0, 0.0, 0.0],
        up=[0.0, 1.0, 0.0]
    )

    loc_proj = glGetUniformLocation(shaders, "projection")
    loc_view = glGetUniformLocation(shaders, "view")

    glUniformMatrix4fv(loc_proj, 1, GL_FALSE, proj.astype(np.float32))
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, view.astype(np.float32))

    # Ensure star block type is registered in BLOCK_TYPES
    # For example "star_core" with appropriate textures, color, and emissive values.
    # If missing, add minimal entry here (or in your block_types.py):
    

    # Create a single Block instance for the star
    star_blocks = generate_sun_layers(radius=10.0)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(144) / 1000.0  # delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for block in star_blocks:
            block.update(dt)
            block.draw(shaders)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
