import rio

from .. import article


def generate() -> article.Article:
    result = article.Article()

    result.markdown(
        """
# Creating our First Components

Everything is installed, our project structure is in place, and we are ready to
start working on our app! Let's start by creating a component that displays our
name, and a short biography.

If you've followed the tutorial so far you should have the following file
structure:

```
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

Create a new file in the `components` directory, and name it `about_me.py`. In
this file, we will create a new component that displays our name, and a short
biography.

Copy & paste the following code into the file:
"""
    )

    result.snippet("tutorial-biography/about_me.py")

    result.markdown(
        """
Most parts of the component should look familiar by now. We again have a class
that inherits from `rio.Component`, and a `build` method. Since our content here
never changes there is no need for any attributes in this class.

The `build` method returns a `rio.Row` component. We've already seen those
before. They simply display all of their children next to each other,
horizontally. In this case, we have two children: A `rio.Image` component, and a
`rio.Column` component.

We'll use the `Image` to display a picture of yourself. To do this, add a
picture of yourself to the `assets` directory, and name it `me.jpg`.

The other parameters of the `Image` component control the size, shape, and
layout. In particular, `corner_radius` allows us to round the image's corners.
By providing a very large number, the image will be displayed as a circle.

`fill_mode` controls how the image is scaled to fit the shape. By providing
`fit`, the image is scaled to fit entirely inside the shape, without being
distorted.

`margin_right` makes Rio leave some empty space to the right of the image.
Remember that width's are specified in font-heights, to keep the layout
consistent across different screen sizes.

The `Column` below displays textual information about you. You can change these
to your liking of course. There's two things we haven't seen before here:
Firstly, the first `Text` component has a `style` attribute. This allows us to
control the appearance of that particular component. In this case we use it to
display your name as a heading, making it stand out from the rest of the text.

Secondly, the `Column`'s width is set to `grow`. This means that it will take up
all the remaining space in its parent `Row`. Taking back a step, we can see that
the `Image` will always be on the left side of the `Row` and take a fixed amount
of space, while the `Column` will take up all the remaining space on the right
side.

## Putting it all Together

Now that we have a component that displays our name and a short biography, we
can use it in our app. Rename the `sample_page.py` file to `biography_page.py`,
and replace its contents with the following code:
"""
    )

    result.snippet("tutorial-biography/biography_page_after_tutorial_4.py")

    result.markdown(
        """
Our page currently simply returns the `AboutMe` component we just created. We'll
extend this with more components over the next tutorials, but for now that's all
we have.

Finally, we have to update some references, since we renamed the
`sample_page.py` file earlier. Open `pages/__init__.py`, and update the import
like so:

```python
from .biography_page import BiographyPage
```

The root-level `__init__.py` file also needs the new class name:

```python
...
rio.Page("", pages.BiographyPage),
...
```

That's it! You can now run the app again, and see the changes you've made. Run
`rio run` to see our new component in action!
"""
    )

    result.summary(
        "Projects are organized into `components`, `pages`, and `assets`. Clean projects are easier to work on!",
        "Components often contain optional parameters that allow you to control their appearance.",
        "We can create interesting layouts by stacking components inside each other.",
    )

    result.navigation(
        "App Setup",
        rio.URL("tutorial-3-app-setup"),
        "More Components",
        rio.URL("tutorial-5-more-components"),
    )

    return result
