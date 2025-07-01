# src/core/planet_projection.py
import numpy as np

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
