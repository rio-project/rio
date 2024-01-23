from dataclasses import dataclass
from typing import *  # type: ignore

import rio
from rio.components import Component


class Outliner(rio.Component):
    def build(self) -> rio.Component:
        history_entries = [
            "Placeholder 1",
            "Placeholder 2",
            "Placeholder 3",
        ]

        children = []

        for entry in history_entries:
            children.append(
                rio.Button(
                    content=entry,
                    style="plain",
                )
            )

        return rio.Column(
            rio.Text(
                "Conversations",
                style="heading3",
                margin_bottom=1,
            ),
            *children,
            rio.Button(
                icon="add",
                content="New Conversation",
                color="primary",
                style="plain",
                # margin_top=1.5,
            ),
            # rio.IconButton(
            #     "add",
            #     color="primary",
            #     style="minor",
            #     size=2.5,
            #     margin_top=1.5,
            # ),
            spacing=0.5,
        )
