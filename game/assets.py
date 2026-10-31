"""Optional asset loading with safe fallbacks."""

from pathlib import Path
import pygame


class AssetManager:
    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent / "assets"
        self._fonts = {}
        self._images = {}

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

    def image(self, *parts, alpha=True, size=None):
        """Load an optional image once and return ``None`` when it is absent."""
        key = (parts, alpha, size)
        if key in self._images:
            return self._images[key]
        image_path = self.path(*parts)
        if not image_path.is_file():
            self._images[key] = None
            return None
        try:
            image = pygame.image.load(str(image_path))
            image = image.convert_alpha() if alpha else image.convert()
            if size and image.get_size() != size:
                image = pygame.transform.smoothscale(image, size)
        except pygame.error:
            image = None
        self._images[key] = image
        return image
