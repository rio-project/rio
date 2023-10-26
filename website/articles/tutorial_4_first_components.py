from .. import article


def generate() -> article.Article:
    result = article.Article()

    result.markdown(
        """
# Creating our First Components

Everything is installed, our project structure is in place, and we are ready to
start working on our app! Let's start by creating a component that displays our
name, and a short biography.

Create a new file in the `components` directory, and name it `TODO.py`. In this
file, we will create a new component that displays our name, and a short
biography.

Copy & paste the following code into the file:
"""
    )

    result.snippet("biography_component")

    result.markdown(
        """
Most parts of the component should look familiar by now. We again have a class
that inherits from `rio.Component`, and a `build` method. Since our content is
doesn't have to change there is no need for any attributes in this class
"""
    )

    result.summary(
        "TODO",
    )

    return result
