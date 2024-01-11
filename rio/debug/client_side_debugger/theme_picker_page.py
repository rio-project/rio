import functools
from typing import *  # type: ignore

import rio


class PalettePicker(rio.Component):
    shared_open_key: str

    palette_nicename: str
    palette_attribute_name: str

    pick_opacity: bool = False

    round_top: bool = False
    round_bottom: bool = False

    @property
    def palette(self) -> rio.Palette:
        return getattr(self.session.theme, self.palette_attribute_name)

    async def _on_color_change(self, event: rio.ColorChangeEvent) -> None:
        replace_kwargs: Any = {
            self.palette_attribute_name: rio.Palette.from_color(event.color, True)
        }
        new_theme = self.session.theme.replace(**replace_kwargs)

        await self.session._apply_theme(new_theme)
        await self.force_refresh()

    def _on_press(self, event: rio.PressEvent) -> None:
        # Toggle the popup
        if self.shared_open_key == self.palette_nicename:
            self.shared_open_key = ""
        else:
            self.shared_open_key = self.palette_nicename

    def build(self) -> rio.Component:
        palette = self.palette

        top_radius = self.session.theme.corner_radius_medium if self.round_top else 0
        bottom_radius = (
            self.session.theme.corner_radius_medium if self.round_bottom else 0
        )

        return rio.Popup(
            anchor=rio.MouseEventListener(
                rio.Rectangle(
                    child=rio.Column(
                        rio.Text(
                            self.palette_nicename,
                            style=rio.TextStyle(
                                font_size=self.session.theme.heading3_style.font_size,
                                fill=palette.foreground,
                            ),
                            selectable=False,
                            align_x=0,
                        ),
                        rio.Text(
                            f"#{palette.background.hex}",
                            style=rio.TextStyle(
                                font_size=1,
                                fill=palette.foreground.replace(opacity=0.5),
                            ),
                            align_x=0,
                        ),
                        spacing=0.2,
                        margin_x=1,
                        margin_y=0.8,
                    ),
                    style=rio.BoxStyle(
                        fill=palette.background,
                        corner_radius=(
                            top_radius,
                            top_radius,
                            bottom_radius,
                            bottom_radius,
                        ),
                    ),
                    ripple=True,
                    transition_time=0.15,
                ),
                on_press=self._on_press,
            ),
            content=rio.Column(
                rio.Text(
                    f"{self.palette_nicename} Background",
                    style="heading2",
                ),
                rio.ColorPicker(
                    color=palette.background,
                    pick_opacity=self.pick_opacity,
                    on_change=self._on_color_change,
                    width=18,
                    height=16,
                ),
                spacing=0.8,
                margin=1,
            ),
            is_open=self.shared_open_key == self.palette_nicename,
            color="hud",
            direction="left",
            gap=1,
        )


class ThemePickerPage(rio.Component):
    shared_open_key: str = ""

    async def _on_radius_change(
        self,
        radius_name: str,
        event: rio.SliderChangeEvent,
    ) -> None:
        replace_kwargs: Any = {
            radius_name: event.value,
        }
        new_theme = self.session.theme.replace(**replace_kwargs)

        await self.session._apply_theme(new_theme)
        await self.force_refresh()

    def build(self) -> rio.Component:
        # Prepare the radius sliders
        slider_min = 0
        slider_max = 4
        radius_sliders = rio.Grid(
            (
                rio.Text("Small"),
                rio.Slider(
                    value=self.session.theme.corner_radius_small,
                    minimum=slider_min,
                    maximum=slider_max,
                    width="grow",
                    on_change=functools.partial(
                        self._on_radius_change,
                        "corner_radius_small",
                    ),
                ),
            ),
            (
                rio.Text("Medium"),
                rio.Slider(
                    value=self.session.theme.corner_radius_medium,
                    minimum=slider_min,
                    maximum=slider_max,
                    width="grow",
                    on_change=functools.partial(
                        self._on_radius_change,
                        "corner_radius_medium",
                    ),
                ),
            ),
            (
                rio.Text("Large"),
                rio.Slider(
                    value=self.session.theme.corner_radius_large,
                    minimum=slider_min,
                    maximum=slider_max,
                    width="grow",
                    on_change=functools.partial(
                        self._on_radius_change,
                        "corner_radius_large",
                    ),
                ),
            ),
        )

        # Combine everything
        return rio.ScrollContainer(
            child=rio.Column(
                # Main Colors
                rio.Text(
                    "Theme Colors",
                    style="heading2",
                    margin_bottom=1,
                    align_x=0,
                ),
                PalettePicker(
                    shared_open_key=ThemePickerPage.shared_open_key,
                    palette_nicename="Primary",
                    palette_attribute_name="primary_palette",
                    round_top=True,
                ),
                PalettePicker(
                    shared_open_key=ThemePickerPage.shared_open_key,
                    palette_nicename="Secondary",
                    palette_attribute_name="secondary_palette",
                    round_bottom=True,
                ),
                # Neutral Colors
                PalettePicker(
                    shared_open_key=ThemePickerPage.shared_open_key,
                    palette_nicename="Background",
                    palette_attribute_name="background_palette",
                    margin_top=1,
                    round_top=True,
                ),
                PalettePicker(
                    shared_open_key=ThemePickerPage.shared_open_key,
                    palette_nicename="Neutral",
                    palette_attribute_name="neutral_palette",
                ),
                PalettePicker(
                    shared_open_key=ThemePickerPage.shared_open_key,
                    palette_nicename="HUD",
                    palette_attribute_name="hud_palette",
                    pick_opacity=True,
                ),
                PalettePicker(
                    shared_open_key=ThemePickerPage.shared_open_key,
                    palette_nicename="Disabled",
                    palette_attribute_name="disabled_palette",
                    round_bottom=True,
                ),
                # Semantic Colors
                PalettePicker(
                    shared_open_key=ThemePickerPage.shared_open_key,
                    palette_nicename="Success",
                    palette_attribute_name="success_palette",
                    margin_top=1,
                    round_top=True,
                ),
                PalettePicker(
                    shared_open_key=ThemePickerPage.shared_open_key,
                    palette_nicename="Warning",
                    palette_attribute_name="warning_palette",
                ),
                PalettePicker(
                    shared_open_key=ThemePickerPage.shared_open_key,
                    palette_nicename="Danger",
                    palette_attribute_name="danger_palette",
                    round_bottom=True,
                ),
                # Corner radii
                rio.Text(
                    "Corner Radii",
                    style="heading2",
                    margin_top=1,
                    margin_bottom=1,
                    align_x=0,
                ),
                radius_sliders,
                # Theme Variants
                rio.Text(
                    "Theme Variants",
                    style="heading2",
                    margin_top=1,
                    margin_bottom=1,
                    align_x=0,
                ),
                rio.Row(
                    rio.Spacer(),
                    rio.IconButton(
                        "light-mode",
                        style="minor",
                    ),
                    rio.Spacer(),
                    rio.IconButton(
                        "dark-mode",
                        style="plain",
                    ),
                    rio.Spacer(),
                ),
                margin=1,
                align_y=0,
            ),
            height="grow",
        )
