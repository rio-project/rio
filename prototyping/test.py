import asyncio
from web_gui import *
from pathlib import Path
import web_gui.widgets as widgets
import json


HERE = Path(__file__).resolve().parent.parent
PROJECT_ROOT = HERE
BUILD_DIR = PROJECT_ROOT / "build"
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def build_lsd() -> Widget:
    Lsd = LinearGradientFill(
        (Color.RED, 0.0),
        (Color.GREEN, 0.5),
        (Color.BLUE, 1.0),
        angle_degrees=45,
    )

    return Column(
        children=[
            Text("Foo", font_weight="bold"),
            Rectangle(fill=Color.BLUE),
            Row(
                children=[
                    Rectangle(fill=Color.RED),
                    Rectangle(fill=Color.GREY),
                ],
            ),
            Stack(
                children=[
                    Text("Bar"),
                    Text("Baz"),
                    Rectangle(fill=Color.GREEN),
                ]
            ),
            Rectangle(fill=Lsd),
        ]
    )


def build_diffusion_ui() -> Widget:
    children = [
        Rectangle(
            fill=Color.RED,
            corner_radius=(2.0, 2.0, 2.0, 2.0),
        ),
        Column(
            children=[
                Text(
                    "Positive Prompt Example, Lorem Ipsum dolor sit amet",
                    multiline=True,
                ),
                Text(
                    "Negative Prompt Example, Lorem Ipsum dolor sit amet",
                    multiline=True,
                ),
                Row(
                    children=[
                        Text("Euler A"),
                        Text("20 Steps"),
                    ],
                ),
                Text("CFG 7.0"),
                Text("Tilable"),
            ],
        ),
    ]
    return Stack(children)


def main():
    root_widget = build_lsd()
    app = App("Super Dynamic Website!", root_widget)
    app.run(quiet=False)


if __name__ == "__main__":
    # asyncio.run(main())
    main()
