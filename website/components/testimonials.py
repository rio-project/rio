import reflex as rx

from .. import theme


class Testimonial(rx.Widget):
    text: str
    icon: str
    company_name: str
    # company_logo: str  # TODO
    # image: str  # TODO

    def build(self) -> rx.Widget:
        return rx.Card(
            rx.Row(
                rx.Icon(
                    self.icon,
                    width=5.0,
                    height=5.0,
                    margin=3,
                ),
                rx.Column(
                    rx.Text(
                        self.text,
                        style=rx.TextStyle(
                            font_size=1.2,
                            font_weight="bold",
                        ),
                    ),
                    rx.Text(
                        f"— {self.company_name}",
                        style=rx.TextStyle(
                            font_size=1.0,
                            font_weight="bold",
                            font_color=theme.THEME.text_color_for(
                                theme.THEME.surface_color
                            ),
                        ),
                    ),
                    width="grow",
                    spacing=0.5,
                    align_x=0.0,
                    align_y=0.5,
                ),
            ),
            corner_radius=theme.LARGE_CORNER_RADIUS,
            width=30,
            height=12,
        )


class Testimonials(rx.Widget):
    def build(self) -> rx.Widget:
        grid = rx.Grid(
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
