import rio

from ... import article_models


class Builder(article_models.ArticleBuilder):
    def __init__(self):
        super().__init__(
            "App Setup",
            "3-app-setup",
        )

    def build(self) -> article_models.BuiltArticle:
        result = article_models.BuiltArticle()

        result.markdown(
            """
# App Setup

In the previous tutorial, we have looked at the source code of a simple Rio app.
While this has given us a nice overview over what a Rio app looks like, it the
previous app wasn't what we want to build in this tutorial. Instead of a
counter, let's build a personal website that shows our biography, and past
projects, so that we can show it to potential employers.

Let's get started by creating a new project using the Rio CLI:

```bash
rio new
```

Once again, rio will ask us a few questions about our project. This time, we
will answer them as follows:

<-- TODO: Rework this once the CLI is done. -->

The rio tool has created a new project directory for us, and added some code to
help us get started. Open the project directory in your editor of choice, and
let's have a look at the code.

You should see a file structure resembling this:

```text
<todo-project-name>
│
├── components
│   ├── __init__.py
│   └── sample_component.py
│
├── pages
│   ├── __init__.py
│   └── sample_page.py
|
├── assets
│
└── __init__.py
```

Along with some other files, you can see Rio's suggested project structure.

The `components` directory contains all components that make up your app. Since
these will be reused all throughout your code, they are placed in a separate,
and well known directory.

The `pages` directory is similar, but contains top-level components that are
used to display the content of a page. By keeping the pages separate from the
remaining components it's easier to keep an overview over your app.

The `assets` directory is empty for now. It is used to store non-code files that
are needed by your app, such as images.
    """
        )

        result.box(
            "info",
            """
You are of course free to change this structure to your liking, but sticking to
the common structure will make it easier for other developers to understand your
code and also help you when you ask for advice.
            """,
        )

        result.markdown(
            """
If you would like to run the placeholder code to get a quick overview over what
it does, you can do so by running the following command:

```bash
rio run
```

This already concludes the project setup. Thanks to the `rio` tool everything is
taken care of for us, and we can start working on our app right away.
    """
        )

        result.summary(
            "The rio tool can be used to create new projects, as well as to run them.",
            "Sticking to the standard project structure makes it easier to work with other developers.",
        )

        result.navigation(
            "App Overview",
            rio.URL("tutorial-2-app-overview"),
            "First Components",
            rio.URL("tutorial-4-first-components"),
        )

        return result
