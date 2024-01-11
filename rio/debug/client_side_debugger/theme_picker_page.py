import functools
from typing import *  # type: ignore

import rio


async def update_and_apply_theme(
    session: rio.Session,
    theme_replacements: Dict[str, Any],
) -> None:
    """
    Overrides the session's theme with the given one, and makes sure to update
    all components so they use the new theme.
    """

    # Build the new theme
    new_theme = session.theme.replace(**theme_replacements)

    # The theme theme itself can preserve some values. For example, the primary
    # color is encoded in the heading text style, so just replacing the primary
    # palette won't make it go away.
    #
    # Take care of that.
    recreated_theme = rio.Theme.from_color(
        new_theme.primary_color,
        light=new_theme.background_color.perceived_brightness > 0.5,
    )

    new_theme = new_theme.replace(
        heading1_style=recreated_theme.heading1_style,
        heading2_style=recreated_theme.heading2_style,
        heading3_style=recreated_theme.heading3_style,
    )

    # Apply the theme
    await session._apply_theme(new_theme)

    # The application itself isn't enough, because some components will have
    # read theme values and used them to set e.g. their corner radii. Dirty
    # every component to force a full rebuild.
    for component in session._weak_components_by_id.values():
        session._register_dirty_component(
            component,
            include_children_recursively=False,
        )

    # Refresh
    await session._refresh()


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
        await update_and_apply_theme(
            self.session,
            {self.palette_attribute_name: rio.Palette.from_color(event.color, True)},
        )

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
                    style="heading3",
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

    theme_variants_are_initialized: bool = False
    create_light_theme: bool = True
    create_dark_theme: bool = False

    @rio.event.on_populate
    async def _on_populate(self) -> None:
        if self.theme_variants_are_initialized:
            return

        current_theme_is_light = (
            self.session.theme.background_color.perceived_brightness > 0.5
        )

        self.create_light_theme = current_theme_is_light
        self.create_dark_theme = not current_theme_is_light

    async def _on_radius_change(
        self,
        radius_name: str,
        event: rio.SliderChangeEvent,
    ) -> None:
        await update_and_apply_theme(
            self.session,
            {
                radius_name: event.value,
            },
        )

    def _toggle_create_light_theme(self) -> None:
        self.create_light_theme = not self.create_light_theme

        if not self.create_light_theme and not self.create_dark_theme:
            self.create_dark_theme = True

    def _toggle_create_dark_theme(self) -> None:
        self.create_dark_theme = not self.create_dark_theme

        if not self.create_light_theme and not self.create_dark_theme:
            self.create_light_theme = True

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
                # rio.Text(
                #     "Theme Colors",
                #     style="heading3",
                #     margin_bottom=1,
                #     align_x=0,
                # ),
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
                    style="heading3",
                    margin_top=1,
                    margin_bottom=1,
                    align_x=0,
                ),
                radius_sliders,
                # Theme Variants
                rio.Text(
                    "Theme Variants",
                    style="heading3",
                    margin_top=1,
                    margin_bottom=1,
                    align_x=0,
                ),
                rio.Row(
                    rio.Spacer(),
                    rio.IconButton(
                        "light-mode",
                        style="minor" if self.create_light_theme else "plain",
                        on_press=self._toggle_create_light_theme,
                    ),
                    rio.Spacer(),
                    rio.IconButton(
                        "dark-mode",
                        style="minor" if self.create_dark_theme else "plain",
                        on_press=self._toggle_create_dark_theme,
                    ),
                    rio.Spacer(),
                ),
                # Code Sample
                rio.Text(
                    "Code Sample",
                    style="heading3",
                    margin_top=1,
                    # margin_bottom=1,  Not used for now, since markdown has an oddly large margin anyway
                    align_x=0,
                ),
                rio.MarkdownView(
                    f"""
```python
Super cool, most definitely working
Code sample
```
                    """,
                ),
                margin=1,
                align_y=0,
            ),
            height="grow",
        )
