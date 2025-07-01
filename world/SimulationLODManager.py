#SimulationLODManager.py

class SimulationLODManager:
    def __init__(self):
        self.current_tier = "space"  # could be 'space', 'orbital', 'atmo', 'surface'
    
    def update(self, player_position, camera_distance_to_planet):
        # Update tier based on distance thresholds
        if camera_distance_to_planet > 10000:
            self.current_tier = "space"
        elif camera_distance_to_planet > 5000:
            self.current_tier = "orbital"
        elif camera_distance_to_planet > 500:
            self.current_tier = "atmo"
        else:
            self.current_tier = "surface"
