import asyncio
import concurrent.futures

import lazyopenai


async def generate(*args, **kwargs):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, lazyopenai.generate, *args, **kwargs)
        return result
