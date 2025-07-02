# planet_generator.py
import math
import numpy as np
from core.planet_projection import local_grid_to_normalized_uv, project_cube_to_sphere
from world.block import Block
from core.block_registry import BLOCK_TYPES
from tqdm import tqdm
from rendering.geometry import *

def generate_sun_layers(
    radius=100.0,
    layers=[
        (4.0, 4),   # (block size, resolution per face side)
        (2.0, 8),
        (1.0, 16),
        (0.5, 32),
        (0.25, 64),
    ],
    block_type="_sun_molten_hydrogen_helium",
    block_size =5.0,
):
    """
    Generates a sun by layering concentric shells of blocks from large core to fine surface.
    """
    blocks = []
    
    total_steps = sum(6 * res * res for _, res in layers)  # total iterations for progress bar
    pbar = tqdm(total=total_steps, desc="Generating Sun")

    for block_size, resolution in layers:
        shell_radius = radius - (block_size * 0.5)

        for face_id in range(6):
            for x in range(resolution):
                for y in range(resolution):
                    u, v = local_grid_to_normalized_uv(x, y, resolution)
                    pos = project_cube_to_sphere(face_id, u, v, resolution, shell_radius)
                    blocks.append(Block(position=pos, block_type=block_type))
                    pbar.update(1)

    pbar.close()
    return blocks


# Layer definitions for rock planets (inside-out)
LAYERS = [
    {"radius": 0.2, "block": "core_iron"},
    {"radius": 0.5, "block": "mantle_rock"},
    {"radius": 1.0, "block": "crust_stone"},
]

def get_block_for_radius(r_norm):
    """Pick block type based on normalized radius (0-1)."""
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

def generate_spherical_blocks(
    radius=32.0,
    block_scale=1.0,
    grid_resolution=96,
    height_map=None,
    height_scale=0.1,
    layer_definitions=None
):
    """
    Generate a sphere with snapping and radial block type layering.

    layer_definitions: list of (inner_radius_ratio, block_type) sorted outside-in
        e.g., [(0.66, "_sun_atmo"), (0.33, "_sun_shell"), (0.0, "_sun_core")]

    Default behavior is a full sphere with a single layer using "_sun_molten_hydrogen_helium"
    """

    if layer_definitions is None:
        # Default: full sphere, all blocks the same type
        layer_definitions = [(0.0, "_sun_molten_hydrogen_helium")]

    blocks = []

    step_theta = math.pi / grid_resolution
    step_phi = 2 * math.pi / grid_resolution

    if height_map is not None:
        height_h, height_w = height_map.shape

        def sample_height(u, v):
            u_clamped = max(0.0, min(1.0, u))
            v_clamped = max(0.0, min(1.0, v))
            i = int(u_clamped * (height_w - 1))
            j = int(v_clamped * (height_h - 1))
            return height_map[j, i]
    else:
        sample_height = lambda u, v: 0.5  # flat displacement

    for theta in tqdm(np.arange(0, math.pi + step_theta * 0.5, step_theta), desc="[Spherical] Generating layers"):
        for phi in np.arange(0, 2 * math.pi + step_phi * 0.5, step_phi):
            u = phi / (2 * math.pi)
            v = theta / math.pi
            displace = (sample_height(u, v) - 0.5) * 2.0 * height_scale
            r = radius + displace

            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.cos(theta)
            z = r * math.sin(theta) * math.sin(phi)

            snapped_pos = block_scale * np.round(np.array([x, y, z]) / block_scale)
            dist = np.linalg.norm(snapped_pos)

            for ratio, block_type in layer_definitions:
                if dist >= radius * ratio:
                    blocks.append(Block(position=snapped_pos.tolist(), block_type=block_type, scale=block_scale))
                    break

    instance_data = np.array([b.position for b in blocks], dtype=np.float32)
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

    index_count = len(indices)
    instance_count = len(blocks)

    return vao, index_count, instance_count, blocks
