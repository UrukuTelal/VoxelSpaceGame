#block.py
import numpy as np
from pyrr import Matrix44
from core.block_registry import BLOCK_TYPES
from core.coordinates import gravity_vector_at, align_up_to_gravity
from rendering.geometry import *

def block_lookup_func(start_pos, end_pos, all_blocks, step=1.0):
    direction = end_pos - start_pos
    length = np.linalg.norm(direction)
    if length == 0:
        return []

    direction /= length
    blocks_in_path = []
    steps = int(length // step)

    for i in range(steps):
        pos = start_pos + direction * (i * step)
        for block in all_blocks:
            if np.linalg.norm(block.position - pos) < step * 0.5:
                blocks_in_path.append(block)
                break
    return blocks_in_path

def get_render_block(block, uv_scale=1.0):
    vertices, indices = generate_cube(uv_scale=uv_scale)  # <-- add parameter pass here

    vao, vbo, ebo = create_vao(vertices, indices)
    return RenderBlock(vao=vao, index_count=len(indices), position=np.array(block.position, dtype=np.float32))

# Block lookup & light
class Block:
    def __init__(self, position, block_type="_default_", scale=1.0):
        self.position = position
        self.block_type = block_type
        self.scale = scale
        self.sub_blocks = []
        # Mesh setup
        self.vertices, self.indices = generate_cube()
        self.index_count = len(self.indices)
        self.vao, self.vbo, self.ebo = create_vao(self.vertices, self.indices)

        # Visual properties from BLOCK_TYPES
        props = BLOCK_TYPES.get(self.block_type, BLOCK_TYPES["_default_"])
        self.color = np.array(props.get("color", [1.0, 1.0, 1.0]), dtype=np.float32)
        self.tint = np.array(props.get("tint", [1.0, 1.0, 1.0]), dtype=np.float32)
        self.emissive = props.get("emissive", 0.0)
        self.alpha = props.get("alpha", 1.0)
        self.ambient_strength = props.get("ambient_strength", 0.3)
        self.textures = props.get("textures", {})

        # Default model matrix
        self.rotation_angle = 0.0
        self.model_matrix = Matrix44.identity()

    def update(self, dt, gravity_center=np.zeros(3)):
        self.rotation_angle += dt * 30.0  # degrees per second
        rot_y = Matrix44.from_y_rotation(np.radians(self.rotation_angle))

        # Compute gravity direction and align model matrix
        gravity = gravity_vector_at(self.position, center=gravity_center)
        orientation = align_up_to_gravity(Matrix44.identity(), gravity)

        # Combine rotation and translation
        translation = Matrix44.from_translation(self.position)
        self.model_matrix = Matrix44(orientation) @ rot_y @ translation

    def draw(self, shader_program):
        glUseProgram(shader_program)

        # Get uniform location ONCE
        loc_model = glGetUniformLocation(shader_program, "model")

        # Create scale matrix and combine with model matrix
        scale_matrix = Matrix44.from_scale([self.scale, self.scale, self.scale])
        model = scale_matrix @ self.model_matrix

        # Upload the combined model matrix (with scale)
        glUniformMatrix4fv(loc_model, 1, GL_FALSE, model.astype(np.float32))

        # Bind VAO
        glBindVertexArray(self.vao)

        # Set other uniforms
        glUniform3fv(glGetUniformLocation(shader_program, "color"), 1, self.color)
        glUniform3fv(glGetUniformLocation(shader_program, "tint"), 1, self.tint)
        glUniform1f(glGetUniformLocation(shader_program, "emissive"), self.emissive)
        glUniform1f(glGetUniformLocation(shader_program, "alpha"), self.alpha)
        glUniform1f(glGetUniformLocation(shader_program, "ambient_strength"), self.ambient_strength)

        # Bind textures if available
        if "color_map" in self.textures:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.textures["color_map"])
            glUniform1i(glGetUniformLocation(shader_program, "color_map"), 0)

        if "grayscale_map" in self.textures:
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.textures["grayscale_map"])
            glUniform1i(glGetUniformLocation(shader_program, "grayscale_map"), 1)

        # Draw elements
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
        glUseProgram(0)


    class SubBlock:
        def __init__(self, local_pos, size=0.1, sub_type="default"):
            self.local_pos = np.array(local_pos, dtype=np.float32)  # values from 0 to 1 in parent space
            self.size = size
            self.sub_type = sub_type

# Particle blocks
class ParticleBlock(Block):
    def __init__(self,position,velocity,block_type="_default_"):
        super().__init__(position,block_type)
        self.velocity=np.array(velocity,dtype=np.float32)
    def update(self,dt,attractor=np.zeros(3),gravity_strength=100.0):
        dir_vec=attractor-self.position; dist=np.linalg.norm(dir_vec)
        if dist>0: self.velocity+=(dir_vec/dist)*gravity_strength*dt
        self.position+=self.velocity*dt