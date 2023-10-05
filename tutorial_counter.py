import rio


class Counter(rio.Component):
    value: int = 0

    def _on_increment(self, event: rio.ButtonPressEvent) -> None:
        self.value += 1

    def _on_decrement(self, event: rio.ButtonPressEvent) -> None:
        self.value -= 1

    def build(self):
        return rio.Column(
            rio.Text(f"The counter is currently at {self.value}"),
            rio.Button(
                "+1",
                on_press=self._on_increment,
            ),
            rio.Button(
                "-1",
                on_press=self._on_decrement,
            ),
            spacing=1,
            width=20,
            align_x=0.5,
            align_y=0.5,
        )


app = rio.App(
    rio.PageView,
    routes=[
        rio.Page(
            "",
            Counter,
        )
    ],
)

app.run_in_browser()
