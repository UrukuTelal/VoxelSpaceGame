 #block_registry.py

# block_registry.py

BLOCK_TYPES = {
    "_default_": {
        "color": [1.0, 1.0, 1.0],
        "tint": [1.0, 1.0, 1.0],
        "emissive": 0.0,
        "alpha": 1.0,
        "ambient_strength": 0.3,
        "textures": {},
        "is_emitter": False,
        "partial_occlusion": 1.0,
    },
    "_sun_molten_hydrogen_helium": {
        "color": [1.0, 0.8, 0.4],
        "emissive": 10.0,
        "alpha" : 0.1,
        "is_emitter": True,
        "partial_occlusion": 0.0,
    },
   
    }
    # ... add others here



    