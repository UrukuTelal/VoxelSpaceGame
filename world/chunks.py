# chunks.py

from collections import defaultdict
import numpy as np
from world.block import Block
from core.coordinates import world_to_face_grid_cell

# --- Constants ---

CHUNK_GRID_SIZE = 8  # Or however many blocks per side per chunk

# --- Face adjacency map ---
# At top of chunks.py, define cube face adjacency with flipping info
# Format: (face_id, direction) -> (neighbor_face_id, flip_x, flip_y)
# direction: one of '+x', '-x', '+y', '-y'

# Face ID legend:
# 0: +Z, 1: -Z, 2: +Y, 3: -Y, 4: +X, 5: -X

# Maps (face, direction) → (adjacent_face, axis_remap, flip_x, flip_y)
# direction: (dx, dy) from grid movement

# Each key: (face_id, edge_direction)
# edge_direction is one of: '+x', '-x', '+y', '-y'  (cube face local edges)
# Value: (neighbor_face_id, flip_x: bool, flip_y: bool)

# flip_x and flip_y indicate whether to invert the local coordinate axis when crossing the edge.
# This depends on how the faces align on the cube.
FACE_NEIGHBORS = {
    (0, '+x'): (4, False, False),
    (0, '-x'): (5, True, False),
    (0, '+y'): (2, False, False),
    (0, '-y'): (3, False, True),

    (1, '+x'): (5, False, False),
    (1, '-x'): (4, True, False),
    (1, '+y'): (2, False, True),
    (1, '-y'): (3, False, False),

    (2, '+x'): (4, False, True),
    (2, '-x'): (5, False, False),
    (2, '+y'): (1, False, False),
    (2, '-y'): (0, False, False),

    (3, '+x'): (4, False, False),
    (3, '-x'): (5, False, True),
    (3, '+y'): (0, False, True),
    (3, '-y'): (1, False, False),

    (4, '+x'): (1, False, False),
    (4, '-x'): (0, False, False),
    (4, '+y'): (2, True, False),
    (4, '-y'): (3, True, True),

    (5, '+x'): (0, True, False),
    (5, '-x'): (1, False, False),
    (5, '+y'): (2, False, False),
    (5, '-y'): (3, False, True),
}

def get_neighbor_coords(face_id, x, y, z, dx, dy, dz):
    new_x, new_y, new_z = x + dx, y + dy, z + dz

    if 0 <= new_x < CHUNK_GRID_SIZE and 0 <= new_y < CHUNK_GRID_SIZE:
        return face_id, new_x, new_y, new_z

    # Crossing face edge: determine which edge was crossed
    if new_x < 0:
        edge = '-x'
    elif new_x >= CHUNK_GRID_SIZE:
        edge = '+x'
    elif new_y < 0:
        edge = '-y'
    elif new_y >= CHUNK_GRID_SIZE:
        edge = '+y'
    else:
        return None  # no crossing

    key = (face_id, edge)
    if key not in FACE_NEIGHBORS:
        return None  # fallback

    neighbor_face, flip_x, flip_y = FACE_NEIGHBORS[key]

    # Wrap coordinates inside grid size
    new_x %= CHUNK_GRID_SIZE
    new_y %= CHUNK_GRID_SIZE

    if flip_x:
        new_x = CHUNK_GRID_SIZE - 1 - new_x
    if flip_y:
        new_y = CHUNK_GRID_SIZE - 1 - new_y

    return neighbor_face, new_x, new_y, new_z




class Chunk:
    def __init__(self, face_id, x, y, z, size=8):
        self.face_id = face_id
        self.x = x
        self.y = y
        self.z = z
        self.size = size  # width/height/depth
        self.blocks = np.empty((size, size, size), dtype=object)
        self.generated = False
        self.lod_level = 0

    def set_block(self, lx, ly, lz, block):
        self.blocks[lx, ly, lz] = block

    def get_block(self, lx, ly, lz):
        return self.blocks[lx, ly, lz]

    def is_inside(self, lx, ly, lz):
        return 0 <= lx < self.size and 0 <= ly < self.size and 0 <= lz < self.size

    def generate(self, lod_level=0):
            self.lod_level = lod_level
            # Call procedural terrain generator here
            self.generated = True

class ChunkManager:
    def __init__(self, chunk_size=8):
        self.chunk_size = chunk_size
        self.chunks = defaultdict(dict)  # {face_id: {(x,y,z): Chunk}}
        self.loaded_chunk_keys = set()

    def get_chunk_coords(self, world_pos):
        face_id, gx, gy, gz = world_to_face_grid_cell(world_pos)
        cx = gx // self.chunk_size
        cy = gy // self.chunk_size
        cz = gz // self.chunk_size
        return face_id, cx, cy, cz

    def get_chunk(self, world_pos):
        face_id, cx, cy, cz = self.get_chunk_coords(world_pos)
        key = (cx, cy, cz)
        if key not in self.chunks[face_id]:
            self.chunks[face_id][key] = Chunk(face_id, cx, cy, cz, self.chunk_size)
        return self.chunks[face_id][key]

    def get_chunk_at(self, world_pos):
        face, x, y, z = world_to_face_grid_cell(world_pos)
        return self.chunks.get(face, {}).get((x, y, z), None)

    def set_block_at(self, world_pos, block):
        face_id, gx, gy, gz = world_to_face_grid_cell(world_pos)
        chunk = self.get_chunk(world_pos)
        lx = gx % self.chunk_size
        ly = gy % self.chunk_size
        lz = gz % self.chunk_size
        chunk.set_block(lx, ly, lz, block)

    def get_block_at(self, world_pos):
        face_id, gx, gy, gz = world_to_face_grid_cell(world_pos)
        chunk = self.get_chunk(world_pos)
        lx = gx % self.chunk_size
        ly = gy % self.chunk_size
        lz = gz % self.chunk_size
        return chunk.get_block(lx, ly, lz)

    def update_loaded_chunks(self, player_pos, player_altitude):
        radius = get_contextual_load_radius(player_altitude)
        face_id, cx, cy, cz = self.get_chunk_coords(player_pos)

        new_keys = set()
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    key = (face_id, cx + dx, cy + dy, cz + dz)
                    new_keys.add(key)
                    if key not in self.chunks[face_id]:
                        self.chunks[face_id][(cx + dx, cy + dy, cz + dz)] = Chunk(face_id, cx + dx, cy + dy, cz + dz, self.chunk_size)
                
                    chunk = self.chunks[face_id][(cx + dx, cy + dy, cz + dz)]

                    if not chunk.generated:
                        lod = compute_lod(chunk, player_pos)
                        chunk.generate(lod_level=lod)

        # Unload chunks after loading all necessary chunks
        keys_to_unload = self.loaded_chunk_keys - new_keys
        for key in keys_to_unload:
            face, x, y, z = key
            if face in self.chunks and (x, y, z) in self.chunks[face]:
                del self.chunks[face][(x, y, z)]
                if not self.chunks[face]:
                    del self.chunks[face]

        self.loaded_chunk_keys = new_keys          

