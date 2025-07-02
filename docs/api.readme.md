| Module                | Function/Class                                                | Description                                                                             |
| --------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `block.py`            | `Block`                                                       | Represents a single world block with rendering and lighting properties.                 |
| `block.py`            | `Block.SubBlock`                                              | Optional micro-structure within a Block, defined by local position and size.            |
| `block.py`            | `ParticleBlock`                                               | A block subclass with velocity and attractor logic for physics-based updates.           |
| `block.py`            | `block_lookup_func(start, end, blocks, step)`             | Casts a ray and returns all blocks intersected by it. Used for occlusion/light tracing. |
| `block.py`            | `get_render_block(block, uv_scale=1.0)`                       | Returns a `RenderBlock` VAO-ready version of a `Block`.                                 |
| `geometry.py`         | `generate_cube(uv_scale)`                                     | Generates vertices and indices for a cube mesh with scaled UVs.                         |
| `geometry.py`         | `create_vao(vertices, indices)`                               | Builds and returns a VAO, VBO, and EBO from geometry data.                              |
| `geometry.py`         | `get_sphere_uv(pos)`                                          | Returns spherical UV coordinates for a 3D position.                                     |
| `lighting.py`         | `compute_light_falloff(intensity, distance)`                  | Calculates light intensity falloff based on distance.                                   |
| `lighting.py`         | `block_is_emitter(block_type)`                                | Returns True if the block type emits light.                                             |
| `lighting.py`         | `block_emission_strength(block_type)`                         | Returns emissive strength for a given block type.                                       |
| `lighting.py`         | `calculate_emission_from_nearby_emitters(block, blocks)`  | Sums emissive light contribution from nearby emitters.                                  |
| `lighting.py`         | `is_occluded(source, target, path_blocks)`                    | Determines if target is occluded by blocks along the path.                              |
| `lighting.py`         | `compute_received_light(target_block, emitters, lookup_func)` | Computes total light at target from emitters using ray checks and scattering.           |
| `utility_belt.py`     | `snap_to_grid(local_pos, snap_size)`                          | Snaps a position to grid space, useful for voxel alignment.                             |
| `shader.py`           | `load_shader(vertex_path, fragment_path)`                     | Loads, compiles, and links a shader program from file paths.                            |
| `planet_generator.py` | `generate_sun_layers(radius, layers, block_type)`             | Generates a sun-like shell of layered blocks using cube-to-sphere projection.           |
| `planet_generator.py` | `sample_height_map(height_map_array, u, v)`                   | Samples a heightmap image at normalized UV coordinates.                                 |
| `planet_generator.py` | `adjust_radius(base_radius, height_value)`                    | Alters radius based on heightmap displacement.                                          |
