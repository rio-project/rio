import rio


class Counter(rio.Component):
    value: int = 0

    def _on_increment(self, event: rio.ButtonPressEvent) -> None:
        self.value += 1

    def _on_decrement(self, event: rio.ButtonPressEvent) -> None:
        self.value -= 1

    def _on_reset(self, event: rio.ButtonPressEvent) -> None:
        self.value = 0

    def build(self):
        return rio.Column(
            rio.Text(str(self.value), style="heading1"),
            rio.Row(
                rio.Button(
                    "-1",
                    shape="circle",
                    width=4,
                    height=4,
                    on_press=self._on_decrement,
                ),
                rio.Button(
                    "+1",
                    shape="circle",
                    width=4,
                    height=4,
                    on_press=self._on_increment,
                ),
                spacing=3,
            ),
            rio.Button(
                "Reset",
                style="minor",
                color="danger",
                on_press=self._on_reset,
            ),
            spacing=2,
            align_x=0.5,
            align_y=0.5,
        )


app = rio.App(
    rio.PageView,
    pages=[
        rio.Page(
            "",
            Counter,
        )
    ],
)

app.run_in_browser()
