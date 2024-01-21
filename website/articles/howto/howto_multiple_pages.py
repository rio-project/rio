import rio

from ... import article_models


class Builder(article_models.ArticleBuilder):
    def __init__(self):
        super().__init__(
            "HowTo: Multipage Apps",
            "pages",
        )

    def build(self) -> article_models.BuiltArticle:
        result = article_models.BuiltArticle()

        result.markdown(
            """
    # Multipage Apps

    TODO
            """
        )

        result.snippet("tutorial-biography/skill_bars.py")

        result.navigation(
            "App Setup",
            rio.URL("4-first-components"),
            "",
            None,
        )

        return result
