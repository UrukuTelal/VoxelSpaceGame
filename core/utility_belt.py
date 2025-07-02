#utility_belt.py
import numpy as np
import pygame

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