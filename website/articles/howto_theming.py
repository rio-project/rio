import rio

from .. import article_models


def generate() -> article_models.BuiltArticle:
    result = article_models.BuiltArticle()

    result.markdown(
        """
# Customizing the Theme
        """
    )

    result.box(
        "info",
        """
The easiest way to customize the theme is to use [Rio's Theme
Builder](https://TODO.com/tools/theme-builder). It allows you to edit your
theme without writing any code, and shows you the result in real-time.
""",
    )

    result.markdown(
        """
TODO
"""
    )

    return result
