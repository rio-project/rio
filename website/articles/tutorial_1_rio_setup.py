import rio

from .. import article


def generate() -> article.Article:
    result = article.Article()
    result.text("Rio Setup", style="heading1")

    result.markdown(
        """
Welcome to the Rio tutorial! This short series will walk you through the process
of setting up a Rio application from scratch, including installing Rio, creating
a new project, and turning that project into your own interactive CV.
"""
    )

    result.box(
        "info",
        """
Rio code is the same, regardless of whether you're creating an app or website.
The only difference is in how you run it.

So, while this tutorial will focus on creating a website, the concepts you learn
here will apply regardless of whether you're creating a website or an app.
        """,
    )
    result.markdown(
        """
## Installing Python

First things first, make sure you have Python installed. Rio is compatible with
Python versions `3.10`, `3.11` and `3.12`. You can check your Python version by
running the following command in your terminal:

```bash
python --version
```

Or, on some platforms:

```bash
python3 --version
```

If you can see a supported Python version you're good to go! If not, install
Python using your package manager, or download it from the [Python
website](https://www.python.org/downloads/).
"""
    )

    result.box(
        "info",
        """
For the rest of this tutorial, we'll assume that the Python command is available
as `python`. If that isn't the case on your system, make sure to replace
`python` with `python3` or whatever the command is on your system.
        """,
    )

    result.markdown(
        """
## Installing Rio

Rio is available on PyPI, so you can install it using `pip`:

```bash
python -m pip install rio
```

This will install the `rio` library, so you can use it in your projects, as well
as the `rio` command line tool. We'll use this tool to setup our little
tutorial project, as well as to run it.

If you're using `poetry`, `conda` or similar, those will work as well of course.

TODO: Actually test conda. How does it work?
"""
    )

    result.navigation(
        "",
        None,
        "Application Overview",
        rio.URL("tutorial-2-application-overview"),
    )

    return result
