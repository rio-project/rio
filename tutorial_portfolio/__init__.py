import rio

from . import pages

app = rio.App(
    name="My Portfolio",
    build=rio.Router,
    routes=[
        rio.Route("", pages.PortfolioView),
    ],
)


fa_app = app.as_fastapi()
