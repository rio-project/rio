import asyncio
from dataclasses import field
from datetime import datetime, timezone
from typing import *  # type: ignore

import rio

from .. import components as comps
from .. import models


class ChatPage(rio.Component):
    is_loading: bool = False
    question_text: str = ""

    messages: List[models.ChatMessage] = field(
        default_factory=lambda: [
            models.ChatMessage(
                timestamp=datetime.now(timezone.utc),
                is_user_message=False,
                text="Hello, I'm a bot!",
                is_upvoted=False,
                is_downvoted=True,
                is_flagged_as_outdated=True,
            ),
            models.ChatMessage(
                timestamp=datetime.now(timezone.utc),
                is_user_message=True,
                text="Hello, I'm human!",
                is_upvoted=False,
                is_downvoted=False,
                is_flagged_as_outdated=False,
            ),
            models.ChatMessage(
                timestamp=datetime.now(timezone.utc),
                is_user_message=False,
                text="Exterminate!",
                is_upvoted=True,
                is_downvoted=False,
                is_flagged_as_outdated=False,
            ),
        ]
    )

    async def _on_user_message(self, _=None) -> None:
        # Add the user message
        self.messages.append(
            models.ChatMessage(
                timestamp=datetime.now(timezone.utc),
                is_user_message=True,
                text=self.question_text,
                is_upvoted=False,
                is_downvoted=False,
                is_flagged_as_outdated=False,
            )
        )

        # Clear the input
        self.question_text = ""

        # Pretend the app is responding
        self.is_loading = True
        await self.force_refresh()
        await asyncio.sleep(3)

        self.messages.append(
            models.ChatMessage(
                timestamp=datetime.now(timezone.utc),
                is_user_message=False,
                text="Totally legit, most definitely AI generated, perfect response.",
                is_upvoted=False,
                is_downvoted=False,
                is_flagged_as_outdated=False,
            )
        )

        self.is_loading = False
        await self.force_refresh()

    def build(self) -> rio.Component:
        children = []

        # Chat history
        for message in self.messages:
            children.append(
                comps.ChatMessage(
                    message,
                    margin_bottom=5 if message.is_user_message else 3,
                )
            )

        # WIP Message
        if self.is_loading:
            children.append(comps.ThinkingMessage(margin_bottom=3))

        # Spacer
        children.append(rio.Spacer())

        # User Input
        children.append(
            rio.Row(
                rio.TextInput(
                    label="Type a message...",
                    text=ChatPage.question_text,
                    on_confirm=self._on_user_message,
                    is_sensitive=not self.is_loading,
                    width="grow",
                ),
                rio.IconButton(
                    "play-arrow:fill",
                    color="primary",
                    on_press=self._on_user_message,
                    is_sensitive=not self.is_loading,
                ),
                spacing=1,
                margin_top=2,
            )
        )

        return rio.Row(
            rio.Overlay(
                rio.Card(
                    comps.Outliner(
                        align_y=0,
                    ),
                    margin=1,
                    width=25,
                    align_x=0,
                ),
            ),
            rio.Spacer(
                width=26,
            ),
            rio.Container(
                rio.Column(
                    *children,
                    margin=1,
                ),
                width="grow",
            ),
            spacing=2,
        )
