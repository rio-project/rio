import rio

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

    result.snippet("example-counter/simple_counter_app")

    result.box(
        "info",
        """
If you would like to run this app yourself, you can create a new project using

```bash
rio init --example counter
```

<!-- TODO: Rework this once the CLI is done. -->

After some questions, this will create the project directory and add
all code necessary to run the "Counter" app. You can start the app using

```bash
rio run
```
""",
    )

    result.markdown(
        """
Let's break this down.

## Components
"""
    )

    result.snippet("example-counter/simple_counter_app", section="circular-button")

    result.markdown(
        """
First, we can see the definition of a `CircularButton` component. Components are
the building blocks of Rio apps. They are the basic elements that make up your
app, and they can be combined to create more complex components. In this case,
`CircularButton` is a component that displays a button with a circular shape.
Since the counter app needs two of these (one for incrementing the counter, and
one for decrementing it), it makes sense to create a component for it, so we
don't have to repeat the same code twice.

This is a common theme you'll see in Rio apps: components are used to create
reusable building blocks. This makes it easy to create complex apps, since you
can just combine existing components to create new ones.

Rio already comes with a lot of components, such as buttons, inputs, text,
images, and more. If you need more complex components, simply combine existing
components to create new ones.

Let's have a closer look at the `CircularButton` component. It starts off like
any other Python class, and inherits from `rio.Component`. This is the base
class for all Rio components.

It then lists all attributes buttons have, as well as their data types. This is
important, because all Rio widgets are automatically `dataclass`es. This means,
that Components will automatically have an `__init__` method, so you don't
have to write one yourself.

Modern code editors such as VSCode also understand dataclasses, and will
help you with autocompletion and type checking. So writing clean code with type
annotations is very important, and Rio makes it easy to do so.

At the bottom of the class, we can see the `build` method. Rio calls this method
when it needs to display the component. In this case the `build` method returns
a `rio.Button` component, which is one of the built-in components that Rio
ships with. So each time Rio needs to display a `CircularButton`, it will
call the Component's build method and display it's output.
"""
    )

    result.snippet("example-counter/simple_counter_app", section="counter")

    result.markdown(
        """
Next, we can see the definition of the `Counter` component. This is the main
component of the app, and combines the `CircularButton` component we just
defined with other built-in components to create the final app. You can see it
follows a similar structure as the `CircularButton` component:

- It inherits from `rio.Component`
- It lists all attributes it has, along with their data types
- It has a `build` method that returns a component

In this case there is also additional methods. These are "event handlers", that
will be called when the user interacts with the component, e.g. by pressing a
button. We'll see more about how events work later.

The `build` method is a bit more complex this time. It combines multiple layout
components to create the final layout of the app. For example, `rio.Column` is a
component that arranges multiple components vertically. `rio.Row` is similar,
but arranges components horizontally. These two are some of the most commonly
used layout components. With some experience you'll quickly be able to create
complex layouts just by combining these two.

We can also see `rio.Text` and `rio.Button` components. `rio.Text` simply
displays the given string, while `rio.Button` displays a button that can be
pressed by the user. The button also has an `on_press` attribute, which is one
of the event handlers we touched on earlier. If you pass a function to
`on_press`, that function will be called whenever the user presses the button.

At last, there is some interesting layout attributes being passed to the
Components:

- `Column.spacing` and `Row.spacing` control how much free space to leave
    inbetween child components.
- `align_x` and `align_y` are available on nearly all Rio components. They
    control the position of a component if it has more space available than it
    needs. A value of `0` means the component will be aligned at the start (i.e.
    left or top), while a value of `1` means it will be aligned at the end (i.e.
    right or bottom). You can also pass any values inbetween, e.g. `0.5` will
    center the component. If you don't pass any alignment values the components
    will take up all available space instead.


## A Quick Note on Units

When specifying sizes in Rio, you'll often see values such as `5` or `2.5`.
These are not pixels, but "font heights". This means that a value of `1` is the
same as the height of a single line of text. `5` would be five times as much,
and so on.

Measuring distances in font-heights may be surprising, but it has some real
advantages. If we were to specify sizes in pixels, the app might look fine on
your screen, but it might look completely different on a screen with a different
resolution. This is especially important since modern apps/websites need to run
on a variety of different devices, from phones to tablets to desktop computers.

By using font-heights, we can ensure that the app will look great on all devices
without having to worry about resolution at all. In addition, the entire app
will scale up nicely if a user increases the font size on their device, e.g.
because they have poor eyesight.

## Creating & Running the App

Next in the code we can see the definition of the `App` itself:
"""
    )

    result.snippet("example-counter/simple_counter_app", section="app")

    result.markdown(
        """
The app contains everything needed to run your app, such as the app's name, and
which Components to display. Since we're trying to keep it simple, we'll only
specify one thing: A page with the `Counter` component. Rio apps can have any
number of pages, but we'll only need the one for this app.

Lastly, let's run the app:
"""
    )

    result.snippet("example-counter/simple_counter_app", section="run")

    result.markdown(
        """
This will start the app, and open it in your browser. You can now interact with
the app, and see how it works. If you want to stop the app, simply press
`Ctrl+C` in the terminal.

Rio supports several ways to run apps, including `run_in_browser`, and
`run_in_window`. There's more ways to run apps, but we'll cover those in detail
when we talk about deployment.
"""
    )

    result.summary(
        "Rio apps are created by combining components",
        "Many components already ship with Rio, but it's easy to create your own by combining existing ones",
        "Components are just Python classes that inherit from `rio.Component`",
        "At a minimum, each component needs to implement a `build` method",
        "Components can have attributes. Each attribute has a name as well as a data type",
        'All sizes in Rio are measured in "font heights"',
    )

    result.navigation(
        "Rio Setup",
        rio.URL("tutorial-1-rio-setup"),
        "App Setup",
        rio.URL("tutorial-3-application-setup"),
    )

    return result
