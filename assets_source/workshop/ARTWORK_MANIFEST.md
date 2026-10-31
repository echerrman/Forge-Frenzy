# Workshop artwork manifest

These are editable, full-resolution source assets. The game uses optimized copies under `assets/workshop/`.

## Approved composition

- `master_workshop_composition_2560x1440_v2.png`: visual reference for the complete shop.
- `workshop_clean_plate_2560x1440_v2.png`: background architecture without stations.
- `layers/station_bases_2560x1440_v1.png`: all production stations on a transparent 2560x1440 canvas.
- `layers/customer_counter_foreground_2560x1440_v1.png`: counter foreground on a transparent 2560x1440 canvas.

The rear customer inlet and counter remain architectural elements. Customer arrival and walking artwork are intentionally out of scope; a counter idle was added later as a separate character layer.

## Station sources

`stations/station_sprite_layout.json` records source and runtime rectangles. Every station folder contains:

- `<station>_base.png`: cropped editable sprite.
- `<station>_mask.png`: white alpha silhouette for interaction highlighting.

The game renders the full-canvas station layer to avoid seams between adjacent station crops. The individual masks provide silhouette hover feedback.

## Animation sources

- `animations/furnace_flame/`: transparent flame-only overlays and their generated source sheet.
- `animations/quench_ripple/`: transparent water-only overlays and their generated source sheet.
- `animations/furnace_station/`: four complete furnace sprites with identical geometry and changing flame.
- `animations/quench_station/`: four complete quench sprites with identical geometry and changing water.

These experimental variants are retained only as source material. The runtime shop deliberately uses the static furnace and quench art because the generated motion did not register cleanly enough with the approved station bases.

## Character sources

- `assets_source/characters/blacksmith_idle/blacksmith_idle_sheet.png`: four-frame apprentice blacksmith hammer-idle sheet.
- `assets_source/characters/customer_idle/elin_idle_sheet.png`: three-frame Elin counter-idle sheet.

Runtime character frames are registered exports in `assets/characters/`. The blacksmith rests for most of a three-second loop before briefly lifting his hammer. Elin's restrained three-frame idle cycles continuously at two frames per second. No customer walking or entrance sequence is included.

## Runtime export

Runtime images are half-scale (1280x720 base canvas) PNGs. No additional runtime dependency is required; Pygame loads the exported files directly.
