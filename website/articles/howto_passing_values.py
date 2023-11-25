import rio

from .. import article


def generate() -> article.Article:
    result = article.Article()

    result.markdown(
        """
# Passing Values Between Components

## Parent to Child

When creating apps with Rio, values frequently need to be passed between
components. For example, you may pass a string value to a `TextInput` component
like this:
"""
    )

    result.snippet("howto-passing-values/parent_to_child.py", section="code")

    result.markdown(
        """
Nothing special going on here. We're just passing a string value to a component.

## Child to Parent

But what if we wanted to pass a value in the other direction? After the user
enters a text, we need to be able to get the modified value after all, so we
can store it in a database, send it to a server, or whatever else we need to do
with it.

Rio provides a convenient way to do this. Let's take a look at code:
        """
    )

    result.snippet("howto-passing-values/child_to_parent.py", section="code")

    result.markdown(
        """
The results looks fairly similar to the previous example, but with one key
difference: Notice how the `text` value we're passing to the `TextInput`
component is written as `CustomComponent.some_value` instead of
`self.some_value`? By passing the class property instead of the instance
property, we're telling Rio that we don't just want to pass the current value to
the child, but for Rio to create a connection between the parent and child
components.

If either of the components now assigns a new value to `some_value`, the other
component will automatically be updated with the new value, without any extra
code on our part!

So now, if you want to get the value of the `TextInput` component, you can just
write `setlf.some_value` and it will always contain the up-to-date value of the
`TextInput` component.

An example including reading the value back follows in the next section:

## Sibling to Sibling

Passing values between siblinds doesn't require any new concepts. Simply bind
both components to the same class property, and they will be kept in sync:

"""
    )

    result.snippet("howto-passing-values/sibling_to_sibling.py", section="code")

    result.markdown(
        """
Here, changing either of the inputs will update the other one. (You might have
to press enter or click outside the input to see the change.)
"""
    )

    return result
