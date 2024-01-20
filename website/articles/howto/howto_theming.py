import rio

from ... import article_models


class Builder(article_models.ArticleBuilder):
    def __init__(self):
        super().__init__(
            "HowTo: Customizing the Theme",
            "theming",
        )

    def build(self) -> article_models.BuiltArticle:
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
