from .. import article


def generate() -> article.Article:
    result = article.Article()

    result.markdown(
        """
# Rio Tutorial - Project Setup

Welcome to the Rio tutorial! This short series will walk you through the basics
of Rio and show you how to build your own apps and websites. The **code for apps
and websites is exactly the same**. The only difference is in how you run them.
So regardless of whether you want to build a website or an app, follow along and
soon you'll be able to create both!

## Installing Python

First things first, let's get your project set up. Rio is a Python library, so
make sure you have Python installed. You can verify your python is working by
running this command in your terminal:

```sh python --version ```

If you can see a version from 3.9.* to 3.11.* you're good to go! If not, you can
install python using your package manager if on Linux, or [download Python
here](https://www.python.org/downloads/). Make sure to check the "Add Python to
PATH" option during installation, as this makes it much easer to run Python from
the command line.

## Installing Rio

Next, we'll need to install Rio. A straightforward way to do this is to just
install it with `pip`:

```sh pip install rio[window] ```

This will install rio, along with the optional `window` extra. This extra allows
you to create local apps in addition to websites.

## Creating a Rio Project

<!-- Explain this once the CLI is done. -->

## Running Your Project

Now that your project is all set up, let's run it! Open a terminal and navigate
to your project directory. Then, run the following command:

<!-- Explain this once the CLI is done. -->

You can exit the app by pressing `Ctrl+C` while the terminal is focused.

If you can see an app window pop-up you're golden! If not, double check that you
have followed all the steps above. If you need help, feel free to reach out on
the [Rio Discord server](https://TODO-insert-discord-server-link). We have a
section dedicated to helping newcomers get started.
"""
    )

    return result
