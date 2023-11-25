import rio

from .. import article


def generate() -> article.Article:
    result = article.Article()

    result.markdown(
        """
# Multipage Apps

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
