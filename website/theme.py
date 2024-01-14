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
ACTION_TITLE_HEIGHT = 4
ACTION_TEXT_HEIGHT = 1.5
COLUMN_WIDTH = 40


THEME_COLORS_GRADIENT_0 = rio.LinearGradientFill(
    (THEME.primary_color, 0),
    (THEME.secondary_color, 1),
    angle_degrees=0,
)


THEME_COLORS_GRADIENT_90 = rio.LinearGradientFill(
    (THEME.primary_color, 0),
    (THEME.secondary_color, 1),
    angle_degrees=90,
)


ACTION_TITLE_STYLE = rio.TextStyle(
    fill=rio.LinearGradientFill(
        (THEME.primary_color, 0),
        (THEME.secondary_color, 1),
        angle_degrees=-30,
    ),
    font_size=ACTION_TITLE_HEIGHT,
    font_weight="bold",
)


def get_subpage_height(session: rio.Session) -> float:
    # Window height, minus a little bit of extra space to have the next subpage
    # peeking through. This indicates that there's more content to scroll to.
    return session.window_height - 6


# Random material-styled images placed around the website
GENERIC_MATERIAL_IMAGES = (
    common.ASSETS_DIR
    / "material-backgrounds"
    / "pawel-czerwinski-ruJm3dBXCqw-unsplash.jpg",
)


def get_random_material_image() -> rio.ImageLike:
    return random.choice(GENERIC_MATERIAL_IMAGES)
