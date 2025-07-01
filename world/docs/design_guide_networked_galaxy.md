# Networked Galaxy Architecture & Void Flight Mechanics

## Overview

This document outlines the design and architecture of the networked server cluster system for our space voxel game, where the universe is divided into discrete star clusters hosted on separate servers arranged in a scalable grid. It also covers the gameplay and technical behavior of player flight beyond cluster boundaries into the vast, unbounded void of space.

---

## Server Cluster Grid

- The game universe is divided into multiple **star clusters**, each simulated and hosted on its own server instance.
- Servers are arranged logically in a **3x3 grid pattern**, where each server manages one star cluster.
- Each cluster represents a bounded volume of space containing stars, planets, and entities unique to that region.

### Inter-Cluster Navigation

- Players cannot freely fly from one cluster to another in real-time across server boundaries.
- Instead, cluster transitions happen through **intentional jump mechanics** such as warp gates or hyperjumps.
- Upon initiating a jump:
  - The current server serializes the player’s entity state (position, ship configuration, inventory, etc.).
  - This state is transmitted to the destination cluster’s server.
  - The player entity is spawned at a designated entry point within the target cluster.
  - The original server despawns the player entity.

### Benefits of This Approach

- Simplifies networking by avoiding live entity synchronization across server boundaries.
- Allows easy scalability—servers can be added or removed to expand or contract the universe.
- Supports modular cluster management and load balancing.

---

## The Void: No Wrap-Around, Infinite Space

- The universe does **not** wrap around; clusters are discrete islands in an endless cosmic ocean.
- Flying beyond the edge of a cluster leads into the **stary void**—a vast, unpopulated, and uncharted expanse.

### Behavior When Flying Into the Void

- No wrap-around or teleportation to another cluster happens when crossing cluster boundaries without a jump.
- The void represents:
  - Diminishing star density.
  - Loss of navigational aids and communication signals.
  - An existential danger zone where players risk getting lost or stranded indefinitely.

### Gameplay and Technical Considerations

- **Warning System:** Players receive visual or audio alerts when approaching cluster edges.
- **Void Drift:** Players can choose to drift into the void but risk losing their ship or needing emergency jumps.
- **Despawn Protocol:** Entities left unattended in the void for extended periods may be flagged for removal or trigger dynamic events.
- **Optional Void Events:** Rare cosmic phenomena or hidden wormholes may be discovered, enhancing exploration mystery.

---

## Server Boundary Logic

- Each cluster defines a fixed spatial boundary (e.g., a large sphere) beyond which void protocols apply.
- When a player's position exceeds this boundary, the system triggers appropriate gameplay responses such as warnings, drift behavior, or despawning.

```python
CLUSTER_BOUNDARY_RADIUS = 1_000_000  # Game units

def check_player_boundary(player):
    if player.position.magnitude() > CLUSTER_BOUNDARY_RADIUS:
        trigger_void_protocol(player)
