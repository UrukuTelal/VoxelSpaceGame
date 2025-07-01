#utility_belt.py
def snap_to_grid(local_pos, snap_size):
    snapped = np.round(np.array(local_pos) / snap_size) * snap_size
    return np.clip(snapped, 0.0, 1.0 - snap_size)