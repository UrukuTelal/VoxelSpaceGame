# Voxel Space Game
## WIP
Voxel Space Game
Explore a living, breathing voxel universe — from spherical planets with evolving ecosystems to vast networked star clusters and mysterious AEtheric forces.

Overview
Voxel Space Game is an ambitious open-world sci-fi sandbox blending procedural planetary voxel worlds, evolutionary biology, and networked interstellar exploration.

Procedural spherical planets built from voxel chunks with realistic gravity and seamless edge continuity.

Dynamic species evolution driven by environmental and AEtheric influences.

Networked galaxy clusters powering seamless interstellar travel and multiplayer exploration.

Rich lore and narrative guided by an AI companion to immerse players in cosmic discovery.

Features
Spherical Voxel Worlds: Cube-face projection mapped onto spheres, supporting planetary-scale voxel terrain with smooth chunk loading and LOD.

Speciation & Evolution: Life adapts to varied environments with AEtheric particle interactions affecting mutations and abilities.

Networked Star Clusters: Scalable server grid hosting discrete star clusters, enabling galactic exploration with jump mechanics and void flight.

Player Gravity & Orientation: Realistic gravity vectors tied to planetary location with dynamic player orientation and flight controls.

Tutorial Arc: Narrative-driven onboarding guiding players through resource gathering, life creation, terraforming, and interstellar logistics.

Getting Started
Clone the repository

bash
Copy code
git clone https://github.com/UrukuTelal/VoxelSpaceGame.git
cd VoxelSpaceGame
Install dependencies (Python 3.10+, NumPy, PyOpenGL, pygame)

bash
Copy code
pip install -r requirements.txt
Run the main game module

bash
Copy code
python main.py
Project Structure
text
Copy code
assets/               # Textures and art assets (e.g. sun maps)
core/                 # Core math and projection modules (coordinates, voxel math)
world/                # Voxel world logic (blocks, chunks, planet generator)
rendering/            # OpenGL rendering and shaders
docs/                 # Design docs, specs, tutorial outlines
main.py               # Game entry point
Development Roadmap
 Spherical projection & cube-face mapping

 Face and block indexing with chunk management

 Player gravity and orientation system

 Procedural planet builder with layered biomes

 Species evolution and AEtheric mechanics integration

 Networked star cluster system and void flight

 Multiplayer support & server cluster syncing

 Narrative tutorial arc with AI companion integration

For detailed progress, see development_plan.md.

Design Documents
Speciation System

Networked Galaxy Architecture

Gameplay & Tutorial

Contributing
Contributions are welcome! Please fork the repo, create feature branches, and submit pull requests.
Report issues and ideas via GitHub issues.

License
This project is licensed under the MIT License. See LICENSE for details.

Contact
Created by Papa Moshi — Chickasaw Citizen, visionary, and space dreamer.
For questions or collaborations, open an issue or message via GitHub.