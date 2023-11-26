import rio


# <code>
class CustomComponent(rio.Component):
    some_value: str

    def _on_button_press(self) -> None:
        print(
            self.some_value
        )  # Just read the local value. It will always be up-to-date

    def build(self) -> rio.Component:
        return rio.Column(
            rio.TextInput(
                text=CustomComponent.some_value,  # Using the class property creates a state binding
            ),
            rio.Button(
                "Click me!",
                on_press=self._on_button_press,
            ),
        )


# </code>
