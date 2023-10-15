from .. import article


def generate() -> article.Article:
    result = article.Article()

    result.snippet("example_counter")

    return result
