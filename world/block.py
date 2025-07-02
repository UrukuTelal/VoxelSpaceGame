#block.py
import numpy as np
from pyrr import Matrix44
from core.block_registry import BLOCK_TYPES
from core.coordinates import gravity_vector_at, align_up_to_gravity
from rendering.geometry import *

def block_lookup_func(start_pos, end_pos, blocks, step=1.0):
    start_pos = np.asarray(start_pos, dtype=np.float32)
    end_pos = np.asarray(end_pos, dtype=np.float32)
    direction = end_pos - start_pos
    length = np.linalg.norm(direction)
    if length == 0:
        return []

    direction /= length
    blocks_in_path = []
    steps = int(length // step)

    for i in range(steps):
        pos = start_pos + direction * (i * step)
        for block in blocks:
            block_pos = np.asarray(block.position)
            if np.linalg.norm(block_pos - pos) < step * 0.5:
                blocks_in_path.append(block)
                break
    return blocks_in_path

def get_render_block(block, uv_scale=1.0):
    vertices, indices = generate_cube(uv_scale=uv_scale)
    vao, vbo, ebo = create_vao(vertices, indices)
    return RenderBlock(vao=vao, index_count=len(indices), position=np.array(block.position, dtype=np.float32))

class Block:
    def __init__(self, position, block_type="_default_", scale=1.0):
        self.position = position  # kept as list for consistency
        self.block_type = block_type
        self.scale = scale
        self.sub_blocks = []

        self.vertices, self.indices = generate_cube()
        self.index_count = len(self.indices)
        self.vao, self.vbo, self.ebo = create_vao(self.vertices, self.indices)

        props = BLOCK_TYPES.get(self.block_type, BLOCK_TYPES["_default_"])
        self.color = np.array(props.get("color", [1.0, 1.0, 1.0]), dtype=np.float32)
        self.tint = np.array(props.get("tint", [1.0, 1.0, 1.0]), dtype=np.float32)
        self.emissive = props.get("emissive", 0.0)
        self.alpha = props.get("alpha", 1.0)
        self.ambient_strength = props.get("ambient_strength", 0.3)
        self.textures = props.get("textures", {})

        self.rotation_angle = 0.0
        self.model_matrix = Matrix44.identity()

        self.grid_resolution = 10
        self.cell_size = self.scale / self.grid_resolution

    @property
    def np_position(self):
        return np.array(self.position, dtype=np.float32)

    def update(self, dt, gravity_center=np.zeros(3)):
        self.rotation_angle += dt * 30.0
        rot_y = Matrix44.from_y_rotation(np.radians(self.rotation_angle))

        gravity = gravity_vector_at(self.position, center=gravity_center)
        orientation = align_up_to_gravity(Matrix44.identity(), gravity)
        translation = Matrix44.from_translation(self.position)
        self.model_matrix = Matrix44(orientation) @ rot_y @ translation

    def draw(self, shader_program):
        glUseProgram(shader_program)
        loc_model = glGetUniformLocation(shader_program, "model")
        scale_matrix = Matrix44.from_scale([self.scale, self.scale, self.scale])
        model = scale_matrix @ self.model_matrix
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, model.astype(np.float32))

        glBindVertexArray(self.vao)
        glUniform3fv(glGetUniformLocation(shader_program, "color"), 1, self.color)
        glUniform3fv(glGetUniformLocation(shader_program, "tint"), 1, self.tint)
        glUniform1f(glGetUniformLocation(shader_program, "emissive"), self.emissive)
        glUniform1f(glGetUniformLocation(shader_program, "alpha"), self.alpha)
        glUniform1f(glGetUniformLocation(shader_program, "ambient_strength"), self.ambient_strength)

        if "color_map" in self.textures:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.textures["color_map"])
            glUniform1i(glGetUniformLocation(shader_program, "color_map"), 0)

        if "grayscale_map" in self.textures:
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.textures["grayscale_map"])
            glUniform1i(glGetUniformLocation(shader_program, "grayscale_map"), 1)

        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glUseProgram(0)

    def snap_to_block_grid(self, local_pos, size):
        """
        Snaps local_pos and size to the global grid with respect to this block's position grid origin.
        Positions snap to the grid cell origin, not block center.
        """
        step = self.cell_size
        block_origin = np.floor(np.array(self.position) / step) * step

        snapped_local = np.round(np.array(local_pos) / step) * step
        final_pos = block_origin + snapped_local

        snapped_size = max(step, round(size / step) * step)
        return final_pos, snapped_size

    class SubBlock:
        def __init__(self, local_pos, size=0.1, sub_type="default"):
            self.local_pos = np.array(local_pos, dtype=np.float32)
            self.size = size
            self.sub_type = sub_type

class ParticleBlock(Block):
    def __init__(self, position, velocity, block_type="_default_"):
        super().__init__(position, block_type)
        self.velocity = np.array(velocity, dtype=np.float32)

    def update(self, dt, attractor=np.zeros(3), gravity_strength=100.0):
        dir_vec = attractor - np.asarray(self.position)
        dist = np.linalg.norm(dir_vec)
        if dist > 0:
            self.velocity += (dir_vec / dist) * gravity_strength * dt
        self.position += self.velocity * dt

class AtmosphericBlock(Block):
    def __init__(self, position, block_type="air", velocity=None):
        super().__init__(position, block_type)
        self.velocity = np.array(velocity or [0.0, 0.0, 0.0])
        self.pressure = 1.0
        self.temperature = 288.0

class CloudBlock(ParticleBlock):
    def __init__(self, position, block_type="cloud", velocity=None):
        super().__init__(position, velocity or [0.0, 0.0, 0.0], block_type)
        self.opacity = 0.5

def apply_air_currents(air_blocks, cloud_blocks, dt):
    for cloud in cloud_blocks:
        influencing_air = [a for a in air_blocks if np.linalg.norm(np.asarray(a.position) - np.asarray(cloud.position)) < 4.0]
        if not influencing_air:
            continue
        avg_velocity = sum(a.velocity for a in influencing_air) / len(influencing_air)
        cloud.velocity += avg_velocity * dt

"""TODO:
make Atmosphere:
Terrain-aware
Heat-pressure-gradient driven
Spin-aware (Coriolis-style effects)
"""

"""TODO:
make Atmosphere:
Terrain-aware
Heat-pressure-gradient driven
Spin-aware (Coriolis-style effects)
"""

