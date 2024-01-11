from typing import *  # type: ignore

import rio


class PalettePicker(rio.Component):
    shared_open_key: str

    palette_nicename: str
    palette_attribute_name: str

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

    def build(self) -> rio.Component:
        palette = self.palette

        return rio.Column(
            rio.Text(
                self.palette_nicename,
                style="heading3",
                align_x=0,
            ),
            rio.ColorPicker(
                color=palette.background,
                on_change=self._on_color_change,
            ),
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
                            fill=palette.foreground,
                        ),
                        align_x=0,
                    ),
                    spacing=0.8,
                    margin=0.8,
                ),
                style=rio.BoxStyle(
                    fill=palette.background,
                ),
                transition_time=0.15,
            ),
            spacing=1,
            margin=1,
            align_y=0,
        )


class ThemePickerPage(rio.Component):
    shared_open_key: str = ""

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text(
                "Them Picker",
                style="heading2",
                margin=1,
                align_x=0,
            ),
            rio.ScrollContainer(
                child=rio.Column(
                    PalettePicker(
                        shared_open_key=ThemePickerPage.shared_open_key,
                        palette_nicename="Primary",
                        palette_attribute_name="primary_palette",
                    ),
                    PalettePicker(
                        shared_open_key=ThemePickerPage.shared_open_key,
                        palette_nicename="Secondary",
                        palette_attribute_name="secondary_palette",
                    ),
                    PalettePicker(
                        shared_open_key=ThemePickerPage.shared_open_key,
                        palette_nicename="Background",
                        palette_attribute_name="background_palette",
                    ),
                    PalettePicker(
                        shared_open_key=ThemePickerPage.shared_open_key,
                        palette_nicename="Neutral",
                        palette_attribute_name="neutral_palette",
                    ),
                    PalettePicker(
                        shared_open_key=ThemePickerPage.shared_open_key,
                        palette_nicename="Success",
                        palette_attribute_name="success_palette",
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
                    ),
                    spacing=1,
                    margin=1,
                    align_y=0,
                ),
                height="grow",
            ),
        )
