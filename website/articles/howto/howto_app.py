import rio

from ... import article_models


class Builder(article_models.ArticleBuilder):
    def __init__(self):
        super().__init__(
            "HowTo: Create an app with Rio",
            "create-app",
        )

    def build(self) -> article_models.BuiltArticle:
        result = article_models.BuiltArticle()

        result.markdown(
            f"""
    # {self.title}

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
