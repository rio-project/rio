from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Iterable, Optional

import moderngl
import numpy as np

from rectagon import Color

from . import events


class _RenderContext:
    def __init__(
        self,
        window_width: float,
        window_height: float,
        ogl: moderngl.Context,
    ):
        self.window_width = window_width
        self.window_height = window_height
        self.ogl = ogl

        self.rectangle_vbo = ogl.buffer(
            np.array(
                [
                    # TL, TR, BL
                    0,
                    1,
                    1,
                    1,
                    0,
                    0,
                    # TR, BR, BL
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                ],
                dtype="f4",
            )
        )


class Widget(ABC):
    def __init__(
        self,
        *,
        requested_size: float = 0.0,
        requested_width: float = 0.0,
        requested_height: float = 0.0,
        grow: float = 0.0,
        grow_x: float = 0.0,
        grow_y: float = 0.0,
    ):
        if requested_size == 0.0:
            self.requested_width = requested_width
            self.requested_height = requested_height
        else:
            self.requested_width = requested_size
            self.requested_height = requested_size

        if grow == 0.0:
            self.grow_x = grow_x
            self.grow_y = grow_y
        else:
            self.grow_x = grow
            self.grow_y = grow

        self.allocated_left: float = 0.0
        self.allocated_top: float = 0.0
        self.allocated_width: float = 0.0
        self.allocated_height: float = 0.0

    def children(self) -> Iterable["Widget"]:
        return tuple()

    @abstractmethod
    def _update_requested_size(self):
        raise NotImplementedError()

    @abstractmethod
    def _update_allocated_size(self):
        raise NotImplementedError()

    @abstractmethod
    def _draw(self, ctx: _RenderContext):
        raise NotImplementedError()


class Margin(Widget):
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
        super().__init__()

        self.child = child

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

    def children(self) -> Iterable[Widget]:
        yield self.child

    def _update_requested_size(self):
        self.child._update_requested_size()

        self.requested_width = (
            self.child.requested_width + self.margin_left + self.margin_right
        )
        self.requested_height = (
            self.child.requested_height + self.margin_top + self.margin_bottom
        )

        self.grow_x = self.child.grow_x
        self.grow_y = self.child.grow_y

    def _update_allocated_size(self):
        self.child.allocated_left = self.allocated_left + self.margin_left
        self.child.allocated_top = self.allocated_top + self.margin_top

        self.child.allocated_width = max(
            self.allocated_width - self.margin_left - self.margin_right, 0
        )
        self.child.allocated_height = max(
            self.allocated_height - self.margin_top - self.margin_bottom, 0
        )

        self.child._update_allocated_size()

    def _draw(self, ctx: _RenderContext):
        self.child._draw(ctx)


class Align(Widget):
    def __init__(
        self,
        child: Widget,
        *,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        super().__init__()

        self.child = child
        self.align_x = align_x
        self.align_y = align_y

    @classmethod
    def top(cls, child: Widget):
        return cls(child, align_y=0)

    @classmethod
    def bottom(cls, child: Widget):
        return cls(child, align_y=1)

    @classmethod
    def left(cls, child: Widget):
        return cls(child, align_x=0)

    @classmethod
    def right(cls, child: Widget):
        return cls(child, align_x=1)

    @classmethod
    def top_left(cls, child: Widget):
        return cls(child, align_x=0, align_y=0)

    @classmethod
    def top_center(cls, child: Widget):
        return cls(child, align_x=0.5, align_y=0)

    @classmethod
    def top_right(cls, child: Widget):
        return cls(child, align_x=1, align_y=0)

    @classmethod
    def center_left(cls, child: Widget):
        return cls(child, align_x=0, align_y=0.5)

    @classmethod
    def center(cls, child: Widget):
        return cls(child, align_x=0.5, align_y=0.5)

    @classmethod
    def center_right(cls, child: Widget):
        return cls(child, align_x=1, align_y=0.5)

    @classmethod
    def bottom_left(cls, child: Widget):
        return cls(child, align_x=0, align_y=1)

    @classmethod
    def bottom_center(cls, child: Widget):
        return cls(child, align_x=0.5, align_y=1)

    @classmethod
    def bottom_right(cls, child: Widget):
        return cls(child, align_x=1, align_y=1)

    def children(self) -> Iterable[Widget]:
        yield self.child

    def _update_requested_size(self):
        self.child._update_requested_size()

        self.requested_width = self.child.requested_width
        self.requested_height = self.child.requested_height
        self.grow_x = self.child.grow_x
        self.grow_y = self.child.grow_y

    def _update_allocated_size(self):
        def update_size_single(
            align: Optional[float],
            requested: float,
            allocated: float,
        ):
            return allocated if align is None else requested

        self.child.allocated_width = update_size_single(
            self.align_x, self.child.requested_width, self.allocated_width
        )

        self.child.allocated_height = update_size_single(
            self.align_y, self.child.requested_height, self.allocated_height
        )

        def update_position_single(
            self_position: float,
            align: Optional[float],
            requested: float,
            allocated: float,
        ):
            if align is None:
                return self_position
            else:
                return self_position + align * max(allocated - requested, 0)

        self.child.allocated_left = update_position_single(
            self.allocated_left,
            self.align_x,
            self.child.requested_width,
            self.allocated_width,
        )

        self.child.allocated_top = update_position_single(
            self.allocated_top,
            self.align_y,
            self.child.requested_height,
            self.allocated_height,
        )

    def _draw(self, ctx: _RenderContext):
        self.child._draw(ctx)


def _linear_container_update_requested_size(
    parent: Widget,
    children: Iterable[Widget],
    horizontal: bool,
):
    # Prepare names for the two axes. These will be used with getattr() and
    # setattr() later
    if horizontal:
        main_requested_size_name = "requested_width"
        cross_requested_size_name = "requested_height"
        main_grow_name = "grow_x"
        cross_grow_name = "grow_y"
    else:
        main_requested_size_name = "requested_height"
        cross_requested_size_name = "requested_width"
        main_grow_name = "grow_y"
        cross_grow_name = "grow_x"

    # Instead of setattr-ing the values every iteration, keep them in variables
    # for speed, then set them once at the end
    main_requested_size = 0
    cross_requested_size = 0
    main_grow = 0
    cross_grow = 0

    # Process all children
    for child in children:
        child._update_requested_size()

        main_requested_size += getattr(child, main_requested_size_name)
        cross_requested_size = max(
            cross_requested_size, getattr(child, cross_requested_size_name)
        )

        main_grow += getattr(child, main_grow_name)
        cross_grow = max(cross_grow, getattr(child, cross_grow_name))

    # Set the values in the parent
    setattr(parent, main_requested_size_name, main_requested_size)
    setattr(parent, cross_requested_size_name, cross_requested_size)
    setattr(parent, main_grow_name, main_grow)
    setattr(parent, cross_grow_name, cross_grow)


def _linear_container_update_allocated_size(
    parent: Widget,
    children: Iterable[Widget],
    horizontal: bool,
):
    # Prepare names for the two axes. These will be used with getattr() and
    # setattr() later
    if horizontal:
        main_requested_size_name = "requested_width"
        main_grow_name = "grow_x"
        main_allocated_start_name = "allocated_left"
        cross_allocated_start_name = "allocated_top"
        main_allocated_size_name = "allocated_width"
        cross_allocated_size_name = "allocated_height"
    else:
        main_requested_size_name = "requested_height"
        main_grow_name = "grow_y"
        main_allocated_start_name = "allocated_top"
        cross_allocated_start_name = "allocated_left"
        main_allocated_size_name = "allocated_height"
        cross_allocated_size_name = "allocated_width"

    # Prepare common variables
    main_pos = getattr(parent, main_allocated_start_name)
    superfluously_allocated_size = max(
        getattr(parent, main_allocated_size_name)
        - getattr(parent, main_requested_size_name),
        0,
    )
    cross_start = getattr(parent, cross_allocated_start_name)
    parent_main_grow = getattr(parent, main_grow_name)
    parent_cross_allocated_size = getattr(parent, cross_allocated_size_name)

    # Process all children
    for child in children:
        setattr(child, main_allocated_start_name, main_pos)
        setattr(child, cross_allocated_start_name, cross_start)

        if parent_main_grow == 0:
            expansion_factor = 0.0
        else:
            expansion_factor = getattr(child, main_grow_name) / parent_main_grow

        setattr(
            child,
            main_allocated_size_name,
            getattr(child, main_requested_size_name)
            + superfluously_allocated_size * expansion_factor,
        )
        setattr(child, cross_allocated_size_name, parent_cross_allocated_size)

        child._update_allocated_size()

        main_pos += getattr(child, main_allocated_size_name)


class Row(Widget):
    def __init__(self, *children: Widget):
        super().__init__()
        self._children = children

    def children(self) -> Iterable[Widget]:
        return self._children

    def _update_requested_size(self):
        _linear_container_update_requested_size(
            self,
            self._children,
            horizontal=True,
        )

    def _update_allocated_size(self):
        _linear_container_update_allocated_size(
            self,
            self._children,
            horizontal=True,
        )

    def _draw(self, ctx: _RenderContext):
        for child in self.children():
            child._draw(ctx)


class Column(Widget):
    def __init__(self, *children: Widget):
        super().__init__()
        self._children = children

    def children(self) -> Iterable[Widget]:
        return self._children

    def _update_requested_size(self):
        _linear_container_update_requested_size(
            self,
            self._children,
            horizontal=False,
        )

    def _update_allocated_size(self):
        _linear_container_update_allocated_size(
            self,
            self._children,
            horizontal=False,
        )

    def _draw(self, ctx: _RenderContext):
        for child in self.children():
            child._draw(ctx)


class Stack(Widget):
    def __init__(self, *children: Widget):
        super().__init__()
        self._children = children

    def children(self) -> Iterable[Widget]:
        return self._children

    def _update_requested_size(self):
        self.requested_height = 0
        self.requested_width = 0
        self.grow_x = 0
        self.grow_y = 0

        for child in self.children():
            child._update_requested_size()

            self.requested_height = max(self.requested_height, child.requested_height)
            self.requested_width = max(self.requested_width, child.requested_width)
            self.grow_x = max(self.grow_x, child.grow_x)
            self.grow_y = max(self.grow_y, child.grow_y)

    def _update_allocated_size(self):
        for child in self.children():
            child.allocated_left = self.allocated_left
            child.allocated_top = self.allocated_top
            child.allocated_height = self.allocated_height
            child.allocated_width = self.allocated_width

            child._update_allocated_size()

    def _draw(self, ctx: _RenderContext):
        for child in self.children():
            child._draw(ctx)


class Spacer(Widget):
    def _update_requested_size(self):
        pass

    def _update_allocated_size(self):
        pass

    def _draw(self, ctx: _RenderContext):
        pass


class Override(Widget):
    def __init__(
        self,
        child: Widget,
        *,
        requested_size: Optional[float] = None,
        requested_width: Optional[float] = None,
        requested_height: Optional[float] = None,
        grow: Optional[float] = None,
        grow_x: Optional[float] = None,
        grow_y: Optional[float] = None,
    ):

        super().__init__()

        if requested_size is not None:
            self._override_requested_width = requested_size
            self._override_requested_height = requested_size
        else:
            self._override_requested_width = requested_width
            self._override_requested_height = requested_height

        if grow is not None:
            self._override_grow_x = grow
            self._override_grow_y = grow
        else:
            self._override_grow_x = grow_x
            self._override_grow_y = grow_y

        self._child = child

    def children(self) -> Iterable[Widget]:
        return (self._child,)

    def _update_requested_size(self):
        self._child._update_requested_size()

        self.requested_width = (
            self._child.requested_width
            if self._override_requested_width is None
            else self._override_requested_width
        )
        self.requested_height = (
            self._child.requested_height
            if self._override_requested_height is None
            else self._override_requested_height
        )

        self.grow_x = (
            self._child.grow_x
            if self._override_grow_x is None
            else self._override_grow_x
        )
        self.grow_y = (
            self._child.grow_y
            if self._override_grow_y is None
            else self._override_grow_y
        )

    def _update_allocated_size(self):
        self._child.allocated_left = self.allocated_left
        self._child.allocated_top = self.allocated_top
        self._child.allocated_height = self.allocated_height
        self._child.allocated_width = self.allocated_width

        self._child._update_allocated_size()

    def _draw(self, ctx: _RenderContext):
        self._child._draw(ctx)


class Rectangle(Widget):
    def __init__(
        self,
        *,
        requested_size: float = 0.0,
        requested_width: float = 0.0,
        requested_height: float = 0.0,
        grow: float = 0.0,
        grow_x: float = 0.0,
        grow_y: float = 0.0,
        color: Color = Color.WHITE,
    ):
        super().__init__(
            requested_size=requested_size,
            requested_width=requested_width,
            requested_height=requested_height,
            grow=grow,
            grow_x=grow_x,
            grow_y=grow_y,
        )

        self._color = color
        self._vao: Optional[moderngl.VertexArray] = None

    def _init_gl(self, ctx: _RenderContext) -> moderngl.VertexArray:
        self._prog = ctx.ogl.program(
            vertex_shader="""
                #version 330

                uniform vec2 scale;
                uniform vec2 offset;

                in vec2 in_vert;

                out vec2 rectCoord;

                void main() {
                    rectCoord = in_vert;

                    vec2 pos2d = offset + in_vert * scale;
                    pos2d.x = pos2d.x * 2.0 - 1.0;
                    pos2d.y = (1.0 - pos2d.y) * 2.0 - 1.0;

                    gl_Position = vec4(pos2d, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330

                uniform vec2 scale;
                uniform vec4 color;

                in vec2 rectCoord;

                out vec4 f_color;

                void main() {
                    // Distance to border, for debugging
                    vec2 border_vector = abs(vec2(0.5) - rectCoord);
                    float border_distance = max(border_vector.x, border_vector.y);
                    float border_factor = smoothstep(0.96, 1.0, 2.0 * border_distance);

                    // Color calculation
                    f_color = vec4(color.rgb - border_factor, 1.0);
                    // f_color = vec4(rectCoord, 0.0, 1.0);

                    // Gama correction
                    // f_color = vec4(
                    //     pow(f_color.rgb, vec3(2.2)),
                    //     f_color.a
                    // );
                }
            """,
        )

        return ctx.ogl.vertex_array(
            self._prog,
            ctx.rectangle_vbo,
            "in_vert",
        )

    def _update_requested_size(self):
        pass

    def _update_allocated_size(self):
        pass

    def _draw(self, ctx: _RenderContext):
        if self._vao is None:
            self._vao = self._init_gl(ctx)

        self._prog["scale"].value = (  # type: ignore
            self.allocated_width / ctx.window_width,
            self.allocated_height / ctx.window_height,
        )
        self._prog["offset"].value = (  # type: ignore
            self.allocated_left / ctx.window_width,
            self.allocated_top / ctx.window_height,
        )
        self._prog["color"].value = self._color.rgba  # type: ignore

        self._vao.render()


class Text(Widget):
    def __init__(
        self,
        text: str,
        *,
        font_name: str = "sans-serif",
        font_size: float = 12.0,
        color: Color = Color.BLACK,
    ):
        super().__init__()

        self.text = text
        font_name = font_name
        self.font_size = font_size
        self.color = color

        self.vao: Optional[moderngl.VertexArray] = None


class Button(Widget):
    def __init__(
        self,
        child: Widget,
        on_click: Optional[Callable[[events.ButtonEventData], Awaitable[None]]] = None,
    ):
        super().__init__()

        self.child = child
        self.on_click = events.EventSlot(on_click)
