import asyncio
from web_gui import *
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent.parent
PROJECT_ROOT = HERE
GENERATED_DIR = PROJECT_ROOT / "generated"
SERVED_DIR = PROJECT_ROOT / "served"


def make_html(
    title: str,
    root_widget: Widget,
) -> str:
    # Dump the widgets
    widgets_json = root_widget._serialize()

    # Dump their states
    initial_states_json = {}
    to_do: List[Widget] = [root_widget]

    def extend_and_keep(widget: Widget):
        to_do.append(widget)
        return widget

    while to_do:
        widget = to_do.pop()
        initial_states_json[str(widget._id)] = widget._serialize_state()
        widget._map_direct_children(extend_and_keep)

    # Load the templates
    html = (SERVED_DIR / "root.html").read_text()
    js = (SERVED_DIR / "root.js").read_text()
    css = (SERVED_DIR / "root.css").read_text()

    # Fill in all placeholders
    js = js.replace(
        '"{root_widget}"',
        json.dumps(widgets_json, indent=4),
    )

    js = js.replace(
        '"{initial_states}"',
        json.dumps(initial_states_json, indent=4),
    )

    html = html.replace("{title}", title)
    html = html.replace("/*{style}*/", css)
    html = html.replace("/*{script}*/", js)

    return html


async def main():
    Lsd = LinearGradientFill(
        (Color.RED, 0.0),
        (Color.GREEN, 0.5),
        (Color.BLUE, 1.0),
        angle_degrees=45,
    )

    root_widget = Column(
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

    GENERATED_DIR.mkdir(exist_ok=True, parents=True)
    html = make_html("Super Static Website!", root_widget)
    (GENERATED_DIR / "site.html").write_text(html)


if __name__ == "__main__":
    asyncio.run(main())
