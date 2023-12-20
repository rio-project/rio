from __future__ import annotations

from typing import *  # type: ignore

import rio
import rio.debug

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
        # Spawn a debugger if running in debug mode
        if self.session._app_server.debug_mode:
            # Avoid a circular import
            import rio.debug.client_side_debugger

            debugger = rio.debug.client_side_debugger.ClientSideDebugger()
        else:
            debugger = None

        return FundamentalRootComponent(
            self.build_function(),
            self.build_connection_lost_message_function(),
            debugger=debugger,
        )


class FundamentalRootComponent(FundamentalComponent):
    child: Component
    connection_lost_component: Component
    debugger: Optional[Component]


FundamentalRootComponent._unique_id = "FundamentalRootComponent-builtin"
