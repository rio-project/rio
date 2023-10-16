from .. import article


def generate() -> article.Article:
    result = article.Article()

    result.markdown(
        """
# Application Overview

Now that we have Rio installed, let's take a look what a Rio application looks
like. This won't be the app we'll be building in this tutorial, but it will give
you a good idea of how Rio apps are structured, and what we need to implement to
create our own app.

This is the code of a simple Counter app. It just displays a number, along with
some buttons to change said number.
"""
    )

    result.snippet("simple_counter_app")

    result.markdown(
        """
Let's break this down.

TODO

"""
    )

    return result
