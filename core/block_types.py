#block_types.py

def define_blocks(star_color_tex, star_gray_tex):
    # Define which block types are light emitters
    LIGHT_EMITTERS = set([
            "_sun_"
            "_star_"
            "_molten_",
            "_plasma_",
            "_lightEmitter_"
            
        ])        
        
    default_ambient_strength = 0.3 
    # --- Block Definition ---
    def define_block_type(
        name,
        color,
        tint,
        emissive,
        transparent=False,
        alpha=1.0,
        ambient_strength=default_ambient_strength,
        light_occlusion=1.0,
        reflectivity=0.0,
        textures=None
    ):
        BLOCK_TYPES[name] = {
            "block_type_id": block_state_ids.get(name, 0),
            "color": color,
            "tint": tint,
            "emissive": emissive,
            "alpha": alpha,
            "light_occlusion": light_occlusion,
            "ambient_strength": ambient_strength,
            "reflectivity": reflectivity,
            "is_emitter": name in LIGHT_EMITTERS or False,
            "textures": textures or {}
        }
        
   
# Copy to after initialization
# define_blocks()