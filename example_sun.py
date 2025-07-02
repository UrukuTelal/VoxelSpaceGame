# example_sun.py
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

WINDOW_SIZE = (1200, 720)

def init_pygame():
    pygame.init()
    pygame.display.set_mode(WINDOW_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Voxel Space Game - Star Example")

def setup_opengl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)  # black background


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

def generate_baked_mesh(radius=33.3, thickness=5.0, divisions=140, height_map=None, height_scale=3.0):
    assert height_map is not None, "Height map is required for displaced mesh."
    
    shell_size = (radius + height_scale) * 2
    block_size = shell_size / divisions
    half = shell_size / 2.0

    base_outer = radius
    base_inner = max(0, radius - thickness)

    instance_positions = []

    height_h, height_w = height_map.shape    

    def get_uv(pos):
        x, y, z = pos
        u = 0.5 + math.atan2(z, x) / (2 * math.pi)
        v = 0.5 - math.asin(y) / math.pi
        return u, v

    def sample_height(u, v):
        i = int(u * (height_w - 1)) % height_w
        j = int(v * (height_h - 1)) % height_h
        return height_map[j, i]

    start_time = time.time()

    for x in range(divisions):
        for y in range(divisions):
            for z in range(divisions):
                bx = -half + x * block_size + block_size / 2.0
                by = -half + y * block_size + block_size / 2.0
                bz = -half + z * block_size + block_size / 2.0
                center = np.array([bx, by, bz])
                dist = np.linalg.norm(center)
                if dist == 0:
                    continue

                direction = center / dist
                u, v = get_uv(direction)
                height = sample_height(u, v)
                displace = (height - 0.5) * 2.0 * height_scale
                adjusted_outer = base_outer + displace
                adjusted_inner = max(0, adjusted_outer - (base_outer - base_inner))

                if adjusted_inner <= dist <= adjusted_outer:
                    instance_positions.append(center.tolist())

                

    elapsed = time.time() - start_time
    print(f"\nPlanet generation complete in {time.strftime('%H:%M:%S', time.gmtime(elapsed))}.")

    instance_data = np.array(instance_positions, dtype=np.float32)

    vertices, indices = generate_cube()
    vao, vbo, ebo = create_vao(vertices, indices)

    instance_vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, instance_vbo)
    glBufferData(GL_ARRAY_BUFFER, instance_data.nbytes, instance_data, GL_STATIC_DRAW)

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
    glVertexAttribDivisor(2, 1)
    glBindVertexArray(0)

    return vao, len(indices), len(instance_positions), instance_positions



def load_height_map(path):
    surface = pygame.image.load(path).convert()
    w, h = surface.get_size()
    pixels = pygame.surfarray.array3d(surface)
    # Convert RGB to grayscale float between 0-1 (using luminosity method)
    grayscale = (0.2126 * pixels[:,:,0] + 0.7152 * pixels[:,:,1] + 0.0722 * pixels[:,:,2]) / 255.0
    return np.flipud(grayscale.T)  # Transpose + flip for UV coords if needed


def main():
    pygame.init()
    init_pygame()
    height_map = load_height_map("assets/2k_sun_grayscale.jpg")
    define_blocks("assets/star_color_inverted.jpg", "assets/star_color_grayscale.jpg")
    
    glEnable(GL_DEPTH_TEST)
    
    
    blocks = []
    vao_outer, index_count, instance_count, outer_instance_positions = generate_baked_mesh(32.0, 2.0, 96, height_map, 0.1)
    vao_inner, _, instance_count_inner, inner_instance_positions = generate_baked_mesh(16.0, 2.0, 48, height_map, 0.01)
    vao_core, _, instance_count_core, core_instance_positions = generate_baked_mesh(8.0, 2.0, 24, height_map, 0.001)
    if vao_outer: 
        blocks += blocks
    elif vao_inner > 0.0:
        blocks += blocks
    elif vao_core > 0.0:
        blocks += blocks
    
    shader = load_shaders("shaders/star.vert", "shaders/star.frag")
    glUseProgram(shader)

    tex_color = load_texture("assets/2k_sun_color.jpg")
    tex_inverted = load_texture("assets/2k_sun_color_inverted.jpg")
    tex_gray = load_texture("assets/2k_sun_grayscale.jpg")
    tex_gray_contrast = load_texture("assets/2k_sun_color_inverted.jpg")

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, tex_color)
    glUniform1i(glGetUniformLocation(shader, "sun_color"), 0)

    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, tex_color)
    glUniform1i(glGetUniformLocation(shader, "sun_map"), 1)

    glActiveTexture(GL_TEXTURE2)
    glBindTexture(GL_TEXTURE_2D, tex_gray)
    glUniform1i(glGetUniformLocation(shader, "sun_grayscale"), 2)

    glActiveTexture(GL_TEXTURE3)
    glBindTexture(GL_TEXTURE_2D, tex_gray)
    glUniform1i(glGetUniformLocation(shader, "sun_grayscale_contrast"), 3)

    eye = [30.0, 30.0, 30.0]
    view = Matrix44.look_at(eye=eye, target=[0, 0, 0], up=[0, 1, 0])
    proj = Matrix44.perspective_projection(45.0, 1280 / 720, 0.1, 1000.0)
    glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view.astype('float32'))
    glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, proj.astype('float32'))

    glUniform1f(glGetUniformLocation(shader, "alpha"), 1.0)
    glUniform3f(glGetUniformLocation(shader, "light_pos"), 0.0, 0.0, 0.0)
    glUniform3f(glGetUniformLocation(shader, "view_pos"), *eye)
    glUniform1f(glGetUniformLocation(shader, "wobble_strength"), 0.01)

    orbit_radius = 0.0
    spin_angle = 0.0
    orbit_angle = 0.0

    clock = pygame.time.Clock()

    emitters_cache = {}
    render_block_cache = {}
    occlusion_cache = {}
    particle_blocks = []
    
    vertices, indices = generate_cube()
    vao_particle, _, _ = create_vao(vertices, indices)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        dt = clock.tick(60) / 1000.0
        fps = clock.get_fps()
        print(f"FPS: {fps:.2f}", end='\r')
        spin_angle += dt * 15.0
        orbit_angle += dt * 5.0
        if not math.isfinite(spin_angle):
            spin_angle = 0.0

        axis = np.array([0.0, 1.0, 0.0])
        axis /= np.linalg.norm(axis)
        spin_quat = quaternion.create_from_axis_rotation(axis, math.radians(spin_angle))

        spin_matrix = matrix44.create_from_quaternion(spin_quat)
        tilt_matrix = Matrix44.from_x_rotation(math.radians(23.5))
        model_rotation = tilt_matrix @ Matrix44(spin_matrix)

        orbit_x = math.cos(math.radians(orbit_angle)) * orbit_radius
        orbit_z = math.sin(math.radians(orbit_angle)) * orbit_radius
        orbit_translation = Matrix44.from_translation([orbit_x, 0.0, orbit_z])

        model_matrix = orbit_translation @ model_rotation
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model_matrix.astype("float32"))
        glUniform1f(glGetUniformLocation(shader, "time"), pygame.time.get_ticks() / 1000.0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        emitters_cache = [b for b in blocks if block_is_emitter("_sun_molten_hydrogen_helium")]
        occlusion_cache.clear()

        block_lighting = {}
        for block in blocks:
            def cached_block_lookup(start_pos, end_pos):
                key = (tuple(start_pos), tuple(end_pos))
                if key in occlusion_cache:
                    return occlusion_cache[key]
                blocks_path = block_lookup_func(start_pos, end_pos, blocks)
                occlusion_cache[key] = blocks_path
                return blocks_path

            light = compute_received_light(block, emitters_cache, cached_block_lookup)
            block_lighting[tuple(block.position)] = light

        average_light = sum(block_lighting.values()) / max(len(block_lighting), 1)
        glUniform1f(glGetUniformLocation(shader, "ambient_light"), average_light)

        for vao, count, instances, block_name, tex_override in [
            (vao_outer, index_count, instance_count, "_sun_molten_hydrogen_helium", tex_color),
            (vao_inner, index_count, instance_count_inner, "_sun_molten_hydrogen_helium", tex_color),
            (vao_core, index_count, instance_count_core, "_sun_molten_hydrogen_helium", tex_color)
        ]:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, tex_override)
            glUniform1i(glGetUniformLocation(shader, tex_color), 0)
            glBindVertexArray(vao)
            glDrawElementsInstanced(GL_TRIANGLES, count, GL_UNSIGNED_INT, None, instances)


        pygame.display.flip()

if __name__ == '__main__':
    main()