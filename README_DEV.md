# Forge Frenzy development notes

Forge Frenzy (also called Forged to Order) is a 1280x720 mouse-driven blacksmith game built with Python and Pygame.

## Run

```text
python -m pip install -r requirements.txt
python main.py
```

Phases 3 and 4 provide the complete playable order loop: persistent hotbar placement, six mouse-driven crafting interactions, delivery, scoring, rewards, results, day summaries, and continued days. The initial Elin iron-dagger order is the primary polished prototype path.

Controls: left-click buttons and workshop hotspots. Escape goes back; Escape on the main menu quits.

Start a workday, accept the displayed order at the Customer Counter, click a metal ingot in Storage, and follow the order ticket through the stations. The active customer, order, patience, inventory, station progress, and workpiece location remain intact while navigating scenes.

## Station controls

- Storage: click an iron or steel ingot in its storage bin.
- Furnace: click Current Work to insert the metal; click it in the furnace when the timer is ready.
- Mold: click the matching mold, click Current Work, then hold the ladle until full.
- Anvil: click Current Work, then click all glowing blade targets.
- Quench: click Current Work, drag the blade into the water, and hold continuously until complete.
- Grindstone: click Current Work, click the crank seven times, then hold and sweep the blade horizontally across the wheel. Spin resets on station exit while sharpening progress persists.
- Assembly: click Current Work, then drag the requested handle and guard onto their targets.
- Delivery: return to the Customer Counter and click it.

The Options menu supports fullscreen and windowed modes. Rendering uses a fixed 1280x720 logical canvas with aspect-ratio-preserving scaling.
