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
        return rio.Rectangle(
            child=rio.Text("Sample Text"),
            style=rio.BoxStyle(
                fill=theme.THEME.neutral_palette.background,
                corner_radius=theme.THEME.corner_radius_large,
                shadow_color=theme.THEME.shadow_color,
                shadow_radius=1.0 if self._is_hovered else 0,
            ),
            align_x=self.alignment,
            margin_x=2,
            margin_y=5,
            width=20,
            height=15,
        )
