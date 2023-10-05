import rio

from .. import theme


class HoverCard(rio.Component):
    alignment: float

    _is_hovered: bool = False

    def _on_mouse_enter(self, event: rio.MouseEnterEvent) -> None:
        self._is_hovered = True

    def _on_mouse_leave(self, event: rio.MouseLeaveEvent) -> None:
        self._is_hovered = False

    def build(self) -> rio.Component:
        return rio.Stack(
            # Hidden background
            rio.Rectangle(
                style=rio.BoxStyle(
                    fill=rio.Color.RED,
                ),
            ),
            # Cover, hides the background unless hovered
            rio.MouseEventListener(
                rio.Rectangle(
                    style=rio.BoxStyle(
                        fill=rio.Color.TRANSPARENT
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
            rio.Rectangle(
                child=rio.Text("Sample Text"),
                style=rio.BoxStyle(
                    fill=theme.THEME.surface_color,
                    corner_radius=theme.THEME.corner_radius_large,
                    shadow_color=theme.THEME.shadow_color,
                    shadow_radius=1.0 if self._is_hovered else 0,
                ),
                align_x=self.alignment,
                margin_x=2,
                margin_y=5,
                width=20,
                height=15,
            ),
        )
