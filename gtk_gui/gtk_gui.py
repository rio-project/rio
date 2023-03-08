import os
import gi
from abc import ABC, abstractmethod

# Disable wayland before importing Gdk. This is necessary, as initializing VLC
# on wayland is different/impossible. `Gdk.set_allowed_backends("x11")` does
# exist, but doesn't appear to have any effect.
os.environ["GDK_BACKEND"] = "x11"

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, Gtk
import cairo


from pathlib import Path
from typing import (
    Optional,
    List,
    Union,
    AsyncIterator,
    Iterable,
    Awaitable,
    Callable,
    Dict,
    Any,
    Tuple,
    AsyncIterable,
)
import asyncio
import time


# Enable Gtk's dark theme
settings = Gtk.Settings.get_default()

if settings is None:
    raise ImportError("Can't fetch Gtk.Settings. Running in terminal?")

settings.set_property("gtk-application-prefer-dark-theme", True)


def queue_async(func: Callable[..., Awaitable]):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.create_task(func(*args, **kwargs))  # type: ignore

    return wrapper


# def get_screen_size(display: Optional[Gdk.Display]) -> Tuple[int, int]:
#     if display is None:
#         display = Gdk.Display.get_default()

#         if display is None:
#             raise RuntimeError(
#                 "Cannot get the primary display. Is the app running in terminal?"
#             )

#     mon_geoms = [
#         display.get_monitor(i).get_geometry() for i in range(display.get_n_monitors())
#     ]

#     x0 = min(r.x for r in mon_geoms)
#     y0 = min(r.y for r in mon_geoms)
#     x1 = max(r.x + r.width for r in mon_geoms)
#     y1 = max(r.y + r.height for r in mon_geoms)

#     return x1 - x0, y1 - y0


class App:
    def __init__(self, name: str, identifier: str):
        self.name = name
        self.identifier = identifier
        self._stop_event = asyncio.Event()
        self._windows: List["Window"] = []

    @property
    def cache_directory(self) -> Path:
        raise NotImplementedError("TODO")

    @property
    def config_directory(self) -> Path:
        raise NotImplementedError("TODO")

    def create_window(
        self,
        widget: "Widget",
        *,
        title: Optional[str] = None,
        size: tuple[int, int] = (800, 600),
        resizable: bool = True,
    ) -> "Window":
        window = Window(
            app=self,
            widget=widget,
            title=self.name if title is None else title,
            size=size,
            resizable=resizable,
        )

        self._windows.append(window)
        return window

    async def run(self) -> None:
        # Make sure the app is only run once
        if self._stop_event.is_set():
            raise RuntimeError(
                "The app has already been run. Apps may only be used once. Create a new App instance to run again."
            )

        # Show all windows
        for window in self._windows:
            window._gtk_window.show_all()

        # Enter the main loop
        try:
            while True:
                # Wait for the stop event, but don't block for too long
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=1 / 60)

                # On timeout, process all Gtk events
                except asyncio.TimeoutError:
                    while Gtk.events_pending():
                        Gtk.main_iteration_do(blocking=False)

                # The stop event was set, so stop the app
                else:
                    break

        # Finally, clean up all Gtk windows
        finally:
            for window in self._windows:
                window._gtk_window.destroy()

            self._windows.clear()

    async def stop(self) -> None:
        self._stop_event.set()


class Window:
    def __init__(
        self,
        app: App,
        widget: "Widget",
        title: str,
        size: tuple[int, int],
        resizable: bool = True,
    ):
        self.app = app

        self._gtk_window = Gtk.Window(
            title=title,
            default_height=size[1],
            default_width=size[0],
            resizable=resizable,
        )

        self._widget = widget
        self._gtk_window.add(widget._gtk_widget)

    @property
    def title(self) -> str:
        result = self._gtk_window.get_title()
        return "" if result is None else result

    @title.setter
    def title(self, title: str) -> None:
        self._gtk_window.props.title = title

    @property
    def size(self) -> Tuple[int, int]:
        return self._gtk_window.get_size()

    @size.setter
    def size(self, size: Tuple[int, int]) -> None:
        self._gtk_window.resize(*size)

    @property
    def resizable(self) -> bool:
        return self._gtk_window.get_resizable()

    @resizable.setter
    def resizable(self, resizable: bool) -> None:
        self._gtk_window.props.resizeable = resizable

    @property
    def widget(self) -> "Widget":
        return self._widget

    @widget.setter
    def widget(self, widget: "Widget") -> None:
        self._widget = widget
        self._gtk_window.remove(self._gtk_window.get_child())
        self._gtk_window.add(widget._gtk_widget)


class Widget(ABC):
    _gtk_widget: Gtk.Widget

    def __init__(
        self,
        gtk_widget: Gtk.Widget,
        grow: bool = False,
        grow_x: bool = False,
        grow_y: bool = False,
    ):
        if grow:
            grow_x = True
            grow_y = True

        self._gtk_widget = gtk_widget

        self._gtk_widget.props.halign = Gtk.Align.FILL
        self._gtk_widget.props.valign = Gtk.Align.FILL

        self.grow_x = grow_x
        self.grow_y = grow_y

    @property
    def grow_x(self) -> bool:
        return self._gtk_widget.get_hexpand()

    @grow_x.setter
    def grow_x(self, x_expand: bool) -> None:
        self._gtk_widget.props.hexpand = x_expand

    @property
    def grow_y(self) -> bool:
        return self._gtk_widget.get_vexpand()

    @grow_y.setter
    def grow_y(self, y_expand: bool) -> None:
        self._gtk_widget.props.vexpand = y_expand


class Label(Widget):
    _gtk_widget: Gtk.Label

    def __init__(
        self,
        text: str,
        *,
        grow: bool = False,
        grow_x: bool = False,
        grow_y: bool = False,
    ):
        super().__init__(
            Gtk.Label(text),
            grow=grow,
            grow_x=grow_x,
            grow_y=grow_y,
        )

    @property
    def text(self) -> str:
        return self._gtk_widget.get_text()

    @text.setter
    def text(self, text: str) -> None:
        self._gtk_widget.props.text = text


class Button(Widget):
    _gtk_widget: Gtk.Button

    def __init__(
        self,
        child: Union[Widget, str],
        *,
        grow: bool = False,
        grow_x: bool = False,
        grow_y: bool = False,
        on_press: Optional[Callable[[], None]] = None,
    ):
        if isinstance(child, str):
            child = Label(child)

        super().__init__(
            Gtk.Button(),
            grow=grow,
            grow_x=grow_x,
            grow_y=grow_y,
        )

        self._gtk_widget.add(child._gtk_widget)

        if on_press is not None:
            self._gtk_widget.connect("clicked", lambda _: on_press())


class _LinearContainer(Widget):
    _gtk_widget: Gtk.Box

    def __init__(self, *children: Widget, horizontal: bool):
        super().__init__(
            Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL
                if horizontal
                else Gtk.Orientation.VERTICAL
            ),
            grow_x=any(child.grow_x for child in children),
            grow_y=any(child.grow_y for child in children),
        )

        self.children = list(children)

        for child in children:
            self._gtk_widget.pack_start(
                child._gtk_widget,
                child.grow_x if horizontal else child.grow_y,
                True,
                0,
            )

            self._gtk_widget.add(child._gtk_widget)


class Row(_LinearContainer):
    def __init__(self, *children: Widget):
        super().__init__(*children, horizontal=True)


class Column(_LinearContainer):
    def __init__(self, *children: Widget):
        super().__init__(*children, horizontal=False)


class Margin(Widget):
    _gtk_widget: Gtk.Bin

    def __init__(
        self,
        child: Widget,
        *,
        margin: float = 0,
        margin_horizontal: float = 0,
        margin_vertical: float = 0,
        margin_left: float = 0,
        margin_top: float = 0,
        margin_right: float = 0,
        margin_bottom: float = 0,
    ):
        super().__init__(
            Gtk.Bin(),
            grow_x=child.grow_x,
            grow_y=child.grow_y,
        )

        self.child = child

        # Get the effective margin values
        if margin != 0:
            self.margin_left = margin
            self.margin_top = margin
            self.margin_right = margin
            self.margin_bottom = margin

        elif margin_horizontal != 0:
            self.margin_left = margin_horizontal
            self.margin_top = 0
            self.margin_right = margin_horizontal
            self.margin_bottom = 0

        elif margin_vertical != 0:
            self.margin_left = 0
            self.margin_top = margin_vertical
            self.margin_right = 0
            self.margin_bottom = margin_vertical

        else:
            self.margin_left = margin_left
            self.margin_top = margin_top
            self.margin_right = margin_right
            self.margin_bottom = margin_bottom

        # Create the Gtk widget
        self._gtk_widget.add(child._gtk_widget)
        self._gtk_widget.props.margin_left = round(self.margin_left)
        self._gtk_widget.props.margin_top = round(self.margin_top)
        self._gtk_widget.props.margin_right = round(self.margin_right)
        self._gtk_widget.props.margin_bottom = round(self.margin_bottom)


# class PictureWidget(Gtk.DrawingArea):
#     def __init__(
#         self,
#         *,
#         source_path: Path,
#     ):
#         assert isinstance(source_path, Path)

#         super().__init__()

#         pixbuf = GdkPixbuf.PixbufAnimation.new_from_file(os.fspath(source_path))

#         if pixbuf.is_static_image():
#             self._pixbuf = pixbuf.get_static_image()
#             self._animation_iter = None
#         else:
#             self._pixbuf = None
#             self._animation_iter = pixbuf.get_iter(None)

#             iter_task = asyncio.create_task(self._iter_animation())
#             self.connect("destroy", lambda *args: iter_task.cancel())

#     async def _iter_animation(self):
#         assert self._animation_iter is not None

#         while True:
#             # Get the next frame
#             self._animation_iter.advance(None)
#             self.queue_draw()

#             # Wait for the next frame
#             delay = self._animation_iter.get_delay_time()

#             # A delay of -1 means the animation is over
#             if delay == -1:
#                 break

#             await asyncio.sleep(delay / 1000)

#     def do_draw(self, ctx: cairo.Context):
#         # Get the current pixbuf
#         if self._animation_iter is not None:
#             pixbuf = self._animation_iter.get_pixbuf()
#         else:
#             assert self._pixbuf is not None
#             pixbuf = self._pixbuf

#         allocated_width = self.get_allocated_width()
#         allocated_height = self.get_allocated_height()
#         pixbuf_width = pixbuf.get_width()
#         pixbuf_height = pixbuf.get_height()

#         scale_factor = min(
#             allocated_width / pixbuf_width,
#             allocated_height / pixbuf_height,
#         )

#         scaled_x = round(pixbuf_width * scale_factor)
#         scaled_y = round(pixbuf_height * scale_factor)

#         offset_x = (allocated_width - scaled_x) * 0.5
#         offset_y = (allocated_height - scaled_y) * 0.5

#         # Draw a background
#         ctx.set_source_rgb(0, 0, 0)
#         ctx.paint()

#         # Draw the image
#         ctx.scale(scale_factor, scale_factor)
#         surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, 1, None)
#         ctx.set_source_surface(
#             surface,
#             offset_x / scale_factor,
#             offset_y / scale_factor,
#         )
#         ctx.paint()
