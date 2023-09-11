import reflex as rx

from .. import theme


class HoverCard(rx.Widget):
    alignment: float

    _is_hovered: bool = False

    def _on_mouse_enter(self, event: rx.MouseEnterEvent) -> None:
        self._is_hovered = True

    def _on_mouse_leave(self, event: rx.MouseLeaveEvent) -> None:
        self._is_hovered = False

    def build(self) -> rx.Widget:
        return rx.Stack(
            # Hidden background
            rx.Rectangle(
                style=rx.BoxStyle(
                    fill=rx.Color.RED,
                ),
            ),
            # Cover, hides the background unless hovered
            rx.MouseEventListener(
                rx.Rectangle(
                    style=rx.BoxStyle(
                        fill=rx.Color.TRANSPARENT
                        if self._is_hovered
                        else theme.THEME.surface_color,
                    ),
                    transition_time=1.5,
                ),
                on_mouse_enter=self._on_mouse_enter,
                on_mouse_leave=self._on_mouse_leave,
                height=20,
            ),
            # Content Card
            rx.Rectangle(
                child=rx.Text("Sample Text"),
                style=rx.BoxStyle(
                    fill=theme.THEME.surface_color,
                    corner_radius=theme.LARGE_CORNER_RADIUS,
                    shadow_color=theme.THEME.shadow_color,
                    shadow_radius=theme.THEME.shadow_radius if self._is_hovered else 0,
                ),
                align_x=self.alignment,
                margin_x=2,
                margin_y=5,
                width=20,
                height=15,
            ),
        )
