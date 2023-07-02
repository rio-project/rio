from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore
from typing import Optional

import reflex as rx

from .. import common, styling, theme
from . import widget_base

__all__ = [
    "Button",
    "ButtonPressedEvent",
]


class ButtonPressedEvent:
    pass


class Button(widget_base.Widget):
    text: str
    on_press: rx.EventHandler[ButtonPressedEvent] = None
    _: KW_ONLY
    style: rx.BoxStyle
    hover_style: rx.BoxStyle
    click_style: rx.BoxStyle
    insensitive_style: rx.BoxStyle
    text_style: rx.TextStyle
    text_style_hover: rx.TextStyle
    text_style_click: rx.TextStyle
    text_style_insensitive: rx.TextStyle
    transition_speed: float
    is_sensitive: bool = True
    is_loading: bool = False
    _is_pressed: bool = False
    _is_entered: bool = False

    @classmethod
    def major(
        cls,
        text: str,
        on_press: rx.EventHandler[ButtonPressedEvent] = None,
        *,
        is_sensitive: bool = True,
        is_loading: bool = False,
        font_color: rx.Color = theme.COLOR_FONT,
        accent_color: rx.Color = theme.COLOR_ACCENT,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["natural", "grow"], float] = "natural",
        height: Union[Literal["natural", "grow"], float] = "natural",
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        return cls(
            text,
            on_press,
            is_sensitive=is_sensitive,
            is_loading=is_loading,
            style=rx.BoxStyle(
                fill=accent_color,
                corner_radius=theme.CORNER_RADIUS,
            ),
            hover_style=rx.BoxStyle(
                fill=accent_color.brighter(0.1),
                corner_radius=theme.CORNER_RADIUS,
            ),
            click_style=rx.BoxStyle(
                fill=accent_color.brighter(0.2),
                corner_radius=theme.CORNER_RADIUS,
            ),
            insensitive_style=rx.BoxStyle(
                fill=accent_color.desaturated(0.8),
                corner_radius=theme.CORNER_RADIUS,
            ),
            text_style=rx.TextStyle(
                font_color=font_color,
                font_weight="bold",
            ),
            text_style_hover=rx.TextStyle(
                font_color=accent_color.contrasting(),
                font_weight="bold",
            ),
            text_style_click=rx.TextStyle(
                font_color=accent_color.contrasting(),
                font_weight="bold",
            ),
            text_style_insensitive=rx.TextStyle(
                font_color=accent_color.desaturated(0.8).contrasting(0.25),
            ),
            transition_speed=theme.TRANSITION_FAST,
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

    @classmethod
    def minor(
        cls,
        text: str,
        on_press: rx.EventHandler[ButtonPressedEvent] = None,
        *,
        is_sensitive: bool = True,
        is_loading: bool = False,
        accent_color: rx.Color = theme.COLOR_ACCENT,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["natural", "grow"], float] = "natural",
        height: Union[Literal["natural", "grow"], float] = "natural",
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        base_style = rx.BoxStyle(
            fill=styling.Color.TRANSPARENT,
            corner_radius=theme.CORNER_RADIUS,
            stroke_width=theme.OUTLINE_WIDTH,
            stroke_color=accent_color,
        )

        return cls(
            text,
            on_press,
            is_sensitive=is_sensitive,
            is_loading=is_loading,
            style=base_style,
            hover_style=base_style.replace(
                fill=accent_color.brighter(0.1),
                stroke_color=accent_color.brighter(0.1),
            ),
            click_style=base_style.replace(
                fill=accent_color.brighter(0.2),
                stroke_color=accent_color.brighter(0.2),
            ),
            insensitive_style=base_style.replace(
                stroke_color=accent_color.desaturated(0.8),
            ),
            text_style=rx.TextStyle(
                font_color=accent_color,
            ),
            text_style_hover=rx.TextStyle(
                font_color=accent_color.contrasting(),
            ),
            text_style_click=rx.TextStyle(
                font_color=accent_color.contrasting(),
            ),
            text_style_insensitive=rx.TextStyle(
                font_color=accent_color.desaturated(0.8).contrasting(),
            ),
            transition_speed=theme.TRANSITION_FAST,
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

    def _on_mouse_enter(self, event: rx.MouseEnterEvent) -> None:
        self._is_entered = True

    def _on_mouse_leave(self, event: rx.MouseLeaveEvent) -> None:
        self._is_entered = False

    def _on_mouse_down(self, event: rx.MouseDownEvent) -> None:
        # Only react to left mouse button
        if event.button != rx.MouseButton.LEFT:
            return

        self._is_pressed = True

    async def _on_mouse_up(self, event: rx.MouseUpEvent) -> None:
        # Only react to left mouse button, and only if sensitive
        if event.button != rx.MouseButton.LEFT or not self.is_sensitive:
            return

        await self._call_event_handler(
            self.on_press,
            ButtonPressedEvent(),
        )

        self._is_pressed = False

    def build(self) -> rx.Widget:
        # If not sensitive, use the insensitive styles
        if not self.is_sensitive:
            style = self.insensitive_style
            hover_style = None
            text_style = self.text_style_insensitive

        # If pressed use the click styles
        elif self._is_pressed:
            style = self.click_style
            hover_style = None
            text_style = self.text_style_click

        # Otherwise use the regular styles
        else:
            style = self.style
            hover_style = self.hover_style
            text_style = self.text_style_hover if self._is_entered else self.text_style

        # Prepare the child
        if self.is_loading:
            scale = text_style.font_size
            child = rx.ProgressCircle(
                color=text_style.font_color,
                size=scale * 1.2,
                align_x=0.5,
                margin=0.3,
            )
        else:
            child = rx.Text(
                self.text,
                style=text_style,
                margin=0.3,
            )

        return rx.MouseEventListener(
            rx.Rectangle(
                child=child,
                style=style,
                hover_style=hover_style,
                transition_time=theme.TRANSITION_FAST,
                cursor=common.CursorStyle.POINTER
                if self.is_sensitive
                else common.CursorStyle.DEFAULT,
            ),
            on_mouse_enter=self._on_mouse_enter,
            on_mouse_leave=self._on_mouse_leave,
            on_mouse_down=self._on_mouse_down,
            on_mouse_up=self._on_mouse_up,
        )
