from __future__ import annotations

import os
import sys
import threading
import webbrowser
from datetime import timedelta
from pathlib import Path
from typing import *  # type: ignore

import __main__
import fastapi
import uvicorn

import rio

from . import app_server, assets, common, debug, maybes
from .common import ImageLike

# Only available with the `window` extra
try:
    import webview  # type: ignore
except ImportError:
    webview = None


__all__ = [
    "App",
]


def _validate_build_function(
    build_function: Callable[[], rio.Component]
) -> Callable[[], rio.Component]:
    assert callable(
        build_function
    ), f"The App requires a function that returns a component, not {build_function!r}"

    def wrapper():
        component = build_function()

        assert isinstance(
            component, rio.Component
        ), f"The `build` function passed to the App must return a `Component` instance, not {component!r}."

        return component

    return wrapper


def make_default_connection_lost_component() -> rio.Component:
    class DefaultConnectionLostComponent(rio.Component):
        def build(self) -> rio.Component:
            return rio.Rectangle(
                child=rio.Row(
                    rio.Icon(
                        "error",
                        fill="danger",
                        width=1.5,
                        height=1.5,
                    ),
                    rio.Text(
                        "Connection lost",
                        style=rio.TextStyle(
                            fill=self.session.theme.danger_palette.background,
                            font_weight="bold",
                        ),
                    ),
                    spacing=1,
                    margin_x=2.5,
                    margin_y=1.5,
                ),
                style=rio.BoxStyle(
                    fill=self.session.theme.neutral_palette.background,
                    corner_radius=99999,
                    shadow_color=self.session.theme.shadow_color,
                    shadow_radius=0.6,
                    shadow_offset_y=0.15,
                ),
                margin_top=3,
                align_x=0.5,
                align_y=0.0,
            )

    return DefaultConnectionLostComponent()


class App:
    """
    Contains all the information needed to run a Rio app.

    Apps group all the information needed for Rio to run your application, such
    as its name, icon and, and the pages it contains. Apps also expose several
    lifetime events that you can use to perform tasks such as initialization and
    cleanup.

    If you're serving your app as a website, all users share the same `App`
    instance. If running in a window, there's only one window, and thus `App`,
    anyway.

    A basic setup may look like this:

    ```py
    app = rio.App(
        name="My App",
        build=MyAppRoot,
    )
    ```

    You can then run this app, either as a local application in a window:

    ```py
    app.run_in_window()
    ```

    Or you can create and run a webserver:

    ```py
    app.run_as_web_server()
    ```

    Or create a server, without running it. This allows you to start the script
    externally with tools such as uvicorn:

    ```py
    fastapi_app = app.as_fastapi()
    ```

    Attributes:
        name: The name to display for this app. This can show up in window
            titles, error messages and wherever else the app needs to be
            referenced in a nice, human-readable way.

        pages: The pages that make up this app. You can navigate between these
            using `Session.navigate_to` or using `Link` components. If running
            as website the user can also access these pages directly via their
            URL.

        assets_dir: The directory where the app's assets are stored. This allows
            you to conveniently access any images or other files that are needed
            by your app.
    """

    # Type hints so the documentation generator knows which fields exist
    name: str
    pages: Tuple[rio.Page, ...]
    assets_dir: Path

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        build: Optional[Callable[[], rio.Component]] = None,
        icon: Optional[ImageLike] = None,
        pages: Iterable[rio.Page] = tuple(),
        on_app_start: rio.EventHandler[App] = None,
        on_session_start: rio.EventHandler[rio.Session] = None,
        on_session_end: rio.EventHandler[rio.Session] = None,
        default_attachments: Iterable[Any] = (),
        ping_pong_interval: Union[int, float, timedelta] = timedelta(seconds=50),
        assets_dir: Union[str, os.PathLike, None] = None,
        theme: Union[rio.Theme, Tuple[rio.Theme, rio.Theme], None] = None,
        build_connection_lost_message: Callable[
            [], rio.Component
        ] = make_default_connection_lost_component,
    ):
        """
        Args:
            build: A function that returns the root component of the app. This
                function will be called whenever a new session is created. Note
                that since classes are callable in Python, you can pass a class
                here instead of a function, so long as the class doesn't require
                any arguments.

                If no build method is passed, the app will create a `PageView`
                as the root component.

            name: The name to display for this app. This can show up in window
                titles, error messages and wherever else the app needs to be
                referenced in a nice, human-readable way. If not specified,
                `Rio` name will try to guess a name based on the name of the
                main Python file.

            icon: The icon to display for this app. This can show up in window
                the title bars of windows, browser tabs, or similar.

            pages: The pages that make up this app. You can navigate between
                these using `Session.navigate_to` or using `Link` components. If
                running as website the user can also access these pages directly
                via their URL.

            on_app_start: A function that will be called when the app is first
                started. You can use this to perform any initialization tasks
                that need to happen before the app is ready to use.

                The app start will be delayed until this function returns. This
                makes sure initialization is complete before the app is
                displayed to the user. If you would prefer to perform
                initialization in the background try using `asyncio.create_task`
                to run your code in a separate task.

            on_session_start: A function that will be called each time a new
                session is created. In the context of a website that would be
                each time a new user visits the site. In the context of a window
                there is only one session, so this will only be called once.

                This function does not block the creation of the session. This
                is to make sure initialization code doesn't accidentally make
                the user wait.

            on_session_end: A function that will be called each time a session
                ends. In the context of a website that would be each time a user
                closes their browser tab. In the context of a window this will
                only be called once, when the window is closed.

            default_attachments: A list of attachments that will be attached to
                every new session.

            ping_pong_interval: Rio periodically sends ping-pong messages
                between the client and server to prevent overzealous proxies
                from closing the connection. The default value should be fine
                for most deployments, but feel free to change it if your hosting
                provider deploys a particularly obnoxious proxy.

            assets_dir: The directory where the app's assets are stored. This
                allows you to conveniently access any images or other files that
                are needed by your app. If not specified, Rio will assume the
                assets are stored in a directory called "assets" in the same
                directory as the main Python file.
        """
        main_file = _get_main_file()

        if name is None:
            name = _get_default_app_name(main_file)

        if build is None:
            build = rio.PageView

        if theme is None:
            theme = rio.Theme.pair_from_color()

        self.name = name
        self._build = _validate_build_function(build)
        self._icon = None if icon is None else assets.Asset.from_image(icon)
        self.pages = tuple(pages)
        self._on_app_start = on_app_start
        self._on_session_start = on_session_start
        self._on_session_end = on_session_end
        self._default_attachments = tuple(default_attachments)
        self.assets_dir = main_file.parent / (
            "assets" if assets_dir is None else assets_dir
        )
        self._theme = theme
        self._build_connection_lost_message = build_connection_lost_message

        if isinstance(ping_pong_interval, timedelta):
            self._ping_pong_interval = ping_pong_interval
        else:
            self._ping_pong_interval = timedelta(seconds=ping_pong_interval)

    def _as_fastapi(
        self,
        *,
        debug_mode: bool,
        running_in_window: bool,
        validator_factory: Optional[Callable[[rio.Session], debug.Validator]],
        internal_on_app_start: Optional[Callable[[], None]],
    ) -> fastapi.FastAPI:
        """
        Internal equivalent of `as_fastapi` that takes additional arguments.
        """
        return app_server.AppServer(
            self,
            debug_mode=debug_mode,
            running_in_window=running_in_window,
            on_session_start=self._on_session_start,
            on_session_end=self._on_session_end,
            default_attachments=self._default_attachments,
            validator_factory=validator_factory,
            internal_on_app_start=internal_on_app_start,
        )

    def as_fastapi(
        self,
        debug_mode: bool = False,
    ) -> fastapi.FastAPI:
        """
        Return a FastAPI instance that serves this app.

        This method returns a FastAPI instance that serves this app. This allows
        you to run the app with a custom server, such as uvicorn:

        ```py
        app = rio.App(
            name="My App",
            build=MyAppRoot,
        )

        fastapi_app = app.as_fastapi()
        ```

        You can then run this app with uvicorn:

        ```sh
        uvicorn my_app:fastapi_app
        ```
        """
        return self._as_fastapi(
            debug_mode=debug_mode,
            running_in_window=False,
            validator_factory=None,
            internal_on_app_start=None,
        )

    def _run_as_web_server(
        self,
        *,
        host: str,
        port: int,
        quiet: bool,
        debug_mode: bool = False,
        validator_factory: Optional[Callable[[rio.Session], debug.Validator]],
        internal_on_app_start: Optional[Callable[[], None]],
    ) -> None:
        """
        Internal equivalent of `run_as_web_server` that takes additional
        arguments.
        """
        port = common.ensure_valid_port(host, port)

        # Make sure all globals are initialized. This should be done as late as
        # possible, because it depends on which modules have been imported into
        # `sys.modules`.
        maybes.initialize()

        # Suppress stdout messages if requested
        kwargs = {}

        if quiet:
            kwargs["log_config"] = {
                "version": 1,
                "disable_existing_loggers": True,
                "formatters": {},
                "handlers": {},
                "loggers": {},
            }

        # Create the FastAPI server
        fastapi_app = self._as_fastapi(
            debug_mode=debug_mode,
            running_in_window=False,
            validator_factory=validator_factory,
            internal_on_app_start=internal_on_app_start,
        )

        # Serve
        uvicorn.run(
            app=fastapi_app,
            host=host,
            port=port,
            **kwargs,
        )

    def run_as_web_server(
        self,
        *,
        host: str = "localhost",
        port: int = 8000,
        quiet: bool = False,
    ) -> None:
        """
        Creates and runs a webserver that serves this app.

        This method creates and immediately runs a webserver that serves this
        app. This is the simplest way to run a Rio app.

        ```py
        app = rio.App(
            name="My App",
            build=MyAppRoot,
        )

        app.run_as_web_server()
        ```

        The will synchronously block until the server is shut down.

        Args:
            host: Which IP address to serve the webserver on. `localhost` will
                make the service only available on your local machine. This is
                the recommended setting if running behind a proxy like nginx.

            port: Which port the webserver should listen to.

            quiet: If `True` Rio won't send any routine messages to `stdout`.
                Error messages will be printed regardless of this setting.
        """
        self._run_as_web_server(
            host=host,
            port=port,
            quiet=quiet,
            validator_factory=None,
            internal_on_app_start=None,
        )

    def run_in_browser(
        self,
        *,
        host: str = "localhost",
        port: Optional[int] = None,
        quiet: bool = False,
    ) -> None:
        """
        Runs an internal webserver and opens the app in the default browser.

        This method creates and immediately runs a webserver that serves this
        app, and then opens the app in the default browser. This is a quick and easy
        way to access your app.

        ```py
        app = rio.App(
            name="My App",
            build=MyAppRoot,
        )

        app.run_in_browser()
        ```

        Args:
            host: Which IP address to serve the webserver on. `localhost` will
                make the service only available on your local machine. This is
                the recommended setting if running behind a proxy like nginx.

            port: Which port the webserver should listen to. If not specified,
                Rio will choose a random free port.

            quiet: If `True` Rio won't send any routine messages to `stdout`.
                Error messages will be printed regardless of this setting.
        """
        port = common.ensure_valid_port(host, port)

        def on_startup() -> None:
            webbrowser.open(f"http://{host}:{port}")

        self._run_as_web_server(
            host=host,
            port=port,
            quiet=quiet,
            validator_factory=None,
            internal_on_app_start=on_startup,
        )

    def run_in_window(
        self,
        quiet: bool = True,
        debug_mode: bool = False,
    ) -> None:
        """
        Runs the app in a local window.

        This method creates a window and displays the app in it. This is great
        if you don't want the complexity of running a web server, or wish to
        package your app as a standalone executable.

        ```py
        app = rio.App(
            name="My App",
            build=MyAppRoot,
        )

        app.run_in_window()
        ```

        This method requires the `window` extra. If you don't have it installed,
        you can install it with:

        ```sh
        pip install rio-ui[window]
        ```

        This method will synchronously block until the window is closed.  <!-- TODO is that correct? -->

        Args:
            quiet: If `True` Rio won't send any routine messages to `stdout`.
                Error messages will be printed regardless of this setting.
        """

        if webview is None:
            raise Exception(
                "The `window` extra is required to use `App.run_in_window`."
                " Run `pip install rio[window]` to install it."
            )

        # Unfortunately, WebView must run in the main thread, which makes this
        # tricky. We'll have to banish uvicorn to a background thread, and shut
        # it down when the window is closed.

        host = "localhost"
        port = common.ensure_valid_port(host, None)
        url = f"http://{host}:{port}"

        # This lock is released once the server is running
        lock = threading.Lock()
        lock.acquire()

        server: Optional[uvicorn.Server] = None

        # Start the server, and release the lock once it's running
        def run_web_server():
            fastapi_app = self._as_fastapi(
                debug_mode=debug_mode,
                running_in_window=True,
                validator_factory=None,
                internal_on_app_start=lock.release,
            )

            # Suppress stdout messages if requested
            log_level = "error" if quiet else "info"

            nonlocal server
            config = uvicorn.Config(
                fastapi_app,
                host=host,
                port=port,
                log_level=log_level,
                timeout_graceful_shutdown=1,  # Without a timeout, sometimes the server just deadlocks
            )
            server = uvicorn.Server(config)
            server.run()

        server_thread = threading.Thread(target=run_web_server)
        server_thread.start()

        # Wait for the server to start
        lock.acquire()

        # Start the webview
        try:
            webview.create_window(
                self.name,
                url,
            )
            webview.start()

        finally:
            assert isinstance(server, uvicorn.Server)

            server.should_exit = True
            server_thread.join()


def _get_main_file() -> Path:
    try:
        return Path(__main__.__file__)
    except AttributeError:
        pass

    # Find out if we're being executed by uvicorn
    main_file = Path(sys.argv[0])
    if (
        main_file.name != "__main__.py"
        or main_file.parent != Path(uvicorn.__file__).parent
    ):
        return main_file

    # Find out from which module uvicorn imported the app
    try:
        app_location = next(arg for arg in sys.argv[1:] if ":" in arg)
    except StopIteration:
        return main_file

    module_name, _, _ = app_location.partition(":")
    module = sys.modules[module_name]

    if module.__file__ is None:
        return main_file

    return Path(module.__file__)


def _get_default_app_name(main_file: Path) -> str:
    name = main_file.stem
    if name in ("main", "__main__", "__init__"):
        name = main_file.absolute().parent.stem

    return name.replace("_", " ").title()
