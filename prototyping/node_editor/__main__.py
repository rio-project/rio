from pathlib import Path

import rio

# Initialize the development component
HERE = Path(__file__).parent.resolve()

rio.DevelComponent.initialize(HERE)


app = rio.App(
    build=rio.DevelComponent,
)

app.run_as_web_server(
    port=8001,
    debug_mode=True,
)
