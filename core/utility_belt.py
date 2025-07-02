#utility_belt.py
import numpy as np

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