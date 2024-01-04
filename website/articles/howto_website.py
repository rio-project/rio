import rio

from .. import article_models


def generate() -> article_models.BuiltArticle:
    result = article_models.BuiltArticle()

    result.markdown(
        """
# Creating a Website with Rio

TODO
        """
    )

    result.snippet("tutorial-biography/skill_bars.py")

    result.navigation(
        "App Setup",
        rio.URL("tutorial-4-first-components"),
        "",
        None,
    )

    return result
