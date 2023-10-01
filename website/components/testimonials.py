import rio

from .. import theme


class Testimonial(rio.Widget):
    text: str
    icon: str
    company_name: str
    # company_logo: str  # TODO
    # image: str  # TODO

    def build(self) -> rio.Widget:
        return rio.Card(
            rio.Row(
                rio.Icon(
                    self.icon,
                    width=5.0,
                    height=5.0,
                    margin=3,
                ),
                rio.Column(
                    rio.Text(
                        self.text,
                        style=rio.TextStyle(
                            font_size=1.2,
                            font_weight="bold",
                        ),
                    ),
                    rio.Text(
                        f"— {self.company_name}",
                        style=rio.TextStyle(
                            font_size=1.0,
                            font_weight="bold",
                            fill=theme.THEME.text_color_for(theme.THEME.surface_color),
                        ),
                    ),
                    width="grow",
                    spacing=0.5,
                    align_x=0.0,
                    align_y=0.5,
                ),
            ),
            corner_radius=theme.THEME.corner_radius_large,
            elevate_on_hover=0.6,
            width=30,
            height=12,
        )


class Testimonials(rio.Widget):
    def build(self) -> rio.Widget:
        grid = rio.Grid(
            width=theme.CENTER_COLUMN_WIDTH,
            row_spacing=4,
            column_spacing=9,
            align_x=0.5,
        )

        grid.add_child(
            Testimonial(
                "So cool!",
                "material/nutrition",
                "Company 1",
            ),
            row=0,
            column=0,
        )

        grid.add_child(
            Testimonial(
                "Total lifesaver!",
                "material/bolt",
                "Company 2",
            ),
            row=0,
            column=1,
        )

        return grid
