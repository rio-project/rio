import rio

from . import pages

app = rio.App(
    name="My Portfolio",
    pages=[
        rio.Page("", pages.CvView),
    ],
)


fastapi_app = app.as_fastapi()
