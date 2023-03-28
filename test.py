import asyncio
import webview
from web_gui import *
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE
GENERATED_DIR = PROJECT_ROOT / "generated"


async def main():
    title = "Sample Page"

    Lsd = LinearGradientFill(
        (Color.RED, 0.0),
        (Color.GREEN, 0.5),
        (Color.BLUE, 1.0),
        angle_degrees=45,
    )

    gui = Column(
        children=[
            Text("Foo"),
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
                    # Rectangle(fill=Color.GREEN),
                ]
            ),
            Rectangle(fill=Lsd),
        ]
    )

    as_json = gui._serialize()

    with open(GENERATED_DIR / "sample.html", "w") as f:
        f.write(json.dumps(as_json, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
