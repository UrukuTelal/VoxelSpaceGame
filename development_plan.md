✅ Core World Architecture
✅ Spherical projection logic

Your planet_projection.py and world_to_face_grid handle cube-to-sphere math.

✅ Map cube faces to spherical shell

Done through face ID logic in coordinates.py + grid mapping.

✅ Let’s build the math for that cleanly

The math is modular and cleanly abstracted in coordinates.py and planet_projection.py.

✅ Spatial Grid & Block System
✅ Face & Block index system

Implemented with face_id → (x, y, z) logic and world_to_face_grid_cell.

✅ Face[6] → Grid[x][y][z] → Block

chunks.py maps face IDs to block chunks with chunk-local (lx, ly, lz) lookups.

✅ With edge continuity between faces

FACE_NEIGHBORS + get_neighbor_coords() in chunks.py correctly wraps edge lookups across cube faces.

🧱 Planet Construction (In Progress)
🔲 Planet prototype builder

❌ generate_planet(radius, layers, core_scale) stub not yet implemented.

Planned: iteratively fill concentric layers using face/grid logic.

🔲 Builds inside-out: large to small blocks

Not done yet, but logic should go inside planet_generator.py.

🧍 Player Gravity & Orientation
✅ Player gravity/orientation logic

gravity_vector_at() + align_up_to_gravity() in coordinates.py covers this well.

✅ Local gravity vector based on current position

Covered by gravity_vector_at() with world center assumed as source.

🧠 Optimization & World Generation (Upcoming)
🔲 LODs & Lazy Loading (later)

✅ LOD hook exists in chunk generation

❌ Actual compute_lod() implementation pending

❌ No in-engine chunk mesh LOD switching yet

🔲 Procedural generation with per-block metadata for climate, evolution, etc.

❌ Placeholder in chunk.generate()

❌ Climate/evolution metadata not implemented



src/
│
│
├── assets/     
│   ├── 2k_sun_color.jpg - whites, yellows, reds, actual colormap of the sun
│   ├── 2k_sun_color_inverted.jpg - inverted color, so blues
│   └── 2k_sun_grayscale.jpg
│
├── core/
│   ├── planet_projection.py      ← Sphere math, cube face projection, face adjacency
│   ├── coordinates.py            ← Position -> face/grid/voxel conversions, gravity vector
│   ├── block_types.py            ← BLOCK_TYPES, define_all_blocks, IDs
│   ├── voxel_math.py             ← Helpers like snap_to_grid, direction vecs, face normals
│   ├── constants.py
│   └── block_types.py_
│
├── world/
│   ├── block.py                  ← Block, SubBlock, ParticleBlock
│   ├── chunks.py                  ← Future: Handles chunk loading/unloading
│   ├── planet_generator.py       ← Builds a sun/planet inside-out using projection
│
├── rendering/
│   ├── shaders/
│   │   ├── cube.vert
│   │   └── cube.frag
│   ├── rendering.py              ← create_vao, draw logic
│   └── texture_loader.py         ← Loads & binds textures
│
└── main.py                       ← Entry point (e.g. create Sun test, render loop)
