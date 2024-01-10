import rio

from ...components import component_tree
from . import component_details


class AIChatPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text(
                "AI Chat",
                style="heading2",
                margin=1,
                align_x=0,
            ),
            rio.Column(
                rio.Icon(
                    "chat-bubble",
                    width=6,
                    height=6,
                    margin_bottom=3,
                    fill=self.session.theme.secondary_color,
                ),
                rio.Text("The Rio AI Chat is coming soon!"),
                rio.Text("Join our Discord server for updates"),
                spacing=1,
                height="grow",
                align_y=0.3,
                margin=1,
            ),
            width=35,
        )
