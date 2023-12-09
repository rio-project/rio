import asyncio
from pathlib import Path

import watchfiles


async def main() -> None:
    watch_path = Path.home() / "Local" / "rio"
    async for changes in watchfiles.awatch(watch_path):
        print(changes)


if __name__ == "__main__":
    asyncio.run(main())
