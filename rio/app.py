from __future__ import annotations

import asyncio
import os
import socket
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

from . import app_server, assets, debug
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


def default_connection_lost_message() -> rio.Component:
    return rio.Html(
        """
<div class="error-box">
    <svg xmlns="http://www.w3.org/2000/svg"
        style="fill: var(--rio-global-danger-bg); width: 1.6rem; height: 1.6rem;" viewBox="0 -960 960 960">
        <path
            d="M479.928-274.022q16.463 0 27.398-10.743 10.935-10.743 10.935-27.206 0-16.464-10.863-27.518-10.862-11.055-27.326-11.055-16.463 0-27.398 11.037-10.935 11.037-10.935 27.501 0 16.463 10.863 27.224 10.862 10.76 27.326 10.76Zm3.247-158.739q14.499 0 24.195-9.821 9.695-9.82 9.695-24.244v-188.935q0-14.424-9.871-24.244-9.871-9.821-24.369-9.821-14.499 0-24.195 9.821-9.695 9.82-9.695 24.244v188.935q0 14.424 9.871 24.244 9.871 9.821 24.369 9.821Zm-2.876 358.74q-84.202 0-158.041-31.879t-129.159-87.199q-55.32-55.32-87.199-129.201-31.878-73.88-31.878-158.167t31.878-158.2q31.879-73.914 87.161-128.747 55.283-54.832 129.181-86.818 73.899-31.986 158.205-31.986 84.307 0 158.249 31.968 73.942 31.967 128.756 86.768 54.815 54.801 86.79 128.883 31.976 74.083 31.976 158.333 0 84.235-31.986 158.07t-86.818 128.942q-54.833 55.107-128.873 87.169-74.04 32.063-158.242 32.063Zm.201-68.131q140.543 0 238.946-98.752 98.402-98.752 98.402-239.596 0-140.543-98.215-238.946-98.215-98.402-239.753-98.402-140.163 0-238.945 98.215-98.783 98.215-98.783 239.753 0 140.163 98.752 238.945 98.752 98.783 239.596 98.783ZM480-480Z" />
    </svg>
    <div style="font-weight: bold;">Connection lost</div>
</div>
<style>
    #rio-connection-lost-popup .error-box {
        position: absolute;
        top: 2rem;
        left: 50%;
        transform: translateX(-50%);
        width: unset;
        height: unset;

        display: flex;
        align-items: center;
        gap: 0.6rem;

        color: var(--rio-global-danger-bg);
        background: var(--rio-global-neutral-bg);
        padding: 1.5rem 2rem;
        border-radius: 99999px;
        box-shadow: 0 0 1rem var(--rio-global-shadow-color);
    }
</style>
        """
    )


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
    rio_app = rio.App(
        name="My App",
        build=MyAppRoot,
    )
    ```

    You can then run this app, either as a local application in a window:

    ```py
    rio_app.run_in_window()
    ```

    Or you can create and run a webserver:

    ```py
    rio_app.run_as_web_server()
    ```

    Or create a server, without running it. This allows you to start the script
    externally with tools such as uvicorn:

    ```py
    fastapi_app = rio_app.as_fastapi()
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
        ] = default_connection_lost_message,
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
            theme = rio.Theme.from_color()

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
        running_in_window: bool,
        validator_factory: Optional[Callable[[rio.Session], debug.Validator]],
        internal_on_app_start: Optional[Callable[[], None]],
    ) -> fastapi.FastAPI:
        """
        Internal equivalent of `as_fastapi` that takes additional arguments.
        """
        return app_server.AppServer(
            self,
            running_in_window=running_in_window,
            on_session_start=self._on_session_start,
            on_session_end=self._on_session_end,
            default_attachments=self._default_attachments,
            validator_factory=validator_factory,
            internal_on_app_start=internal_on_app_start,
        )

    def as_fastapi(self):
        """
        Return a FastAPI instance that serves this app.

        This method returns a FastAPI instance that serves this app. This allows
        you to run the app with a custom server, such as uvicorn:

        ```py
        rio_app = rio.App(
            name="My App",
            build=MyAppRoot,
        )

        fastapi_app = rio_app.as_fastapi()
        ```

        You can then run this app with uvicorn:

        ```sh
        uvicorn my_app:fastapi_app
        ```
        """
        return self._as_fastapi(
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
        validator_factory: Optional[Callable[[rio.Session], debug.Validator]],
        internal_on_app_start: Optional[Callable[[], None]],
    ) -> None:
        """
        Internal equivalent of `run_as_web_server` that takes additional
        arguments.
        """
        port = _ensure_valid_port(host, port)

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
            running_in_window=False,
            validator_factory=validator_factory,
            internal_on_app_start=internal_on_app_start,
        )

        # Serve
        uvicorn.run(
            fastapi_app,
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
        rio_app = rio.App(
            name="My App",
            build=MyAppRoot,
        )

        rio_app.run_as_web_server()
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
        rio_app = rio.App(
            name="My App",
            build=MyAppRoot,
        )

        rio_app.run_in_browser()
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
        port = _ensure_valid_port(host, port)

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
    ) -> None:
        """
        Runs the app in a local window.

        This method creates a window and displays the app in it. This is great
        if you don't want the complexity of running a web server, or wish to
        package your app as a standalone executable.

        ```py
        rio_app = rio.App(
            name="My App",
            build=MyAppRoot,
        )

        rio_app.run_in_window()
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
                "The `window` extra is required to use `App.run_in_window`. Run `pip install rio[window]` to install it."
            )

        # Unfortunately, WebView must run in the main thread, which makes this
        # tricky. We'll have to banish uvicorn to a background thread, and shut
        # it down when the window is closed.

        host = "localhost"
        port = _ensure_valid_port(host, None)
        url = f"http://{host}:{port}"

        # This lock is released once the server is running
        lock = threading.Lock()
        lock.acquire()

        server: Optional[uvicorn.Server] = None

        # Start the server, and release the lock once it's running
        def run_web_server():
            fastapi_app = self._as_fastapi(
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

            asyncio.run(server.serve())

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


def _choose_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()[1]


def _ensure_valid_port(host: str, port: Optional[int]) -> int:
    if port is None:
        return _choose_free_port(host)

    # if _port_is_in_use(host, port):
    #     raise ValueError(f"The port {host}:{port} is already in use")

    return port
