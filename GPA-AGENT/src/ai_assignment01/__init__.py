"""PUCIT GPA assistant package."""

import asyncio


def main() -> None:
    from .agent import main as async_main

    asyncio.run(async_main())
