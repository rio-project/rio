from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

import rio

from .. import models


class FeedbackButton(rio.Component):
    icon: str
    label: str
    is_active: bool
    color: rio.ColorSet
    _: KW_ONLY
    on_press: rio.EventHandler[[]] = None

    def build(self) -> rio.Component:
        return rio.Tooltip(
            anchor=rio.IconButton(
                self.icon,
                style="major" if self.is_active else "plain",
                # color="keep" if self.is_active else self.color,
                color=self.color,
                size=1.6,
                on_press=self.on_press,
            ),
            tip=self.label,
            position="bottom",
        )


class ChatMessage(rio.Component):
    message: models.ChatMessage

    async def _on_upvote(self) -> None:
        self.message.is_upvoted = not self.message.is_upvoted

        if self.message.is_upvoted:
            self.message.is_downvoted = False

        await self.force_refresh()

    async def _on_downvote(self) -> None:
        self.message.is_downvoted = not self.message.is_downvoted

        if self.message.is_downvoted:
            self.message.is_upvoted = False

        await self.force_refresh()

    async def _on_flag_as_outdated(self) -> None:
        self.message.is_flagged_as_outdated = not self.message.is_flagged_as_outdated
        await self.force_refresh()

    def build(self) -> rio.Component:
        if self.message.is_user_message:
            feedback_area = rio.Spacer(height=0)
        else:
            feedback_area = rio.Row(
                FeedbackButton(
                    "thumb-up",
                    "Like",
                    self.message.is_upvoted,
                    "success",
                    on_press=self._on_upvote,
                ),
                FeedbackButton(
                    "thumb-down",
                    "Dislike",
                    self.message.is_downvoted,
                    "danger",
                    on_press=self._on_downvote,
                ),
                FeedbackButton(
                    "nest-clock-farsight-analog",
                    "Flag as outdated",
                    self.message.is_flagged_as_outdated,
                    "warning",
                    on_press=self._on_flag_as_outdated,
                ),
                spacing=0.5,
                margin_top=0.5,
                margin_right=self.session.theme.corner_radius_medium,
                align_x=1,
            )

        return rio.Column(
            rio.Card(
                rio.Column(
                    rio.Row(
                        rio.Icon(
                            "emoji-people"
                            if self.message.is_user_message
                            else "robot-2",
                            fill="secondary",
                        ),
                        rio.Text(
                            "Stoopid Hooman"
                            if self.message.is_user_message
                            else "Super Duper Bot",
                            style=rio.TextStyle(
                                fill=self.session.theme.secondary_color,
                            ),
                        ),
                        rio.Spacer(),
                        rio.Text(
                            self.message.timestamp.astimezone().strftime("%H:%M"),
                            style="dim",
                        ),
                        spacing=0.6,
                    ),
                    rio.MarkdownView(self.message.text),
                    margin=2,
                ),
            ),
            feedback_area,
            margin_left=10 if self.message.is_user_message else 0,
            margin_right=0 if self.message.is_user_message else 10,
        )
