#utility_belt.py
import numpy as np
import pygame
from OpenGL.GL import *

#DEBUG_SHADER = False

def validate_uniform(shader, name, expected_type="float"):
    loc = glGetUniformLocation(shader, name)
    if loc == -1:
        if DEBUG_SHADER:
            print(f"[WARN] Uniform '{name}' not found or inactive in shader.")
    else:
        if DEBUG_SHADER:
            print(f"[OK]   Uniform '{name}' found at location {loc}.")
    return loc

def bind_texture_unit(shader, texture_id, unit, uniform_name):
    glActiveTexture(GL_TEXTURE0 + unit)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    loc = validate_uniform(shader, uniform_name)
    if loc != -1:
        glUniform1i(loc, unit)
    else:
        print(f"[ERROR] Failed to bind '{uniform_name}' to texture unit {unit}.")


def check_compile_status(shader):
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
        error = glGetShaderInfoLog(shader)
        raise RuntimeError(f"Shader compile error: {error}")

def check_link_status(program):
    result = glGetProgramiv(program, GL_LINK_STATUS)
    if not result:
        error = glGetProgramInfoLog(program)
        raise RuntimeError(f"Program link error: {error}")

def load_height_map(path):
    surface = pygame.image.load(path).convert()
    w, h = surface.get_size()
    pixels = pygame.surfarray.array3d(surface)
    # Convert RGB to grayscale float between 0-1 using luminosity formula
    grayscale = (0.2126 * pixels[:, :, 0] + 0.7152 * pixels[:, :, 1] + 0.0722 * pixels[:, :, 2]) / 255.0
    # Flip + transpose to align with UV coords if needed
    return np.flipud(grayscale.T)


class SpatialMap:
    def __init__(self, chunk_size=16):
        self.chunk_size = chunk_size
        self.chunks = {}

    def _chunk_coords(self, position):
        return tuple((np.floor(position / self.chunk_size)).astype(int))

    def insert(self, block):
        key = self._chunk_coords(block.position)
        self.chunks.setdefault(key, []).append(block)

    def query_line(self, start, end, steps=100):
        direction = end - start
        path = []
        for i in range(steps + 1):
            pos = start + direction * (i / steps)
            chunk_key = self._chunk_coords(pos)
            if chunk_key in self.chunks:
                for block in self.chunks[chunk_key]:
                    if np.allclose(block.position, pos, atol=0.5):
                        path.append(block)
        return path

def safe_uniform_float(shader, name, value):
    loc = glGetUniformLocation(shader, name)
    if loc == -1:
        print(f"[⚠ Shader Warning] Uniform '{name}' not found (float)")
    else:
        glUniform1f(loc, value)

def safe_uniform_vec3(shader, name, x, y, z):
    loc = glGetUniformLocation(shader, name)
    if loc == -1:
        print(f"[⚠ Shader Warning] Uniform '{name}' not found (vec3)")
    else:
        glUniform3f(loc, x, y, z)

def safe_uniform_mat4(shader, name, mat):
    loc = glGetUniformLocation(shader, name)
    if loc == -1:
        print(f"[⚠ Shader Warning] Uniform '{name}' not found (mat4)")
    else:
        glUniformMatrix4fv(loc, 1, GL_FALSE, mat.astype("float32"))

def load_texture(path, unit, shader_program, uniform_name):
    try:
        surface = pygame.image.load(path)
    except Exception as e:
        print(f"[🛑 Texture Error] Failed to load '{path}': {e}")
        return None

    try:
        image = pygame.image.tostring(surface, "RGB", True)
        width, height = surface.get_size()

        texture_id = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
        glGenerateMipmap(GL_TEXTURE_2D)

        loc = glGetUniformLocation(shader_program, uniform_name)
        if loc == -1:
            print(f"[⚠ Shader Warning] Sampler '{uniform_name}' not found in shader.")
        else:
            glUniform1i(loc, unit)

        return texture_id
    except Exception as e:
        print(f"[🛑 OpenGL Error] Could not bind texture '{path}': {e}")
        return None
