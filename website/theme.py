import random

import rio

from . import common

THEME = rio.Theme.from_color(
    # primary_color=rio.Color.from_rgb(0.9, 0.7, 0),
    hud_color=rio.Color.from_hex("0f052f"),
    # light=False,
)


# Text on the landing page is unusually large. These constants control the
# landing page styles for it (and other things).
SUBPAGE_HEIGHT = 60
TITLE_HEIGHT = 4
ACTION_TEXT_HEIGHT = 1.5
COLUMN_WIDTH = 40


# Random material-styled images placed around the website
GENERIC_MATERIAL_IMAGES = (
    common.ASSETS_DIR
    / "material-backgrounds"
    / "pawel-czerwinski-ruJm3dBXCqw-unsplash.jpg",
)


def get_random_material_image() -> rio.ImageLike:
    return random.choice(GENERIC_MATERIAL_IMAGES)
