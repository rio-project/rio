from typing import Dict

import rio


class Picture(rio.Component):
    def build(self) -> rio.Component:
        return rio.Image(
            rio.URL("https://avatars.githubusercontent.com/u/25320293?v=4"),
            corner_radius=99999,
            fill_mode="zoom",
        )


class SkillBars(rio.Component):
    skills: Dict[str, int]

    def build(self) -> rio.Component:
        rows = []

        for name, level in self.skills.items():
            rows.append(
                rio.Column(
                    rio.Text(
                        name,
                        align_x=0,
                    ),
                    rio.ProgressBar(
                        level / 10,
                    ),
                )
            )

        return rio.Column(
            *rows,
            spacing=0.5,
        )


class PortfolioView(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Row(
                Picture(
                    width=10,
                    height=10,
                    align_y=0,
                ),
                rio.Card(
                    SkillBars(
                        {
                            "Python": 10,
                            "C++": 8,
                            "Rust": 7,
                            "JavaScript": 6,
                            "TypeScript": 6,
                        },
                        width=25,
                    )
                ),
                spacing=5,
            ),
            align_x=0.5,
            align_y=0.2,
        )
