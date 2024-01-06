from pathlib import Path

import rio

# Initialize the development component
HERE = Path(__file__).parent.resolve()

rio.DevelComponent.initialize(HERE)


app = rio.App(
    build=lambda: rio.DevelComponent(
        children=[
            rio.Text("Child 1"),
            rio.Text("Child 2"),
        ],
    ),
    theme=rio.Theme.from_color(light=False),
)

app.run_as_web_server(
    port=8001,
    debug_mode=True,
)
