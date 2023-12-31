import rio

from .. import theme

STYLE_A = rio.BoxStyle(
    fill=rio.Color.from_hex("b70074"),
    corner_radius=1,
)

STYLE_B = STYLE_A.replace(
    fill=rio.Color.from_hex("508eff"),
)

STYLE_C = STYLE_A.replace(
    fill=rio.Color.from_hex("00bf63"),
)


def _make_sample_rectangle(
    text: str,
    width: float,
    height: float,
    style: rio.BoxStyle,
) -> rio.Component:
    assert isinstance(style.fill, rio.SolidFill), style.fill

    return rio.Rectangle(
        child=rio.Text(
            text,
            style=rio.TextStyle(
                fill=theme.THEME.text_color_for(
                    style.fill.color,
                ),
                font_weight="bold",
            ),
        ),
        style=style,
        width=width,
        height=height,
    )


class SampleA(rio.Component):
    def build(self) -> rio.Component:
        return _make_sample_rectangle(
            "A",
            3.0,
            3.0,
            STYLE_A,
        )


class SampleB(rio.Component):
    def build(self) -> rio.Component:
        return _make_sample_rectangle(
            "B",
            5.0,
            8.0,
            STYLE_B,
        )


class SampleC(rio.Component):
    def build(self) -> rio.Component:
        return _make_sample_rectangle(
            "C",
            10.0,
            10.0,
            STYLE_C,
        )
