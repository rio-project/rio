from __future__ import annotations

from abc import ABC, abstractproperty
from dataclasses import KW_ONLY, field
from typing import *  # type: ignore
from typing import Optional

import reflex as rx

from ... import common
from .. import fundamental
from . import progress_circle, text, theme

__all__ = [
    "ButtonPressEvent",
    "CustomButton",
    "MinorButton",
    "MajorButton",
]


class ButtonPressEvent:
    pass


class _BaseButton(fundamental.Widget, ABC):
    text: str
    on_press: fundamental.EventHandler[ButtonPressEvent] = None
    _: KW_ONLY
    is_sensitive: bool = True
    is_loading: bool = False
    _is_pressed: bool = field(init=False, default=False)
    _is_entered: bool = field(init=False, default=False)

    def _on_mouse_enter(self, event: fundamental.MouseEnterEvent) -> None:
        self._is_entered = True

    def _on_mouse_leave(self, event: fundamental.MouseLeaveEvent) -> None:
        self._is_entered = False

    def _on_mouse_down(self, event: fundamental.MouseDownEvent) -> None:
        # Only react to left mouse button
        if event.button != fundamental.MouseButton.LEFT:
            return

        self._is_pressed = True

    async def _on_mouse_up(self, event: fundamental.MouseUpEvent) -> None:
        # Only react to left mouse button, and only if sensitive
        if event.button != fundamental.MouseButton.LEFT or not self.is_sensitive:
            return

        await self._call_event_handler(
            self.on_press,
            ButtonPressEvent(),
        )

        self._is_pressed = False

    @abstractproperty
    def _style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        raise NotImplementedError

    @abstractproperty
    def _hover_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        raise NotImplementedError

    @abstractproperty
    def _click_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        raise NotImplementedError

    @abstractproperty
    def _insensitive_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        raise NotImplementedError

    @abstractproperty
    def _transition_speed(self) -> float:
        raise NotImplementedError

    def build(self) -> rx.Widget:
        # If not sensitive, use the insensitive style
        if not self.is_sensitive:
            style, text_style = self._insensitive_style
            hover_style = None

        # If pressed use the click style
        elif self._is_pressed:
            style, text_style = self._click_style
            hover_style = None

        # Otherwise use the regular styles
        else:
            style, text_style = self._style
            hover_style, text_style_hover = self._hover_style
            text_style = text_style_hover if self._is_entered else text_style

        # Prepare the child
        if self.is_loading:
            scale = text_style.font_size
            child = progress_circle.ProgressCircle(
                color=text_style.font_color,
                size=scale * 1.2,
                align_x=0.5,
                margin=0.3,
            )
        else:
            child = text.Text(
                self.text,
                style=text_style,
                margin=0.3,
            )

        return fundamental.MouseEventListener(
            fundamental.Rectangle(
                child=child,
                style=style,
                hover_style=hover_style,
                transition_time=self._transition_speed,
                cursor=common.CursorStyle.POINTER
                if self.is_sensitive
                else common.CursorStyle.DEFAULT,
            ),
            on_mouse_enter=self._on_mouse_enter,
            on_mouse_leave=self._on_mouse_leave,
            on_mouse_down=self._on_mouse_down,
            on_mouse_up=self._on_mouse_up,
        )


class CustomButton(_BaseButton):
    _: KW_ONLY
    style: fundamental.BoxStyle
    hover_style: fundamental.BoxStyle
    click_style: fundamental.BoxStyle
    insensitive_style: fundamental.BoxStyle
    text_style: rx.TextStyle
    text_style_hover: rx.TextStyle
    text_style_click: rx.TextStyle
    text_style_insensitive: rx.TextStyle
    transition_speed: float

    @property
    def _style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        return self.style, self.text_style

    @property
    def _hover_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        return self.hover_style, self.text_style_hover

    @property
    def _click_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        return self.click_style, self.text_style_click

    @property
    def _insensitive_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        return self.insensitive_style, self.text_style_insensitive

    @property
    def _transition_speed(self) -> float:
        return self.transition_speed


class MajorButton(_BaseButton):
    _: KW_ONLY
    color: Optional[rx.Color] = None
    font_color: Optional[rx.Color] = None

    def _get_attributes(self) -> Tuple[theme.Theme, rx.Color, rx.Color]:
        thm = self.session.attachments[theme.Theme]

        return (
            thm,
            thm.main_color if self.color is None else self.color,
            thm.text_style.font_color if self.font_color is None else self.font_color,
        )

    @property
    def _style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        thm, color, font_color = self._get_attributes()

        return (
            fundamental.BoxStyle(
                fill=color,
                corner_radius=thm.corner_radius,
            ),
            rx.TextStyle(
                font_color=font_color,
                font_weight="bold",
            ),
        )

    @property
    def _hover_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        thm, color, font_color = self._get_attributes()

        return (
            fundamental.BoxStyle(
                fill=color.brighter(0.1),
                corner_radius=thm.corner_radius,
            ),
            rx.TextStyle(
                font_color=font_color.contrasting(),
                font_weight="bold",
            ),
        )

    @property
    def _click_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        thm, color, font_color = self._get_attributes()

        return (
            fundamental.BoxStyle(
                fill=color.brighter(0.2),
                corner_radius=thm.corner_radius,
            ),
            rx.TextStyle(
                font_color=font_color.contrasting(),
                font_weight="bold",
            ),
        )

    @property
    def _insensitive_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        thm, color, font_color = self._get_attributes()

        return (
            fundamental.BoxStyle(
                fill=color.desaturated(0.8),
                corner_radius=thm.corner_radius,
            ),
            rx.TextStyle(
                font_color=font_color.desaturated(0.8).contrasting(0.25),
            ),
        )

    @property
    def _transition_speed(self) -> float:
        thm = self.session.attachments[theme.Theme]
        return 0.1 * thm.transition_scale


class MinorButton(_BaseButton):
    _: KW_ONLY
    color: Optional[rx.Color] = None

    def _get_attributes(self) -> Tuple[theme.Theme, rx.Color]:
        thm = self.session.attachments[theme.Theme]

        return (
            thm,
            thm.main_color if self.color is None else self.color,
        )

    @property
    def _style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        thm, color = self._get_attributes()

        return (
            fundamental.BoxStyle(
                fill=rx.Color.TRANSPARENT,
                corner_radius=thm.corner_radius,
                stroke_width=thm.outline_width,
                stroke_color=color,
            ),
            rx.TextStyle(
                font_color=color,
            ),
        )

    @property
    def _hover_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        thm, color = self._get_attributes()

        return (
            fundamental.BoxStyle(
                fill=color.brighter(0.1),
                corner_radius=thm.corner_radius,
                stroke_width=thm.outline_width,
                stroke_color=color.brighter(0.1),
            ),
            rx.TextStyle(
                font_color=color.contrasting(),
            ),
        )

    @property
    def _click_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        thm, color = self._get_attributes()

        return (
            fundamental.BoxStyle(
                fill=color.brighter(0.2),
                corner_radius=thm.corner_radius,
                stroke_width=thm.outline_width,
                stroke_color=color.brighter(0.2),
            ),
            rx.TextStyle(
                font_color=color.contrasting(),
            ),
        )

    @property
    def _insensitive_style(self) -> Tuple[fundamental.BoxStyle, rx.TextStyle]:
        thm, color = self._get_attributes()

        return (
            fundamental.BoxStyle(
                fill=rx.Color.TRANSPARENT,
                corner_radius=thm.corner_radius,
                stroke_width=thm.outline_width,
                stroke_color=color.desaturated(0.8),
            ),
            rx.TextStyle(
                font_color=color.desaturated(0.8).contrasting(),
            ),
        )

    @property
    def _transition_speed(self) -> float:
        thm = self.session.attachments[theme.Theme]
        return 0.1 * thm.transition_scale
