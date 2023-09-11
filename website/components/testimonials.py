import reflex as rx

from .. import theme


class Testimonial(rx.Widget):
    text: str
    company_name: str
    # company_logo: str  # TODO
    # image: str  # TODO

    def build(self) -> rx.Widget:
        return rx.Card(
            rx.Column(
                rx.Text(
                    self.text,
                    style=rx.TextStyle(
                        font_size=1.2,
                        font_weight="bold",
                    ),
                ),
                rx.Text(
                    f"- {self.company_name}",
                    style=rx.TextStyle(
                        font_size=1.0,
                        font_weight="bold",
                        font_color=theme.THEME.text_color_for(
                            theme.THEME.surface_color
                        ),
                    ),
                ),
                spacing=0.5,
                align_y=0.5,
                align_x=0.5,
            ),
            width=30,
            height=12,
        )


class Testimonials(rx.Widget):
    def build(self) -> rx.Widget:
        grid = rx.Grid(
            row_spacing=4,
            column_spacing=9,
            margin=3,
            align_x=0.5,
        )

        grid.add_child(
            Testimonial(
                "So cool!",
                "Company 1",
            ),
            row=0,
            column=0,
        )

        grid.add_child(
            Testimonial(
                "Total lifesaver!",
                "Company 2",
            ),
            row=0,
            column=1,
        )

        return grid
