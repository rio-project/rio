import rio

from .. import article


def generate() -> article.Article:
    result = article.Article()

    result.markdown(
        """
# More Components

At this point we've seen most basic concepts we need to build a Rio app. We've
used components, created components, and added a page to our app.

This tutorial won't introduce any new concepts, but instead will show you more
of the components that are available to you. We'll once again combine them to
create our own components, and use them to extend the bio page we've created
previously.

## Skill Bars

Now that everybody knows who you are, let's add a section that shows off your
skillset. Create a new file in the `components` directory and name it
`skill_bars.py`. Use this code:
        """
    )

    result.snippet("tutorial-biography/skill_bars")

    result.markdown(
        """
This is another rather simple component. It takes a dictionary of skills and
their levels, and displays them as a list of bars. This will give a nice visual
overview of your skills. The `ProgressBar` is a component we haven't come across
yet. It takes a value between 0 and 1, and displays a bar that represents that
value, with zero being empty, and one being full. It can also display
indeterminate progress, which is useful when you don't know how long something
will take. We don't need that ability here though.

A few basic layouting components and Text aside, we finally wrap everything into
a `rio.Card` component. This will give us a nice border around the component,
and make it stand out a bit more. Cards are a great way to visually group
related components together, and are used everywhere in Rio. They can also
react to mouse events, effectively using them as buttons.

Note that this time around we've added an attribute to the component. This will
allow us to pass the skills to the component when we use it, and create multiple
instances of the component representing different skills.

Let's move on to more components.

## Contact

Let's add a section that shows how people can contact you. We'll create a
component for this, and then use it both for contact information, as well as to
link to websites we can find you on.

`contact.py`:
        """
    )

    result.snippet("tutorial-biography/contact")

    result.markdown(
        """
Ah, something new is happening here! Right at the start of the component we've
used a `KW_ONLY` annotation. This is a special annotation that tells Rio that
the following attributes should only be passed by keyword. This isn't actually
specific to Rio, but works with all Python dataclasses. You don't have to use
it, but it can be useful when you have a lot of attributes, and want to make
sure that they are always passed by keyword, to keep the code readable.

We can also see the `build` method have a fair amount of logic. You don't just
have to return a `Component` immediately, but can also do some calculations in
here, as long as they're quick. In this case we're checking whether we should
display an icon or an image, and then create the appropriate component.

There's some new components hiding in here: `rio.Icon` does just what you'd
think. You can specify the name of an icon, and it will display that icon. Rio
ships with hundreds of icons, and you can also add your own. Adding icons is a
dead simple way to make your app look more polished, and because they're already
included this really couldn't be any easier.

You can find an interactive browser of all icons [on the Rio
website](https://TODO.com).
"""
    )

    result.box(
        "info",
        """
Icon names are in the format `set_name/icon_name:variant`. Rio already ships
with the `material` icon set, which contains icons in the style of Google's
Material Design. You don't have to specify all three though. If you leave out
the set name it defaults to `material`, and if you leave out the variant it
defaults to the default variant of the icon, i.e. no variant.
""",
    )

    result.markdown(
        """

Links are also new. Links can either point to external websites, or to other
pages in your app. In this case we'll be using an external link to point to your
web profiles.

## History

Let's add a section that shows what you've done in the past. We'll create a
`History` component for this, and then use it a couple times to show off your
work experience and education.

`history.py`:
"""
    )

    result.snippet("tutorial-biography/history")

    result.markdown(
        """
This component is a bit more complex than the previous ones. In fact, we're
creating two components here. Since they're closely related, we're grouping them
into a single file. But it would also be perfectly fine to split them into two
files.

First up, the `HistoryItem` component. This component displays a single item in
your history. It takes a few attributes, and displays them in a nice way. It
also allows you to expand the item to show more details. This is done by using a
`Revealer` component. This component takes two children: the header, and
content. The header is always visible, and the content is only visible when the
component is expanded. This allows us to show more details about something
without cluttering the UI.

The `History` component then takes a list of `HistoryItem`s, and displays them
in a column. Nothing crazy going on here.

# Projects

Last but not least, let's add a section that shows off some of your personal
projects. Presenting a well maintained portfolio of past projects is a quick way
to show off your skills, and can be a great way to get your foot in the door.

`project.py`:
"""
    )

    result.snippet("tutorial-biography/project")

    result.markdown(
        """
Once again we're creating two components here. The `Project` component displays
a single project. We've already encountered all of the components previously,
but it makes use of some functionality we haven't seen yet. Earlier we've
mentioned that `Card` components can act as buttons, and the `Project` component
does just that. When you click on it, it will open the link to the project in
your browser. This is done by assigning a function to the card's `on_press`
attribute. This function will be called whenever the card is pressed, and can
perform any action you want.

In our case we're using the `navigate_to` method of the `Session` class. This
method takes a `URL` object, and opens it in the browser. This allows us to
easily open links in the browser.
"""
    )

    result.box(
        "info",
        """
## Sessions
Each time a user opens your app or connects to the website a new `rio.Session`
is created. It contains a lot of core functionality, and you'll come across this
class a lot. Here's just some things a session can do:

- Control navigation
- Open & save files
- Manage user settings
- Store localization information, such as the user's preferred language and
  timezone
        """,
    )

    result.markdown(
        """
The `Projects` component then takes a list of `Project`s, and displays them in a
`rio.Grid`. This component is similar to rows and columns, but allows you to
add children two-dimensionally. Each child is added to a specific row and
column, and can occupy one or more grid cells.

# Putting it all together, again

Now that we have all the components we need, let's put them together to create
the complete bio page. We'll keep this short since we've already done this
many times before now. Update `biography_page.py` to look like this:
"""
    )

    result.snippet("tutorial-biography/biography_page")

    result.markdown(
        """
The most notable changes here are some new components again:

`rio.Rectangle` is a component that simply displays a rectangle. It's not very
useful by itself, but can be combined with other components to create
interesting UI elements.

There's also `rio.Overlay`, and this is a weird one. It takes a single child and
displays it above all other components on the page. The component also won't
scroll with the rest of the page, hovering above it instead. We use it to add
a button that allows readers to easily contact you via email.
"""
    )

    result.summary(
        "Rio ships with lots of useful components. Have a look at the docs (TODO link) to see them all",
        "`rio.Session` is an extremely useful class which allows you to control the app, access user settings and more",
        "The session is available in the `build` method of all components as `self.session`",
    )

    result.markdown(
        """
**That's it!** You've now seen the basics of Rio, and are well underway to
create your own apps. We've only scratched the surface of what Rio can do, but
you now know enough to get started.

The remaining tutorials aren't following any specific order, but instead show
you how to solve specific tasks. Feel free to skip around, and come back to
these tutorials whenever you need a refresher on the basics.
        """
    )

    # TODO link more tutorials

    result.navigation(
        "App Setup",
        rio.URL("tutorial-4-first-components"),
        "",
        None,
    )

    return result
