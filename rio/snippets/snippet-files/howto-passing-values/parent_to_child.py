import rio


# <code>
class CustomComponent(rio.Component):
    some_value: str

    def build(self) -> rio.Component:
        return rio.TextInput(
            text=CustomComponent.some_value,
        )


# </code>
