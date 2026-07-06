from __future__ import annotations
import asyncio
from astergard.server.game import GameServer

if __name__ == "__main__":
    asyncio.run(GameServer().start())
