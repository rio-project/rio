import math
from dataclasses import field
from pathlib import Path
from typing import *  # type: ignore

import rio
import rio.debug
from rio.components.component_base import Component

PROJECT_ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT_DIR / "assets"


class ColorPickerPopup(rio.Component):
    theme: rio.Theme
    title: str
    property_name: str
    on_color_change: Callable[[rio.ColorChangeEvent], None]

    _color: rio.Color = field(init=False)

    def _on_create(self) -> None:
        self._color = getattr(self.theme, self.property_name)

    async def _on_confirm(self, event: rio.ButtonPressEvent) -> None:
        await self._call_event_handler(
            self.on_color_change,
            rio.ColorChangeEvent(self._color),
        )

    def build(self) -> rio.Component:
        return rio.Column(
            rio.ColorPicker(
                color=ColorPickerPopup._color,
                height="grow",
            ),
            rio.Button(
                f"Change {self.title}",
                on_press=self._on_confirm,
            ),
            width=20,
            height=18,
            spacing=1,
            margin=1,
        )


class ColorSwatch(rio.Component):
    theme: rio.Theme
    description: Optional[str]
    heading_fill: rio.FillLike
    text_fill: rio.FillLike
    color_property_names: List[Tuple[str, str, bool]]
    currently_edited_property_name: Optional[str]

    def _on_color_click(self, property_name: str) -> None:
        # Stop picking a color, if the same color was clicked again
        if self.currently_edited_property_name == property_name:
            self.currently_edited_property_name = None
            return

        # Otherwise pick a color
        self.currently_edited_property_name = property_name

    def _on_color_selection_finish(self, event: rio.ColorChangeEvent) -> None:
        if self.currently_edited_property_name is None:
            return

        setattr(self.theme, self.currently_edited_property_name, event.color)
        self.theme = self.theme
        self.currently_edited_property_name = None

    def build(self) -> rio.Component:
        assert len(self.color_property_names) > 0, "Must provide at least one color"

        # Create rectangles for each color
        rects = []
        corner_radius = self.theme.corner_radius_medium

        for ii, (color_nice_name, property_name, changeable) in enumerate(
            self.color_property_names
        ):
            color = getattr(self.theme, property_name)

            # Prepare the content for the rectangle
            if ii == 0:
                # Prepare text styles
                heading_style = self.theme.heading3_style.replace(
                    fill=self.heading_fill,
                )
                text_style = self.theme.text_style.replace(
                    fill=self.text_fill,
                )

                children = [
                    rio.Text(
                        text=color_nice_name,
                        style=heading_style,
                        align_x=0,
                    ),
                ]

                if self.description is not None:
                    children.append(
                        rio.Text(
                            text=self.description,
                            style=text_style,
                            align_x=0,
                        )
                    )

                child = rio.Column(
                    *children,
                    margin_left=1,
                    margin_top=1,
                    margin_bottom=1 if len(self.color_property_names) == 1 else 0.5,
                    spacing=0.4,
                    align_y=0,
                )
            else:
                child = rio.Text(
                    text=color_nice_name,
                    style=self.theme.text_style.replace(
                        fill=self.theme.text_color_for(color),
                    ),
                    margin=0.5,
                )

            # The exact shape depends on this color's position
            corner_radii: List[float] = [0, 0, 0, 0]
            if ii == 0:
                corner_radii[0] = corner_radius
                corner_radii[1] = corner_radius

                if len(self.color_property_names) == 1:
                    corner_radii[2] = corner_radius
                    corner_radii[3] = corner_radius

            elif ii == 1:
                corner_radii[3] = corner_radius

            if ii == len(self.color_property_names) - 1:
                corner_radii[2] = corner_radius

            rects.append(
                rio.Rectangle(
                    child=child,
                    style=rio.BoxStyle(
                        fill=color,
                        corner_radius=tuple(corner_radii),  # type: ignore
                    ),
                    ripple=True,
                    width="grow",
                )
            )

        # Show a colorpicker when clicked
        for ii, rect in enumerate(rects):
            _, property_name, changeable = self.color_property_names[ii]

            if not changeable:
                continue

            rects[ii] = rio.MouseEventListener(
                child=rect,
                on_mouse_up=lambda event, pname=property_name: self._on_color_click(
                    pname
                ),
                width="grow",
            )

        # Combine the rectangles into a single swatch
        if len(rects) == 1:
            swatch = rects[0]
        else:
            swatch = rio.Column(
                rects[0],
                rio.Row(
                    *rects[1:],
                    width="grow",
                ),
                width="grow",
            )

        # If the displayed color is too similar to the surface color, add a
        # border
        surface_color = self.theme.surface_color
        main_color = getattr(self.theme, self.color_property_names[0][1])

        difference = (
            abs(main_color.red - surface_color.red)
            + abs(main_color.green - surface_color.green)
            + abs(main_color.blue - surface_color.blue)
        ) / 3

        if difference < 0.2:
            swatch = rio.Rectangle(
                child=swatch,
                style=rio.BoxStyle(
                    fill=rio.Color.TRANSPARENT,
                    stroke_color=self.theme.text_color_for(surface_color).replace(
                        opacity=0.2
                    ),
                    stroke_width=0.1,
                    corner_radius=corner_radius,
                ),
            )

        # Wrap with a popup
        return rio.Popup(
            anchor=swatch,
            content=ColorPickerPopup(
                theme=self.theme,
                title="Foo",
                property_name="primary_color"
                if self.currently_edited_property_name is None
                else self.currently_edited_property_name,
                on_color_change=self._on_color_selection_finish,
            ),
            direction="right",
            alignment=1,
            gap=1,
            is_open=self.currently_edited_property_name is not None,
        )


class Sidebar(rio.Component):
    theme: rio.Theme

    currently_picked_property_name: Optional[str] = None

    def build(self) -> rio.Component:
        return rio.Card(
            rio.Column(
                ColorSwatch(
                    theme=AppRoot.theme,
                    description="Defines your theme",
                    color_property_names=[
                        ("Primary", "primary_color", True),
                        ("Variant", "primary_color_variant", True),
                    ],
                    heading_fill=self.theme.heading_on_primary_fill,
                    text_fill=self.theme.text_on_primary_color,
                    currently_edited_property_name=Sidebar.currently_picked_property_name,
                ),
                ColorSwatch(
                    theme=AppRoot.theme,
                    description="Adds visual interest",
                    color_property_names=[
                        ("Secondary", "secondary_color", True),
                        ("Variant", "secondary_color_variant", True),
                    ],
                    heading_fill=self.theme.heading_on_secondary_color,
                    text_fill=self.theme.text_on_secondary_color,
                    currently_edited_property_name=Sidebar.currently_picked_property_name,
                ),
                ColorSwatch(
                    theme=AppRoot.theme,
                    description="Provides a neutral background",
                    color_property_names=[
                        ("Surface", "surface_color", True),
                        ("Variant", "surface_color_variant", True),
                        ("Active", "surface_active_color", True),
                        ("Background", "background_color", True),
                    ],
                    heading_fill=self.theme.heading1_style.fill,
                    text_fill=self.theme.text_style.fill,
                    currently_edited_property_name=Sidebar.currently_picked_property_name,
                ),
                ColorSwatch(
                    theme=AppRoot.theme,
                    description="Indicates a positive outcome",
                    color_property_names=[
                        ("Success", "success_color", True),
                        ("Variant", "success_color_variant", True),
                    ],
                    heading_fill=self.theme.text_on_success_color,
                    text_fill=self.theme.text_on_success_color,
                    currently_edited_property_name=Sidebar.currently_picked_property_name,
                ),
                ColorSwatch(
                    theme=AppRoot.theme,
                    description="Indicates that attention is needed",
                    color_property_names=[
                        ("Warning", "warning_color", True),
                        ("Variant", "warning_color_variant", True),
                    ],
                    heading_fill=self.theme.text_on_warning_color,
                    text_fill=self.theme.text_on_warning_color,
                    currently_edited_property_name=Sidebar.currently_picked_property_name,
                ),
                ColorSwatch(
                    theme=AppRoot.theme,
                    description="Indicates a problem",
                    color_property_names=[
                        ("Danger", "danger_color", True),
                        ("Variant", "danger_color_variant", True),
                    ],
                    heading_fill=self.theme.text_on_danger_color,
                    text_fill=self.theme.text_on_danger_color,
                    currently_edited_property_name=Sidebar.currently_picked_property_name,
                ),
                ColorSwatch(
                    theme=AppRoot.theme,
                    description=None,
                    color_property_names=[
                        ("Text on Dark", "text_color_on_dark", True),  # type: ignore
                    ],
                    heading_fill=self.theme.text_color_for(
                        self.theme.text_color_on_dark
                    ),
                    text_fill=self.theme.text_color_for(self.theme.text_color_on_dark),
                    currently_edited_property_name=Sidebar.currently_picked_property_name,
                ),
                ColorSwatch(
                    theme=AppRoot.theme,
                    description=None,
                    color_property_names=[
                        ("Text on Light", "text_color_on_light", True),  # type: ignore
                    ],
                    heading_fill=self.theme.text_color_for(
                        self.theme.text_color_on_light
                    ),
                    text_fill=self.theme.text_color_for(self.theme.text_color_on_light),
                    currently_edited_property_name=Sidebar.currently_picked_property_name,
                ),
                spacing=1,
            ),
            corner_radius=self.theme.corner_radius_large,
        )


class PythonCodeView(rio.Component):
    theme: rio.Theme

    def _python_code(self) -> str:
        return """
import rio

theme = rio.Theme(
    primary_color=rio.Color.RED,
)
"""

    def _markdown_source(self) -> str:
        return f"""
```python
{rio.escape_markdown_code(self._python_code())}
```
"""

    def build(self) -> rio.Component:
        return rio.Card(
            rio.MarkdownView(
                text=self._markdown_source(),
            ),
            corner_radius=self.theme.corner_radius_medium,
        )


class AppRoot(rio.Component):
    theme: rio.Theme = field(default_factory=rio.Theme)

    def build(self) -> rio.Component:
        return rio.Row(
            Sidebar(
                theme=self.theme,
                width=20,
                margin_left=3,
                align_y=0.5,
            ),
            rio.Container(
                rio.Column(
                    rio.Text(
                        "Placeholder",
                    ),
                    PythonCodeView(AppRoot.theme),
                    height="grow",
                    spacing=2,
                    width=50,
                    align_x=0.5,
                    align_y=0,
                ),
                width="grow",
            ),
            width="grow",
        )


rio_app = rio.App(
    name="Theme Picker",
    build=AppRoot,
    assets_dir=Path(__file__).parent / "assets",
)


if __name__ == "__main__":
    rio_app.run_as_web_server(
        port=8001,
        quiet=False,
    )
else:
    app = rio_app.as_fastapi()
