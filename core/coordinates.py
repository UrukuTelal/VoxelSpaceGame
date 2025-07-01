# coordinates.py

import numpy as np
from collections import defaultdict


def gravity_vector_at(pos, center=np.zeros(3)):
    direction = center - np.array(pos)
    norm = np.linalg.norm(direction)
    if norm == 0:
        return np.array([0.0, -1.0, 0.0])  # fallback gravity direction
    return direction / norm


def get_adjacent_face(face_id, direction):
    """
    Given a face and direction (+x, -x, +y, -y), return adjacent face and transform logic.
    For now this is a placeholder.
    """
    # This table maps [face][direction] -> (neighbor_face_id, rotation)
    # You’ll need to define this properly later
    face_neighbors = {
        0: {'+x': 4, '-x': 5, '+y': 2, '-y': 3},
        1: {'+x': 5, '-x': 4, '+y': 2, '-y': 3},
        2: {'+x': 4, '-x': 5, '+y': 1, '-y': 0},
        3: {'+x': 4, '-x': 5, '+y': 0, '-y': 1},
        4: {'+x': 1, '-x': 0, '+y': 2, '-y': 3},
        5: {'+x': 0, '-x': 1, '+y': 2, '-y': 3},
    }
    return face_neighbors[face_id][direction]

def align_up_to_gravity(matrix, gravity_vec):
    """
    Given a model matrix and gravity vector, reorients the object to align its 'up' with gravity.
    This rotates the object so that its local +Y is opposite to gravity.
    """
    up = -gravity_vec  # opposite of gravity
    forward = np.array([0, 0, 1], dtype=np.float32)

    if np.allclose(up, forward):
        forward = np.array([0, 1, 0])  # avoid gimbal lock

    right = np.cross(up, forward)
    right /= np.linalg.norm(right)
    forward = np.cross(right, up)
    forward /= np.linalg.norm(forward)

    orientation = np.eye(4, dtype=np.float32)
    orientation[:3, 0] = right
    orientation[:3, 1] = up
    orientation[:3, 2] = forward

    return orientation

def world_to_face_grid_cell(pos: np.ndarray):
    """
    Placeholder. Implement proper cube face projection reverse-mapping.
    Should return: face_id, x, y, z
    """
    face_id = 0  # dummy
    x = int(pos[0])  # dummy
    y = int(pos[1])  # dummy
    z = int(pos[2])  # dummy
    return face_id, x, y, z

def snap_to_grid(local_pos, snap_size):
    snapped = np.round(np.array(local_pos) / snap_size) * snap_size
    return np.clip(snapped, 0.0, 1.0 - snap_size)

def world_to_face_grid(pos, radius, resolution_per_face):
    """
    Given a world position, determine the cube face it's closest to and its grid coordinates.
    Assumes the world is projected from a cube sphere.
    """
    norm_pos = pos / np.linalg.norm(pos)
    abs_pos = np.abs(norm_pos)
    major_axis = np.argmax(abs_pos)

    if major_axis == 0:  # X
        face_id = 4 if norm_pos[0] > 0 else 5
    elif major_axis == 1:  # Y
        face_id = 2 if norm_pos[1] > 0 else 3
    else:  # Z
        face_id = 0 if norm_pos[2] > 0 else 1

    local_dir = norm_pos / abs_pos[major_axis]
    face_x, face_y = {
        0: ( local_dir[0], local_dir[1]),
        1: (-local_dir[0], local_dir[1]),
        2: ( local_dir[0],-local_dir[2]),
        3: ( local_dir[0], local_dir[2]),
        4: (-local_dir[2], local_dir[1]),
        5: ( local_dir[2], local_dir[1])
    }[face_id]

    grid_x = int(((face_x + 1) / 2.0) * resolution_per_face)
    grid_y = int(((face_y + 1) / 2.0) * resolution_per_face)

    return face_id, grid_x, grid_y

def get_contextual_load_radius(player_altitude):
    if player_altitude > 5000:
        return 3  # orbit
    elif player_altitude > 1000:
        return 6  # atmo
    else:
        return 12  # ground

