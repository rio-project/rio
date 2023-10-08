from .. import article


def generate() -> article.Article:
    result = article.Article()

    result.markdown(
        """
# Rio Tutorial - App Structure

In the previous tutorial we've set up our project and ran a simple example app.
Now, let's have a look at that app's code and see what makes it tick.

TODO

"""
    )

    return result
