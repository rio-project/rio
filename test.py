import asyncio
import webview
from web_gui import *
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE
GENERATED_DIR = PROJECT_ROOT / "generated"


HTML_BOILERPLATE = """
<!DOCTYPE html>
<html>
<head>
	<title>{title}</title>
	<style>
		html, body {{
			margin: 0;
			padding: 0;
			height: 100%;
		}}
	</style>
</head>
<body>
{body}
</body>
</html>
"""


async def main():
    title = "Sample Page"

    # gui = Row(
    #     Rectangle(color=Color.srgb(1, 0, 0)),
    #     Rectangle(color=Color.srgb(0, 1, 0)),
    #     Text("Hello, world!"),
    # )

    gui = Row(
        Margin(
            Rectangle(
                color=Color.RED,
                # grow=1,
            ),
            margin=1,
        ),
        Column(
            Rectangle(
                color=Color.GREEN,
                # grow=1,
            ),
            Stack(
                Rectangle(
                    color=Color.BLUE,
                    # grow=1,
                ),
                Align.center(
                    Rectangle(
                        color=Color.WHITE,
                        # requested_height=5,
                        # requested_width=5,
                    ),
                ),
            ),
        ),
    )

    html = "".join(gui._as_html())
    html = HTML_BOILERPLATE.format(
        title=title,
        body=html,
    )

    (GENERATED_DIR / "page.html").write_text(html)

    webview.create_window(
        title,
        html=html,
        text_select=True,
        server=None,  # type: ignore
    )
    webview.start()


if __name__ == "__main__":
    asyncio.run(main())
