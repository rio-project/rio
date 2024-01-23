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
            color="background",
            corner_radius=99999,
            elevate_on_hover=True,
            colorize_on_hover=True,
        )


class Community(rio.Component):
    def build(self) -> rio.Component:
        return rio.Stack(
            rio.Icon(
                "self/accent-shape-corner-bottom-right",
                fill=theme.THEME_COLORS_GRADIENT_90,
                width=25,
                height=30,
                align_x=1,
                align_y=1,
            ),
            rio.Icon(
                "styling/rounded-corner-bottom-right",
                fill=self.session.theme.hud_color,
                width=4,
                height=4,
                align_x=1,
                align_y=1,
            ),
            rio.Icon(
                "styling/rounded-corner-bottom-left",
                fill=self.session.theme.hud_color,
                width=4,
                height=4,
                align_x=0,
                align_y=1,
            ),
            rio.Column(
                rio.Text(
                    "Join the Rio Community",
                    style=theme.ACTION_TITLE_STYLE,
                    margin_top=5,
                ),
                rio.Column(
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
                    height="grow",
                    align_x=0.2,
                    align_y=0.4,
                ),
            ),
            height=theme.get_subpage_height(self.session),
        )