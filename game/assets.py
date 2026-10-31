"""Optional asset loading with safe fallbacks."""

from pathlib import Path
import pygame


class AssetManager:
    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent / "assets"
        self._fonts = {}

    def path(self, *parts):
        return self.root.joinpath(*parts)

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self._fonts:
            optional = self.path("fonts", "medieval.ttf")
            self._fonts[key] = pygame.font.Font(str(optional), size) if optional.is_file() else pygame.font.SysFont("georgia", size, bold=bold)
            if optional.is_file():
                self._fonts[key].set_bold(bold)
        return self._fonts[key]
