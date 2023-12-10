from __future__ import annotations

from typing import *  # type: ignore

from .component_base import Component, FundamentalComponent


# The HighLevelRootComponent is the top-most element. It's a high-level element
# that is never re-built, which is convenient in many ways:
# 1. Every component except for the root component itself has a valid builder
# 2. The JS code is simpler because the root component can't have an
#    alignment or margin
# 3. Children of non-fundamental components are automatically initialized
#    correctly, so we don't need to duplicate that logic here
class HighLevelRootComponent(Component):
    build_function: Callable[[], Component]
    build_connection_lost_message_function: Callable[[], Component]

    def build(self) -> Component:
        return FundamentalRootComponent(
            self.build_function(),
            self.build_connection_lost_message_function(),
        )


class FundamentalRootComponent(FundamentalComponent):
    child: Component
    connection_lost_component: Component


FundamentalRootComponent._unique_id = "FundamentalRootComponent-builtin"
