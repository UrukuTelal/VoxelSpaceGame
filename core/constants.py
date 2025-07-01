#contants.py

# --- Planet Origin Types ---
PLANET_ORIGIN_TYPES = {
    "_Terran_": {"liquid_cycle": "H2O", "atmosphere": ["N2","O2","CO2"], "energy_sources": ["stellar","geothermal","photosynthesis","AEtheric"], "common_life": ["carbon-based","plant-animal-fungal trios","aether-neutral species"]},
    # ... other types omitted for brevity
}

# --- Block & Light System ---

render_block_cache = {}

block_celestial_ids = {
    "_default_": 0,
    "_moon_": 1,
    "_star_": 2,
    "_planet_": 3,
    "_superPlanet_": 4,
    "_asteroid_": 5,
    "_ring_": 6
}

block_state_ids = {
    "_default_": 0,
    "_solid_": 1,
    "_molten_": 2,
    "_liquid_": 3,
    "_gaseous_": 4,
    "_plasma_": 5,
    "_particle_": 6,
    "_lightEmitter_": 6
}

#block_periodic_ids = {
    #periodic table, multiple block_substance_ids in a full id strip denotes material, 
    #ie _solid_hydrogen_hydrogen_carbon_ would be hydro-carbonic ice, change carbon to oxygen and its water.
    #"_iron_", "_nickel_", "_hydrogen_", "_helium_", "_oxygen_", "lead", "iron", "copper", "nitrogen", etc...
    #}

block_species_ids = {
"radiant_proto_motile", #not rendered for the most part bc of scale, these are microscopic
}

#block_organic_ids = {
            #idk yet, maybe different body parts/traits from the speciation tree
            #WIP a robust speciation tree, starting with radiant_proto_motile, ie feeds off radiation, 
            #could be light, could be particle decay
            
            #}
