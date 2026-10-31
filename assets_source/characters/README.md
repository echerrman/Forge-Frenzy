# Character source artwork

## Apprentice blacksmith

`blacksmith_idle/blacksmith_idle_sheet.png` contains four horizontally arranged transparent frames matching the approved primary character reference. The runtime uses a sparse three-second loop: a relaxed hold, a brief hammer lift, and a return to rest.

## Elin

`customer_idle/elin_idle_sheet.png` contains three horizontally arranged transparent frames for the first scripted village customer. The runtime cycles the restrained idle continuously at two frames per second and draws her behind the foreground counter. The counter hides her lower body; no customer walking or entrance sequence is implemented.

Runtime exports live in `assets/characters/`. They are intentionally small and pre-scaled so Pygame does not need to resize them every frame.
