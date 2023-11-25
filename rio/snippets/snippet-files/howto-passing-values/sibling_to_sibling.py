import rio


# <code>
class CustomComponent(rio.Component):
    some_value: str

    def build(self) -> rio.Component:
        return rio.Column(
            rio.TextInput(
                text=CustomComponent.some_value,
            ),
            rio.TextInput(
                text=CustomComponent.some_value,
            ),
            spacing=1,
        )


# </code>
