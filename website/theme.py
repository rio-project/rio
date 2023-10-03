import random

import rio

from . import common

THEME = rio.Theme(
    # primary_color=rio.Color.from_rgb(0.9, 0.7, 0),
    # light=False,
)


# On desktop, most of the website is located in a centered column. This function
# returns the width of that column.
def get_center_column_width(sess: rio.Session) -> float:
    if sess.window_height > 120:
        return 116

    if sess.window_width > 60:
        return sess.window_height - 4

    return 40


# Random material-styled images placed around the website
GENERIC_MATERIAL_IMAGES = (
    common.ASSETS_DIR
    / "material-backgrounds"
    / "pawel-czerwinski-ruJm3dBXCqw-unsplash.jpg",
)


def get_random_material_image() -> rio.ImageLike:
    return random.choice(GENERIC_MATERIAL_IMAGES)
