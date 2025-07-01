🌌 MMO Observer Portal Design (Using CCPWGL)
🧭 Purpose
To allow players (or curious outsiders) to visually explore the persistent universe of the game through a web-based portal that:

Renders delayed, read-only views of MMO activity.

Reflects faction control, traffic density, events, or AEtheric anomalies.

Adds mythic and exploratory elements to the game’s lore via external observation.

🧱 Architecture Overview
Backend:
Component	Role
🛰️ MMO Game Servers	Periodically emit observational data snapshots (every X minutes).
📦 Snapshot Buffer Service	Stores state history, timestamped (e.g., Redis, S3, or flat DB).
🔗 API Gateway	Exposes structured history data as JSON/Protobuf for the web viewer.
⚙️ Event Formatter	Converts game events into lore-styled descriptions (optional).

Frontend:
Component	Role
🌐 Web Interface (React/Vue + CCPWGL)	Visualizes star systems, ships, planetary surfaces.
🎛️ Time Scrubber UI	Allows viewers to scroll through time-delayed state updates.
🌌 Cluster Navigation	Mini-map or star chart for jumping between star clusters.
🎭 Lore Mode Toggle	Switch between raw data and “narrative filter” overlay.

🌠 Visual Data Layers (via CCPWGL)
Layer	Description
🌟 Starfields / Background Nebulae	Based on static data or procedural generation.
🌍 Planetary Bodies	Rendered via existing planetary generation logic.
🚀 Ships / Fleets	Rendered as icons or simplified hulls, anonymized if needed.
🧭 Faction Influence Zones	Volumetric overlays for contested or dominant zones.
⚡ AEtheric Phenomena	Visual overlays for anomalies, entropy wells, or signals.

🛡️ Security & Delay Features
Feature	Purpose
⏳ Snapshot Delay (e.g. 15 min)	Prevents real-time spying.
🚫 No Player Names/IDs	Preserves anonymity & mythic framing.
🧾 Summarized Event Logs	Prevents parsing exact movements (e.g., “Wormhole opened. 3 exits used.”).
📡 Data Fadeout	Older snapshots degrade visually into static/noise.

📚 Example Lore Overlays
“This system is unstable. Entropy storms frequent the void beyond the fifth orbit.”

“Echoes of civilization remain — this cluster saw conflict cycles over 100 years.”

“Unconfirmed signal from [REDACTED] — reinterpreted as a god by locals.”

🛠 Development Milestones
✅ Define snapshot data schema (position, type, faction, timestamp).

✅ Implement snapshot emission from server clusters.

⏳ Build buffer and API to serve latest snapshots.

⏳ Build web UI and CCPWGL integration (basic system view).

⏳ Add time scrubber and cluster map.

⏳ Add lore narration overlay and cosmic phenomena rendering.

