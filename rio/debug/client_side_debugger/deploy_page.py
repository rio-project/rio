import rio

from ...components import component_tree
from . import component_details


class DeployPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text(
                "Deploy",
                style="heading2",
                margin=1,
                align_x=0,
            ),
            rio.Column(
                rio.Icon(
                    "rocket-launch",
                    width=6,
                    height=6,
                    margin_bottom=3,
                    fill=self.session.theme.secondary_color,
                ),
                rio.Text("One-click deployment is coming soon!"),
                rio.Text("Stay tuned for updates."),
                spacing=1,
                height="grow",
                align_y=0.3,
                margin=1,
            ),
        )
