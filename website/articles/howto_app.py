import rio

from .. import article_models


def generate() -> article_models.BuiltArticle:
    result = article_models.BuiltArticle()

    result.markdown(
        """
    # Creating an App with Rio

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


class HowToAppArticle(article_models.ArticleBuilder):
    def __init__(self):
        super().__init__(
            "HowTo: Create an app with Rio",
            "howto-app",
        )

    def build(self) -> article_models.BuiltArticle:
        result = article_models.BuiltArticle()

        result.markdown(
            """
    # Creating an App with Rio

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
