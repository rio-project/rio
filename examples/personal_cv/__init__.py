import rio

from . import pages

app = rio.App(
    name="My Portfolio",
    build=rio.PageView,
    pages=[
        rio.Page("", pages.CvView),
    ],
)


fastapi_app = app.as_fastapi()
