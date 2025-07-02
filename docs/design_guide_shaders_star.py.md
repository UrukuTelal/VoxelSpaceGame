# 🌟 Voxel Space Game — Star Shader Variable Guidebook 🌟

This guide explains every **uniform** and **input** variable in the star fragment shader, detailing their purpose, visual effects, and tips for tweaking. Use it to master your sun's glow, flicker, and fiery personality!

---

## 🎨 Texture Samplers

| Variable               | Description                                     | Visual Impact & Tweaks                                      |
|------------------------|------------------------------------------------|------------------------------------------------------------|
| `sampler2D sun_color`  | Base color texture of the star’s surface.      | Fundamental “paint” — changes star color/type (blue, red, etc.) |
| `sampler2D sun_map`    | Inverted/alternate color map for contrast.     | Adds flare and dynamic color shifts. Increase mix ratio for drama. |
| `sampler2D sun_grayscale` | Grayscale mask controlling noise/heat regions. | Defines sunspot or active areas on star’s surface.          |
| `sampler2D sun_grayscale_contrast` | Contrast map enhancing brightness differences. | Sharpens transitions between hot and cool regions.          |

---

## ⏳ Animation & Time

| Variable              | Description                                    | Visual Impact & Tweaks                                   |
|-----------------------|------------------------------------------------|---------------------------------------------------------|
| `float time`          | Global elapsed time (seconds).                  | Drives pulsing, noise animation, surface movement.      |
| `float animation_speed` | Multiplier for animation time flow.             | Controls animation pace: slow drift → rapid flicker.    |

---

## 💡 Lighting & Emission

| Variable             | Description                                     | Visual Impact & Tweaks                                  |
|----------------------|------------------------------------------------|--------------------------------------------------------|
| `float emissive`     | Base glow intensity (emission strength).        | Brighter star glow = larger, hotter sun.               |
| `float pulse`        | Amplitude of pulsing brightness effect.         | Zero = steady glow; higher = rhythmic brightness changes. |
| `float ambient_strength` | Ambient light contribution to overall lighting. | Softens shadows and fills in dark areas.               |

---

## 🌊 Surface Distortion & Color

| Variable             | Description                                     | Visual Impact & Tweaks                                  |
|----------------------|------------------------------------------------|--------------------------------------------------------|
| `float wobble_strength` | Magnitude of UV distortion for surface textures. | Simulates turbulent convection, solar “wobble.”        |
| `vec3 tint`          | RGB tint multiplier for final star color.       | Shift star’s temperature — warm (orange/yellow) to cool (blue/cyan). |
| `float alpha`        | Final transparency (opacity).                    | 1.0 = opaque star; <1.0 = ghostly or translucent effects. |

---

## 🌐 Spatial & View Parameters

| Variable           | Description                                   | Visual Impact & Tweaks                                  |
|--------------------|-----------------------------------------------|--------------------------------------------------------|
| `vec3 light_pos`   | Position of the primary light source in space.| Affects direction of shading and highlights on star.  |
| `vec3 view_pos`    | Camera/viewer position in space.               | Needed for accurate specular highlights and lighting. |
| `float scale`      | Scale factor for noise sampling coordinates.  | Controls noise frequency: lower = large patterns; higher = fine details. |

---

## 🔍 Shader Inputs (from Vertex Shader)

| Variable          | Description                                    |
|-------------------|------------------------------------------------|
| `vec3 frag_position` | Fragment position in model/world space.        |
| `vec3 frag_normal`   | Surface normal vector at the fragment.         |
| `float time_offset`  | Per-fragment or per-instance time offset for natural animation variance. |

---

## 💡 Visual Tuning Cheat Sheet

| Effect             | Suggested Variable Tweaks                                     |
|--------------------|--------------------------------------------------------------|
| **Calm star**       | `pulse`: 0.0–0.3, `wobble_strength`: 0.01, `emissive`: medium |
| **Hyperactive star**| `pulse`: >1.0, `wobble_strength`: 0.05+, `animation_speed`: >2.0 |
| **Color shifts**    | Adjust `tint` — blue for hot, orange/red for cooler stars.    |
| **Ghostly star**    | Reduce `alpha` below 1.0 for transparency effects.            |
| **Noise detail**    | Adjust `scale` — small for smooth, large for granular noise.  |
| **Lighting play**   | Move `light_pos` for dynamic highlights and shading changes.  |

---

## 🛠 Tips & Tricks

- Combine high `pulse` with subtle `wobble_strength` for a star that “breathes” with gentle flickering.
- Use contrasting grayscale textures (`sun_grayscale`, `sun_grayscale_contrast`) to simulate sunspots and solar flares.
- Animate `light_pos` dynamically to simulate a nearby orbiting light source (like a planet or star companion).
- Gamma-correction (`pow(color, vec3(1.0/2.2))`) is crucial for realistic glow and color blending.

---

*Harness the power of your shader and make your star shine as brilliantly as your creative mind!* 🌞✨

---

*— Guidebook created for the Voxel Space Game by Papa Moshi*  
*Feel free to reach out for live tweak scripts or shader UI helpers!*

