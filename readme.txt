Forge Frenzy / Forged to Order

Individual developer: Chris

Requirements: Python 3 and Pygame 2.5 or newer.

Setup and launch:
1. python -m pip install -r requirements.txt
2. python main.py

Controls:
- Left-click buttons and workshop hotspots.
- Escape returns to the previous screen; on the main menu it quits.
- The window close button quits.
- Select Tutorial in the lower-right corner of the main menu for a guided Day 1.

Implemented through Phases 3 and 4:
- 1280x720, 60 FPS Pygame application with delta-time updates.
- Main menu with Play, Instructions, and Quit.
- Clickable workshop overview with counter, storage, and six crafting stations.
- Dedicated placeholder screen and return navigation for every work area.
- Reusable buttons, font fallback, hover feedback, and scene transitions.
- Persistent GameState and PlayerProfile data shared by every scene.
- Scripted customers, orders, queue, active-order patience, and four supported customer categories.
- Iron/steel inventory selection and persistent active workpieces.
- Dagger/sword order definitions, component requirements, and order tickets.
- Enforced RAW through DELIVERED weapon state model for later crafting integration.
- Persistent Current Work hotbar with click-to-place station interactions.
- Interactive furnace timer, hold-to-pour mold, anvil hotspots, continuous-hold quenching, grindstone markers, and drag-and-drop assembly.
- Penalty-free introductory station interactions with progress indicators.
- Delivery validation, configurable weighted scoring, gold, reputation, and customer responses.
- Results screen, end-of-day summary, Day 2 continuation, and queued customers.
- Fullscreen and windowed display options with scaled rendering.
- Guided tutorial day with dimmed unavailable controls, highlighted objectives, and contextual instructions.

Testing summary: see the current phase report for tests actually executed.

Detailed controls:
- Storage: click a metal ingot in its bin.
- Furnace: click the Current Work item to insert it; click it again when ready.
- Mold: select the matching mold, insert the item, and hold the ladle until full.
- Anvil: place the blade and click every glowing hotspot.
- Quench: place the blade, drag it into the water, and hold continuously.
- Grindstone: place the blade, click the crank seven times, then hold and sweep the blade left and right across the wheel.
- Assembly: place the blade and drag the requested components onto the target boxes.
- Counter: click to accept an order or deliver an assembled weapon.

Known unfinished features: artwork and animation remain procedural and minimal. Advanced upgrades, audio, elaborate inventory economy, and later-game content are not implemented.

Third-party assets: none. Visuals use procedural Pygame shapes and system fonts.

Individual work list: all currently implemented code and procedural visuals were developed for this individual course project.
