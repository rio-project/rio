import rio


# <code>
class CustomComponent(rio.Component):
    def build(self) -> rio.Component:
        return rio.TextInput(
            text="Hello world!",
        )


# </code>
