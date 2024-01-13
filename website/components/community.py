import rio

from .. import theme


class SocialButton(rio.Component):
    icon: str
    title: str
    text: str
    url: str

    def build(self) -> rio.Component:
        return rio.Card(
            rio.Link(
                rio.Row(
                    rio.Icon(
                        self.icon,
                        width=2.5,
                        height=2.5,
                    ),
                    rio.Column(
                        rio.Text(
                            self.title,
                            style=rio.TextStyle(
                                font_size=theme.ACTION_TEXT_HEIGHT,
                                font_weight="bold",
                            ),
                            align_x=0,
                        ),
                        rio.Text(
                            self.text,
                            align_x=0,
                        ),
                        spacing=0.5,
                        width="grow",
                        align_x=0,
                    ),
                    spacing=1,
                    margin=1,
                ),
                target_url=self.url,
                open_in_new_tab=True,
                margin_x=0.5,
            ),
            corner_radius=99999,
            elevate_on_hover=True,
            colorize_on_hover=True,
        )


class Community(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text(
                "Join the Rio Community",
                style=rio.TextStyle(
                    font_size=theme.TITLE_HEIGHT,
                    font_weight="bold",
                ),
            ),
            SocialButton(
                icon="thirdparty/discord-logo",
                title="Join our Discord",
                text="Talk to fellow Rio users, the Rio developer team, or get help.",
                url="https://discord.com/todo",
            ),
            SocialButton(
                icon="thirdparty/github-logo",
                title="View the Source",
                text="See our github repository.",
                url="https://github.com/rio-project/rio",
            ),
            spacing=2,
        )
