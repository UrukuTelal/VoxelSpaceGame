# lighting.py
import numpy as np
from core.block_registry import BLOCK_TYPES
from world.block import *
from tqdm import tqdm

# Constants for physical lighting
PLANCK_CONSTANT = 6.62607015e-34
BOLTZMANN_CONSTANT = 1.380649e-23
SPEED_OF_LIGHT = 2.99792458e8


def compute_light_falloff(intensity, distance):
    return intensity / (distance * distance + 1.0)


def block_is_emitter(block_type):
    return BLOCK_TYPES.get(block_type, {}).get("is_emitter", False)


def block_emission_strength(block_type):
    return BLOCK_TYPES.get(block_type, {}).get("emissive", 0.0)


def block_temperature(block_type):
    return BLOCK_TYPES.get(block_type, {}).get("temperature", 5800.0)


def is_occluded(src, tgt, path):
    occlusion = 0.0
    for b in path:
        props = BLOCK_TYPES.get(b.block_type, {})
        # Sun blocks are fully transparent for occlusion
        if props.get("is_emitter") and b.block_type.startswith("_sun_"):
            continue
        if props.get("is_emitter"):
            continue
        occlusion += props.get("partial_occlusion", 1.0)
        if occlusion >= 1.0:
            return True
    return False


def apply_atmospheric_scattering(target_block, sun_position):
    direction = np.array(sun_position) - np.array(target_block.position)
    norm = np.linalg.norm(direction)

    if norm < 1e-6:
        return 0.0

    direction /= norm
    view_dir = -direction
    dot = np.dot(view_dir, np.array([0.0, 1.0, 0.0]))
    scattering_intensity = max(0.0, dot) ** 2.0  # tweak exponent for effect
    return scattering_intensity


def compute_blackbody_emission(temp_k):
    """Approximate RGB from blackbody temperature in Kelvin"""
    t = temp_k / 100.0
    if t <= 66:
        red = 255
        green = 99.47 * np.log(t) - 161.12 if t > 0 else 0
        blue = 0 if t <= 19 else 138.52 * np.log(t - 10) - 305.04
    else:
        red = 329.7 * ((t - 60) ** -0.133204)
        green = 288.1 * ((t - 60) ** -0.0755148)
        blue = 255
    return np.clip([red, green, blue], 0, 255) / 255.0


def compute_directional_emission_factor(direction, normal, cone_angle_deg=30):
    dir_norm = direction / (np.linalg.norm(direction) + 1e-6)
    norm = normal / (np.linalg.norm(normal) + 1e-6)
    dot = np.dot(dir_norm, norm)
    angle = np.arccos(np.clip(dot, -1.0, 1.0)) * 180 / np.pi
    if angle < cone_angle_deg:
        return 1.0 - (angle / cone_angle_deg)
    return 0.0


def compute_per_face_occlusion(target_block, blocks):
    """Return a dict per face (e.g., +X, -X, +Y, -Y, +Z, -Z) with occlusion"""
    offsets = {
        "+X": [1, 0, 0], "-X": [-1, 0, 0],
        "+Y": [0, 1, 0], "-Y": [0, -1, 0],
        "+Z": [0, 0, 1], "-Z": [0, 0, -1],
    }
    occlusion = {}
    for face, offset in offsets.items():
        check_pos = np.array(target_block.position) + offset
        blocked = any(np.allclose(check_pos, b.position) for b in blocks)
        occlusion[face] = 1.0 if blocked else 0.0
    return occlusion


def compute_received_light(target_block, emitters, block_lookup_func):
    # If the block itself is a sun block, it is a pure emitter:
    if block_is_emitter(target_block.block_type) and target_block.block_type.startswith("_sun_"):
        # Return full emissive strength, no occlusion or scattering applied
        return block_emission_strength(target_block.block_type)

    total_light = 0.0
    pos = target_block.np_position

    # Per-face occlusion could be used for AO or directional lighting if desired
    per_face_occlusion = compute_per_face_occlusion(target_block, emitters)

    # Iterate with tqdm for progress visibility
    for e in tqdm(emitters, desc=f"Calculating light for block at {target_block.position}"):
        emitter_props = BLOCK_TYPES.get(e.block_type, {})

        # Sun blocks are fully transparent for occlusion checks:
        if block_is_emitter(e.block_type) and e.block_type.startswith("_sun_"):
            # No occlusion check needed for sun blocks (light passes through)
            pass
        else:
            # For other emitters, do occlusion check
            path_blocks = block_lookup_func(e.position, target_block.position)
            if is_occluded(e.position, target_block.position, path_blocks):
                continue

        emitter_pos = np.array(e.position)
        direction = pos - emitter_pos
        distance = np.linalg.norm(direction)
        emission = block_emission_strength(e.block_type)
        temp = block_temperature(e.block_type)
        emission_rgb = compute_blackbody_emission(temp)

        intensity = compute_light_falloff(emission, distance)
        scatter = apply_atmospheric_scattering(target_block, e.position)
        beam = compute_directional_emission_factor(direction, target_block.np_position)

        total_light += intensity * scatter * beam

    return total_light
