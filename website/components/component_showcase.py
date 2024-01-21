import rio

from .. import theme


class ComponentSample(rio.Component):
    component: rio.Component
    code: str

    def build(self) -> rio.Component:
        return rio.Card(
            rio.Column(
                rio.Container(
                    self.component,
                    height="grow",
                    align_y=0.5,
                ),
                rio.MarkdownView(
                    f"""
`{rio.escape_markdown_code(self.code)}`
""",
                ),
                spacing=1,
                margin=1.5,
            ),
            color="background",
        )


class ComponentShowcase(rio.Component):
    def make_slide(self, icon: str, color: rio.Color) -> rio.Component:
        return rio.Rectangle(
            child=rio.Icon(
                icon,
                fill=self.session.theme.text_color_for(color),
                width=2,
                height=2,
            ),
            style=rio.BoxStyle(
                fill=color,
            ),
        )

    def build(self) -> rio.Component:
        result_grid = rio.Grid(
            row_spacing=4,
            column_spacing=4,
            height="grow",
            align_x=0.5,
            align_y=0.5,
        )

        samples = [
            ComponentSample(
                rio.Button("Castle", icon="castle"),
                "rio.Button('Castle', icon='castle')",
            ),
            ComponentSample(
                rio.Switch(),
                "rio.Switch()",
            ),
            ComponentSample(
                rio.SwitcherBar(
                    ["home", "design", "build"],
                    # icons=["home", "palette", "build"],
                    # orientation="vertical",
                ),
                "rio.SwitcherBar(['home', 'design', 'build'])",
            ),
            ComponentSample(
                rio.Slider(value=1, width=10),
                "rio.Slider()",
            ),
            ComponentSample(
                rio.ColorPicker(self.session.theme.secondary_color),
                "rio.ColorPicker(rio.Color.ORANGE)",
            ),
            ComponentSample(
                rio.Dropdown(["Home", "Design", "Build"], label="Dropdown"),
                "rio.Dropdown(['home', 'design', 'build'], label='Dropdown')",
            ),
            ComponentSample(
                rio.ListView(
                    rio.HeadingListItem("Heading"),
                    rio.SimpleListItem("Item 1"),
                    rio.SimpleListItem("Item 2"),
                ),
                'rio.ListView((rio.SimpleListItem("Item 1"), rio.SimpleListItem("Item 2"))',
            ),
            ComponentSample(
                rio.TextInput(label="Text"),
                "rio.TextInput(label='Text')",
            ),
            ComponentSample(
                rio.Text("TODO: Plot"),
                "rio.Plot(...)",
            ),
            ComponentSample(
                rio.ProgressCircle(),
                "rio.ProgressCircle()",
            ),
            ComponentSample(
                rio.ProgressBar(),
                "rio.ProgressBar()",
            ),
            ComponentSample(
                rio.Slideshow(
                    self.make_slide(
                        "home",
                        rio.Color.from_hex("b70074"),
                    ),
                    self.make_slide(
                        "palette",
                        rio.Color.from_hex("508eff"),
                    ),
                    self.make_slide(
                        "build",
                        rio.Color.from_hex("00bf63"),
                    ),
                    linger_time=1,
                    height=5,
                ),
                "rio.Slideshow(...)",
            ),
            # ComponentSample(
            #     rio.Table(
            #         {
            #             "Column 1": [1, 2, 3],
            #             "Column 2": [4, 5, 6],
            #         }
            #     ),
            #     "rio.Table(pandas.DataFrame(...))",
            # ),
        ]

        for ii, sample in enumerate(samples):
            result_grid.add_child(
                sample,
                ii // 4,
                ii % 4,
            )

        return rio.Column(
            rio.Text(
                "Batteries Included:\n50+ Material Design Components",
                style=theme.ACTION_TITLE_STYLE,
                multiline=True,
                width=30,
                align_x=0.5,
            ),
            result_grid,
            spacing=3,
            height=theme.get_subpage_height(self.session),
            margin_y=3,
        )
