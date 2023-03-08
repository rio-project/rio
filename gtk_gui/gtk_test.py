import gtk_gui
import asyncio


async def main():
    app = gtk_gui.App("Test App", "com.test")

    window = app.create_window(
        title="Test Title",
        size=(800, 600),
        widget=gtk_gui.Column(
            gtk_gui.Label("Hello, world!", grow=False),
            gtk_gui.Button("Click me!", grow=True),
        ),
    )

    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
