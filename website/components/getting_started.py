import rio

from .. import theme


class GettingStarted(rio.Component):
    def build(self) -> rio.Component:
        return rio.Card(
            rio.Rectangle(
                child=rio.MarkdownView(
                    """
# Get started in just a few minutes

Getting started with Rio is easy. Install it with pip and hit the ground running:

```bash
$ pip install rio-ui
$ rio new --example biography
$ rio run
```

That's it!
""",
                    width=theme.COLUMN_WIDTH,
                    align_y=0.5,
                ),
                style=rio.BoxStyle(
                    fill=rio.Color.BLACK,
                ),
            ),
            color="hud",
            corner_radius=0,
        )
