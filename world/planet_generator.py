# planet_generator.py

import numpy as np
from core.planet_projection import local_grid_to_normalized_uv, project_cube_to_sphere
from world.block import Block
from core.block_registry import BLOCK_TYPES

def generate_sun_layers(
    radius=100.0,
    layers=[
        (4.0, 4),   # (block size, resolution per face side)
        (2.0, 8),
        (1.0, 16),
        (0.5, 32),
        (0.25, 64),
    ],
    block_type="_sun_molten_hydrogen_helium"
):
    """
    Generates a sun by layering concentric shells of blocks from large core to fine surface.
    
    radius: Total planet radius in world units.
    layers: List of (block_size, grid_resolution) tuples.
    block_type: Block type string to use (must be defined in BLOCK_TYPES).
    """

    blocks = []
    for block_size, resolution in layers:
        shell_radius = radius - (block_size * 0.5)

        for face_id in range(6):
            for x in range(resolution):
                for y in range(resolution):
                    u, v = local_grid_to_normalized_uv(x, y, resolution)
                    pos = project_cube_to_sphere(face_id, u, v, resolution, shell_radius)
                    blocks.append(Block(position=pos, block_type=block_type))

    return blocks

# Layer definitions for rock planets (inside-out)
LAYERS = [
    {"radius": 0.2, "block": "core_iron"},
    {"radius": 0.5, "block": "mantle_rock"},
    {"radius": 1.0, "block": "crust_stone"},
]

def get_block_for_radius(r_norm):
    """Pick block type based on normalized radius (0–1)."""
    for layer in LAYERS:
        if r_norm <= layer["radius"]:
            return layer["block"]
    return "default"

def generate_planet(radius=100.0, layers=LAYERS, chunk_manager=None):
    """
    Fill a spherical planet inside-out using ChunkManager.
    """
    from world.chunks import ChunkManager

    if chunk_manager is None:
        chunk_manager = ChunkManager()

    # Cube normalized step based on chunk size and planet radius
    step = chunk_manager.chunk_size / radius
    for x in np.arange(-1.0, 1.0, step):
        for y in np.arange(-1.0, 1.0, step):
            for z in np.arange(-1.0, 1.0, step):
                pos = np.array([x, y, z])
                dist = np.linalg.norm(pos)
                if dist > 1.0:
                    continue

                block_type = get_block_for_radius(dist)
                block = Block(position=pos * radius, block_type=block_type)
                chunk_manager.set_block_at(pos * radius, block)

    return chunk_manager

def sample_height_map(height_map_array, u, v):
    height_map_height, height_map_width = height_map_array.shape
    x = int(u * (height_map_width - 1))
    y = int(v * (height_map_height - 1))
    return height_map_array[y, x]  # grayscale between 0.0 and 1.0
height_scale = 3.0  # tweak this to control max displacement outward/inward

def adjust_radius(base_radius, height_value):
    # e.g., shift radius by height_value scaled
    return base_radius + (height_value - 0.5) * 2.0 * height_scale
