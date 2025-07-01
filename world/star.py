#star.py
import random

class Star:
    def __init__(self, name):
        self.name = name
        self.spectral_type = self.generate_spectral_type()
        self.temperature = self.get_temperature(self.spectral_type)
        self.radius = self.get_radius(self.spectral_type)
        self.luminosity = self.get_luminosity(self.spectral_type)
        self.color = self.get_color(self.temperature)
        # Position would be assigned externally in cluster/grid system

    def generate_spectral_type(self):
        # Weighted chance for types, more M-type stars etc.
        types = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
        weights = [0.00003, 0.0013, 0.006, 0.03, 0.076, 0.12, 0.76]
        return random.choices(types, weights)[0]

    def get_temperature(self, spectral_type):
        ranges = {
            'O': (30000, 50000),
            'B': (10000, 30000),
            'A': (7500, 10000),
            'F': (6000, 7500),
            'G': (5200, 6000),
            'K': (3700, 5200),
            'M': (2400, 3700),
        }
        return random.uniform(*ranges[spectral_type])

    def get_radius(self, spectral_type):
        # Radii in solar radii units (approximate)
        radius_ranges = {
            'O': (6.6, 10),
            'B': (1.8, 6.6),
            'A': (1.4, 1.8),
            'F': (1.15, 1.4),
            'G': (0.96, 1.15),
            'K': (0.7, 0.96),
            'M': (0.1, 0.7),
        }
        return random.uniform(*radius_ranges[spectral_type])

    def get_luminosity(self, spectral_type):
        # Approximate luminosity in solar units
        luminosity_ranges = {
            'O': (30000, 1000000),
            'B': (25, 30000),
            'A': (5, 25),
            'F': (1.5, 5),
            'G': (0.6, 1.5),
            'K': (0.08, 0.6),
            'M': (0.0001, 0.08),
        }
        return random.uniform(*luminosity_ranges[spectral_type])

    def get_color(self, temperature):
        # Simple blackbody approximation to RGB (placeholder)
        # Could be replaced with a better color mapping later
        if temperature > 10000:
            return (173, 216, 230)  # light blue
        elif temperature > 6000:
            return (255, 255, 224)  # light yellow
        elif temperature > 3700:
            return (255, 228, 181)  # moccasin
        else:
            return (255, 140, 0)    # dark orange
