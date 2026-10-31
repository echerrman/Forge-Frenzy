# Forge Frenzy

Forge Frenzy, also called **Forged to Order**, is a single-player medieval blacksmith crafting and time-management game built with Python and Pygame.

Players accept weapon orders, choose materials, and move a persistent workpiece through a furnace, mold, anvil, quench tub, grindstone, and assembly bench. Finished weapons are scored for order accuracy, craftsmanship, and delivery speed before awarding gold and reputation.

## Requirements

- Python 3.10 or newer
- Pygame 2.5 or newer

## Install and run

```bash
python -m venv .venv
```

Activate the environment:

```text
Windows: .venv\Scripts\activate
macOS/Linux: source .venv/bin/activate
```

Then install and launch:

```bash
python -m pip install -r requirements.txt
python main.py
```

No external artwork or network service is required. The current visuals are drawn procedurally with Pygame.

## Gameplay

1. Start a workday and visit the Customer Counter.
2. Click the counter to accept the displayed order.
3. Visit Storage and click the required metal ingot.
4. Complete the crafting stations in order.
5. Return to the counter and deliver the assembled weapon.
6. Review the score and day summary, then begin another day.

The introductory order is an iron dagger for Elin. The workpiece remains in the **Current Work** hotbar while navigating between screens.

New players can select **Tutorial** in the lower-right corner of the main menu. The tutorial plays through Day 1 while dimming unavailable controls, highlighting the current objective, and explaining order details and each new station interaction.

### Station controls

- **Storage:** Click an iron or steel ingot in its storage bin.
- **Furnace:** Click the Current Work item to insert it. Click the heated item when the timer is ready.
- **Mold:** Select the matching mold, insert the workpiece, and hold the ladle until the mold is full.
- **Anvil:** Place the blade and click every glowing hammer point.
- **Quench tub:** Place the blade, drag it into the water, and hold continuously until quenched.
- **Grindstone:** Place the blade, click the crank seven times to spin up the wheel, then hold the blade and sweep it left and right across the wheel until sharp. Wheel spin resets when leaving the station; sharpening progress remains.
- **Assembly:** Place the blade and drag the requested handle and guard onto their target areas.
- **Delivery:** Return to the Customer Counter and click it.

Press **Escape** to return to the previous screen. The Options menu supports fullscreen and windowed display modes.

## Testing

Run the automated suite with:

```bash
python -m pytest -q
```

The tests cover scene navigation, orders, inventory, weapon-stage validation, station interactions, scoring, duplicate-payout prevention, day progression, display modes, and the complete mouse-driven introductory order.

## Project structure

```text
main.py                 Application entry point
game/app.py             Pygame loop and display modes
game/state.py           Persistent player and workday state
game/customers.py       Customers, orders, and queue behavior
game/items.py           Weapon model and production state machine
game/scoring.py         Score and reward calculations
game/scenes/            Menu, workshop, stations, results, and summary screens
game/stations/          Crafting-station controllers
tests/                  Automated tests
```

## Current scope

The first two scripted workdays are playable. Artwork and animation are intentionally lightweight. Advanced upgrades, audio, save files, and extensive later-game content are not yet implemented.
