import rio


# <circular-button>
class CircularButton(rio.Component):
    text: str
    on_press: rio.EventHandler[[]] = None

    def build(self):
        return rio.Button(
            self.text,
            on_press=self.on_press,
            shape="circle",
            width=4,
            height=4,
        )


# </circular-button>


# <counter>
class Counter(rio.Component):
    value: int = 0

    def _on_increment(self) -> None:
        self.value += 1

    def _on_decrement(self) -> None:
        self.value -= 1

    def _on_reset(self) -> None:
        self.value = 0

    def build(self):
        return rio.Column(
            rio.Row(
                CircularButton(
                    "-1",
                    on_press=self._on_decrement,
                ),
                rio.Text(
                    str(self.value),
                    style="heading1",
                    width=5,
                ),
                CircularButton(
                    "+1",
                    on_press=self._on_increment,
                ),
                spacing=3,
            ),
            rio.Button(
                "Reset",
                style="minor",
                on_press=self._on_reset,
            ),
            spacing=2,
            align_x=0.5,
            align_y=0.5,
        )


# </counter>


# <app>
app = rio.App(
    pages=[
        rio.Page("", Counter),
    ],
)
# </app>

# <run>
app.run_in_browser()
# </run>
