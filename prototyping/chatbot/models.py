from dataclasses import dataclass
from datetime import datetime
from typing import *  # type: ignore


@dataclass
class ChatMessage:
    timestamp: datetime
    is_user_message: bool
    text: str

    is_upvoted: bool
    is_downvoted: bool
    is_flagged_as_outdated: bool
