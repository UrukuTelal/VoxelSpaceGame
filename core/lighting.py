#lighting.py
from core.block_registry import BLOCK_TYPES
import numpy as np
from world.block import *

def apply_atmospheric_scattering(target_block, sun_position, scattering_strength=0.4):
    direction = sun_position - target_block.position
    direction /= np.linalg.norm(direction)

    up_vector = target_block.position / np.linalg.norm(target_block.position)
    dot = np.dot(direction, up_vector)

    # dot=1 means sun directly overhead (min scattering), dot=0 means sun at horizon (max scattering)
    scattering_factor = 1.0 - scattering_strength * (1.0 - dot**2)
    return max(scattering_factor, 0.0)


def compute_light_falloff(intensity,distance): return intensity/(distance*distance+1.0)

def block_is_emitter(block_type):
    return BLOCK_TYPES.get(block_type, {}).get("is_emitter", False)

def block_emission_strength(block_type):
    return BLOCK_TYPES.get(block_type, {}).get("emissive", 0.0)

def calculate_emission_from_nearby_emitters(block, blocks, max_distance=20.0):
    total_emission = block.base_emissive
    for other in blocks:
        if other is block:
            continue
        if not block_is_emitter(other.block_type):
            continue

        direction = block.position - other.position
        distance = np.linalg.norm(direction)
        if distance > max_distance:
            continue

        # Optional: Add a line-of-sight check here

        falloff = 1.0 / (distance**2 + 1e-6)
        total_emission += other.base_emissive * falloff

    return total_emission

def is_occluded(src,tgt,path): 
        oc=0.0
        for b in path:
            p = BLOCK_TYPES.get(b.block_type,{});
            if p.get("is_emitter"): continue
            oc+=p.get("partial_occlusion",1.0)
            if oc>=1.0: return True
        return False

def compute_light_falloff(intensity, distance):
    return intensity / (distance * distance + 1.0)

def compute_received_light(target_block, emitters, block_lookup_func):
   
    total_light = 0.0
    for e in emitters:
        distance = np.linalg.norm(target_block.position - e.position)
        intensity = compute_light_falloff(BLOCK_TYPES[e.block_type]['emissive'], distance)

        if not BLOCK_TYPES[e.block_type].get("is_emitter", False):
            path_blocks = block_lookup_func(e.position, target_block.position)
            if is_occluded(e.position, target_block.position, path_blocks):
                continue

            scattering = apply_atmospheric_scattering(target_block, e.position)
            intensity *= scattering  # Apply scattering to non-emitters only
        if not BLOCK_TYPES[e.block_type].get("is_emitter", False):
            path_blocks = block_lookup_func(e.position, target_block.position)
            if is_occluded(e.position, target_block.position, path_blocks):
                continue

            scattering = apply_atmospheric_scattering(target_block, e.position)
            intensity *= scattering  # Apply scattering to non-emitters only
        
        scattering = apply_atmospheric_scattering(target_block, e.position)
        total_light += intensity * scattering