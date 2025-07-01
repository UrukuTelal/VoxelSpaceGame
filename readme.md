 Next Steps: What I Recommend Building First
Spherical projection logic

Map cube faces to spherical shell

Let’s build the math for that cleanly

Face & Block index system

Face[6] -> Grid[x][y][z] -> Block

With edge continuity between faces

Planet prototype builder

generate_planet(radius, layers, core_scale)

Builds inside-out: large to small blocks

Player gravity/orientation logic

Local gravity vector based on current position

LODs & Lazy Loading (later)

Procedural generation with per-block metadata for climate, evolution, etc.

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
