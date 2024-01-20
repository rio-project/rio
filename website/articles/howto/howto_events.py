import rio

from ... import article_models


class Builder(article_models.ArticleBuilder):
    def __init__(self):
        super().__init__(
            "HowTo: Creating Custom Events",
            "events",
        )

    def build(self) -> article_models.BuiltArticle:
        result = article_models.BuiltArticle()

        result.markdown(
            """
    # Creating Custom Events

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
