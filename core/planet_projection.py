# src/core/planet_projection.py
import numpy as np

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
    # face 0 (+Z)
    (0, '+x'): (4, False, False),  # right edge of face 0 goes to face 4
    (0, '-x'): (5, False, True),   # left edge of face 0 goes to face 5, flip y
    (0, '+y'): (2, False, False),  # top edge of face 0 goes to face 2
    (0, '-y'): (3, False, False),  # bottom edge of face 0 goes to face 3

    # face 1 (-Z)
    (1, '+x'): (5, False, False),
    (1, '-x'): (4, False, True),
    (1, '+y'): (2, False, True),
    (1, '-y'): (3, False, True),

    # face 2 (+Y)
    (2, '+x'): (4, True, False),
    (2, '-x'): (5, True, True),
    (2, '+y'): (1, False, False),
    (2, '-y'): (0, False, False),

    # face 3 (-Y)
    (3, '+x'): (4, False, False),
    (3, '-x'): (5, False, True),
    (3, '+y'): (0, False, False),
    (3, '-y'): (1, False, False),

    # face 4 (+X)
    (4, '+x'): (1, False, False),
    (4, '-x'): (0, False, True),
    (4, '+y'): (2, False, False),
    (4, '-y'): (3, True, False),

    # face 5 (-X)
    (5, '+x'): (0, False, False),
    (5, '-x'): (1, False


def cube_face_to_direction(face_id):
    """Returns the unit vector direction of each face center."""
    return {
        0: np.array([ 0,  0,  1]),  # +Z
        1: np.array([ 0,  0, -1]),  # -Z
        2: np.array([ 0,  1,  0]),  # +Y
        3: np.array([ 0, -1,  0]),  # -Y
        4: np.array([ 1,  0,  0]),  # +X
        5: np.array([-1,  0,  0]),  # -X
    }[face_id]

def project_cube_to_sphere(face_id, local_x, local_y, resolution=1.0, radius=1.0):
    """
    Maps 2D local face coordinates (from -1 to 1 range) to a 3D point on a sphere.
    This assumes faces are square and projected out.
    """
    # Local position on the face (plane)
    pos = np.array([local_x, local_y])

    # Start with cube face center
    face_dir = cube_face_to_direction(face_id)
    base = np.zeros(3)
    if face_id in [0, 1]:  # Z faces
        base = np.array([pos[0], pos[1], 0.0])
    elif face_id in [2, 3]:  # Y faces
        base = np.array([pos[0], 0.0, pos[1]])
    elif face_id in [4, 5]:  # X faces
        base = np.array([0.0, pos[0], pos[1]])

    if face_id in [1, 3, 5]:  # Negative axis
        base *= -1

    # Normalize to sphere
    sphere_pos = base / np.linalg.norm(base) * radius
    return sphere_pos

def local_grid_to_normalized_uv(x, y, resolution):
    """Converts grid coordinates to [-1, 1] range for projection."""
    u = (x + 0.5) / resolution * 2.0 - 1.0
    v = (y + 0.5) / resolution * 2.0 - 1.0
    return u, v
